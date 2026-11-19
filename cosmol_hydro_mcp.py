#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Zero-Dependency Python 3.10+ MCP stdio Bridge for COSMOL HydroGeo Studio."""
from __future__ import annotations

import base64, json, os, sys, urllib.error, urllib.parse, urllib.request, uuid
from pathlib import Path
from typing import Any

BASE_URL = (os.environ.get("COSMOL_HYDRO_URL") or "https://hydro.cosmolsesc.com").strip().rstrip("/")
API_TOKEN = (os.environ.get("COSMOL_API_TOKEN") or "").strip()
OUT_ROOT = Path(os.environ.get("COSMOL_OUTPUT_DIR") or ".").expanduser()
GUEST_FILE = Path.home() / ".cosmol_hydro_guest_token"
PROTOCOLS = ("2025-06-18", "2025-03-26", "2024-11-05")
_MOD_TOOLS = {
    "run_m00_globalgeo_crs_mesh": "m00", "run_2d_flood_simulation": "m01",
    "run_m02_coupled_swe_modflow6": "m02", "run_m03_sediment_morpho_sesc": "m03",
    "run_m04_urban_stormwater_lid_sewer": "m04",
}

def _t(name: str, desc: str, props: dict[str, Any], req: list[str] | None = None) -> dict[str, Any]:
    s: dict[str, Any] = {"type": "object", "properties": props}
    return {"name": name, "description": desc, "inputSchema": {**s, "required": req} if req else s}

_RUN_COMMON = {"upload_id": {"type": "string"}, "local_file_path": {"type": "string"}, "site_name": {"type": "string"}, "white_label_company": {"type": "string"}, "output_dir": {"type": "string"}}
TOOLS: list[dict[str, Any]] = [
    _t("get_quota_and_pricing", "Check credits (2 free + 3 w/ email = 5), 5 modules & USD plans ($39/$99/$299 + $79/$249 subs).", {}),
    _t("claim_email_bonus_credits", "Unlock +3 bonus free credits (2 -> 5) via work email or GitHub handle.", {"email": {"type": "string"}, "contact": {"type": "string"}}),
    _t("upload_terrain_base64", "Upload terrain/CAD/GIS (.dxf/.tif/.asc/.las/.geojson/.zip) as base64, text or local_file_path.", {"filename": {"type": "string"}, "content_base64": {"type": "string"}, "content_text": {"type": "string"}, "local_file_path": {"type": "string"}, "upload_id": {"type": "string"}}),
    _t("run_m00_globalgeo_crs_mesh", "M00: Auto-UTM CRS detection, D8 catchment & adaptive mesh.", {**_RUN_COMMON, "lon": {"type": "number"}, "lat": {"type": "number"}, "place": {"type": "string"}}),
    _t("run_2d_flood_simulation", "M01: 2D Full-Momentum SWE flood, structures & Design Rev 5 earthworks.", {**_RUN_COMMON, "case_id": {"type": "string"}, "return_period": {"type": "integer", "default": 100}, "storm_pattern": {"type": "string", "default": "chicago"}, "duration_min": {"type": "integer", "default": 180}, "rainfall_mm": {"type": "number", "default": 144.0}, "inflow_m3s": {"type": "number", "default": 0.0}, "has_dam": {"type": "boolean", "default": False}}),
    _t("run_m02_coupled_swe_modflow6", "M02: Coupled 2D SWE + 3D MODFLOW 6 DISV+XT3D seepage & piping.", {**_RUN_COMMON, "scenario": {"type": "string", "default": "levee_piping"}, "return_period": {"type": "integer", "default": 100}, "cutoff_depth_m": {"type": "number", "default": 18.0}}),
    _t("run_m03_sediment_morpho_sesc", "M03: 2D Grid-RUSLE erosion, Wu (2007) sediment & PACl+PAM HESB SESC.", {**_RUN_COMMON, "scenario": {"type": "string", "default": "coomera_sesc_hesb"}, "return_period": {"type": "integer", "default": 50}, "rainfall_mm": {"type": "number", "default": 178.0}, "duration_min": {"type": "integer", "default": 180}, "no_dosing": {"type": "boolean", "default": False}}),
    _t("run_m04_urban_stormwater_lid_sewer", "M04: Preissmann 1D sewer + 2D urban SWE, LID/SuDS/WSUD & AIDR H1-H6.", {**_RUN_COMMON, "scenario": {"type": "string", "default": "oxenford_coomera_wsud"}, "return_period": {"type": "integer", "default": 50}, "rainfall_mm": {"type": "number", "default": 178.0}, "duration_min": {"type": "integer", "default": 180}, "no_lid": {"type": "boolean", "default": False}}),
    _t("get_simulation_deliverables", "Fetch KPIs and download HydroStudio_Deliverables_<job_id>.zip locally.", {"job_id": {"type": "string"}, "output_dir": {"type": "string"}, "download": {"type": "boolean", "default": True}}, ["job_id"]),
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
    h = {"User-Agent": "cosmol-hydrogeo-mcp/2.0.0", "X-Guest-Token": _guest_token()}
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
    if name == "claim_email_bonus_credits":
        st, data = _http("/api/global/billing/claim_email_bonus", "POST", json.dumps(args).encode("utf-8"), "application/json")
        if st >= 400:
            raise RuntimeError(data.get("error") or f"Claim failed ({st})")
        return data, json.dumps(data, indent=2)
    if name in ("upload_terrain_base64", "upload_local_terrain"):
        if args.get("local_file_path") or args.get("file_path"):
            data = _upload_file(str(args.get("local_file_path") or args.get("file_path")), str(args.get("upload_id") or ""))
            return data, json.dumps(data, indent=2)
        fn = str(args.get("filename") or "terrain.asc").strip()
        raw = base64.b64decode(str(args["content_base64"])) if args.get("content_base64") else str(args.get("content_text") or "").encode("utf-8")
        q = urllib.parse.urlencode({"filename": fn, **({"upload_id": args["upload_id"]} if args.get("upload_id") else {})})
        st, data = _http(f"/api/global/upload?{q}", "POST", raw, "application/octet-stream")
        if st >= 400:
            raise RuntimeError(data.get("error") or f"Upload failed ({st})")
        return data, json.dumps(data, indent=2)
    if name in _MOD_TOOLS:
        up_id = str(args.get("upload_id") or "").strip()
        if args.get("local_file_path") and not up_id:
            up_id = str(_upload_file(str(args["local_file_path"]))["upload_id"])
        payload = {k: v for k, v in args.items() if k not in {"local_file_path", "output_dir"}}
        if name != "run_2d_flood_simulation" or "module_id" in args:
            payload.setdefault("module_id", _MOD_TOOLS[name])
        if up_id:
            payload["upload_id"] = up_id
        st, data = _http("/api/global/run", "POST", json.dumps(payload).encode("utf-8"), "application/json")
        if st == 402:
            return data, f"PAYMENT_REQUIRED: {data.get('message', 'Free credits exhausted.')} Stripe Checkout: {data.get('checkout_url')}"
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
    if any(a in ("-V", "--version") for a in sys.argv[1:]):
        print("cosmol-hydrogeo-mcp 2.0.0")
        return
    if any(a in ("-h", "--help") for a in sys.argv[1:]):
        print("COSMOL HydroGeo Studio MCP stdio server (https://hydro.cosmolsesc.com)")
        return
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
            pv = str(params.get("protocolVersion") or "").strip()
            res: dict[str, Any] = {"protocolVersion": pv if pv in PROTOCOLS else PROTOCOLS[0], "capabilities": {"tools": {"listChanged": False}}, "serverInfo": {"name": "cosmol-hydrogeo-mcp", "version": "2.0.0"}}
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
