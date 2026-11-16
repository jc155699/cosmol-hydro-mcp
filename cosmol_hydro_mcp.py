#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Zero-Dependency Python 3.10+ MCP stdio Bridge for COSMOL 2D Flood Studio."""
from __future__ import annotations

import json, os, sys, urllib.error, urllib.parse, urllib.request, uuid
from pathlib import Path
from typing import Any

BASE_URL = (os.environ.get("COSMOL_HYDRO_URL") or "https://hydro.cosmolsesc.com").strip().rstrip("/")
API_TOKEN = (os.environ.get("COSMOL_API_TOKEN") or "").strip()
OUT_ROOT = Path(os.environ.get("COSMOL_OUTPUT_DIR") or ".").expanduser()
GUEST_FILE = Path.home() / ".cosmol_hydro_guest_token"
TOOLS: list[dict[str, Any]] = [
    {"name": "get_quota_and_pricing", "description": "Check remaining flood simulation credits (2 free full-res runs) and USD plans.", "inputSchema": {"type": "object", "properties": {}}},
    {"name": "upload_local_terrain", "description": "Upload local .dxf, .tif, .asc, .las, .geojson, .csv, or .zip terrain to cloud.", "inputSchema": {"type": "object", "required": ["file_path"], "properties": {"file_path": {"type": "string"}, "upload_id": {"type": "string"}}}},
    {"name": "run_2d_flood_simulation", "description": "Run 2D SWE flood simulation and download HydroStudio_Deliverables_<job_id>.zip locally.", "inputSchema": {"type": "object", "properties": {"upload_id": {"type": "string"}, "local_file_path": {"type": "string"}, "case_id": {"type": "string"}, "return_period": {"type": "integer", "default": 100}, "storm_pattern": {"type": "string", "default": "alternating_block"}, "duration_min": {"type": "integer", "default": 120}, "rainfall_mm": {"type": "number", "default": 180.0}, "inflow_m3s": {"type": "number", "default": 0.0}, "has_dam": {"type": "boolean", "default": False}, "output_dir": {"type": "string"}}}},
    {"name": "get_simulation_deliverables", "description": "Check job status and download HydroStudio_Deliverables_<job_id>.zip into workspace.", "inputSchema": {"type": "object", "required": ["job_id"], "properties": {"job_id": {"type": "string"}, "output_dir": {"type": "string"}, "download": {"type": "boolean", "default": True}}}},
]


def _guest_token() -> str:
    if tok := (os.environ.get("COSMOL_GUEST_TOKEN") or "").strip():
        return tok
    if GUEST_FILE.is_file() and (tok := GUEST_FILE.read_text("utf-8").strip()):
        return tok
    tok = f"mcp_{uuid.uuid4().hex[:16]}"
    try:
        GUEST_FILE.write_text(tok, encoding="utf-8")
    except Exception:
        pass
    return tok


def _headers(ctype: str | None = None) -> dict[str, str]:
    h = {"User-Agent": "cosmol-hydro-mcp/1.0", "X-Guest-Token": _guest_token()}
    if API_TOKEN:
        h["Authorization"] = f"Bearer {API_TOKEN}"
    return {**h, "Content-Type": ctype} if ctype else h


def _http(path: str, method: str = "GET", body: bytes | None = None, ctype: str | None = None) -> tuple[int, dict[str, Any]]:
    req = urllib.request.Request(f"{BASE_URL}{path}", data=body, headers=_headers(ctype), method=method)
    try:
        with urllib.request.urlopen(req, timeout=240) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", "ignore")
        try:
            return exc.code, json.loads(raw)
        except Exception:
            return exc.code, {"error": raw or str(exc)}


def _upload_file(fp_str: str, up_id: str = "") -> dict[str, Any]:
    fp = Path(fp_str).expanduser().resolve()
    if not fp.is_file():
        raise FileNotFoundError(f"Terrain file not found: {fp}")
    q = urllib.parse.urlencode({"filename": fp.name, **({"upload_id": up_id} if up_id else {})})
    st, data = _http(f"/api/global/upload?{q}", "POST", fp.read_bytes(), "application/octet-stream")
    if st >= 400:
        raise RuntimeError(data.get("error") or f"Upload failed ({st})")
    return data


def _download_zip(job: dict[str, Any], out_dir_str: str = "") -> str | None:
    jid = str(job.get("job_id") or "")
    if not jid or job.get("status") != "COMPLETED":
        return None
    url = str(job.get("bundle_zip_url") or (job.get("deliverables") or {}).get("bundle_zip_url") or f"{BASE_URL}/api/global/jobs/{jid}/bundle.zip")
    dest_dir = Path(out_dir_str).expanduser().resolve() if out_dir_str else OUT_ROOT.resolve()
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / f"HydroStudio_Deliverables_{jid}.zip"
    with urllib.request.urlopen(urllib.request.Request(url, headers=_headers()), timeout=120) as resp:
        dest.write_bytes(resp.read())
    return str(dest)


def _call_tool(name: str, args: dict[str, Any]) -> tuple[dict[str, Any], str]:
    if name == "get_quota_and_pricing":
        _, data = _http("/api/global/session", "POST", b"{}", "application/json")
        return data, json.dumps(data, indent=2)
    if name == "upload_local_terrain":
        data = _upload_file(str(args["file_path"]), str(args.get("upload_id") or ""))
        return data, json.dumps(data, indent=2)
    if name == "run_2d_flood_simulation":
        up_id = str(args.get("upload_id") or "").strip()
        if args.get("local_file_path") and not up_id:
            up_id = str(_upload_file(str(args["local_file_path"]))["upload_id"])
        payload = {k: v for k, v in args.items() if k not in {"local_file_path", "output_dir"}}
        if up_id:
            payload["upload_id"] = up_id
        st, data = _http("/api/global/run", "POST", json.dumps(payload).encode("utf-8"), "application/json")
        if st == 402:
            return data, f"PAYMENT_REQUIRED: Free quota exhausted. Top up ($29/$89/$249 USD) via Stripe Checkout: {data.get('checkout_url')}"
        if st >= 400:
            raise RuntimeError(data.get("error") or f"Simulation failed ({st})")
        if saved := _download_zip(data.get("job") or {}, str(args.get("output_dir") or "")):
            data["local_bundle_zip"] = saved
        return data, json.dumps(data, indent=2)
    if name == "get_simulation_deliverables":
        jid = str(args["job_id"]).strip()
        st, data = _http(f"/api/global/jobs/{urllib.parse.quote(jid)}")
        if st >= 400:
            raise RuntimeError(data.get("error") or f"Job lookup failed ({st})")
        if args.get("download", True) and data.get("job") and (saved := _download_zip(data["job"], str(args.get("output_dir") or ""))):
            data["local_bundle_zip"] = saved
        return data, json.dumps(data, indent=2)
    raise ValueError(f"Unknown tool: {name}")


def main() -> None:
    for raw_line in sys.stdin:
        if not (line := raw_line.strip()):
            continue
        try:
            req = json.loads(line)
        except Exception:
            continue
        rid, method, params = req.get("id"), str(req.get("method") or ""), dict(req.get("params") or {})
        if method.startswith("notifications/"):
            continue
        if method == "initialize":
            res: dict[str, Any] = {"protocolVersion": "2024-11-05", "capabilities": {"tools": {"listChanged": False}}, "serverInfo": {"name": "cosmol-hydro-mcp", "version": "1.0.0"}}
        elif method == "ping":
            res = {}
        elif method == "tools/list":
            res = {"tools": TOOLS}
        elif method == "tools/call":
            try:
                out, txt = _call_tool(str(params.get("name") or ""), dict(params.get("arguments") or {}))
                res = {"content": [{"type": "text", "text": txt}], "structuredContent": out, "isError": False}
            except Exception as exc:
                res = {"content": [{"type": "text", "text": f"Error: {exc}"}], "isError": True}
        else:
            sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": rid, "error": {"code": -32601, "message": f"Method not found: {method}"}}) + "\n")
            sys.stdout.flush()
            continue
        sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": rid, "result": res}) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
