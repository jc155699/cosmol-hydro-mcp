#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Zero-Dependency CLI Client for COSMOL HydroGeo Studio (M00-M04)."""
from __future__ import annotations

import argparse, json, os, sys, urllib.error, urllib.parse, urllib.request, uuid
from pathlib import Path
from typing import Any

DEFAULT_URL = (os.environ.get("COSMOL_HYDRO_URL") or "https://hydro.cosmolsesc.com").strip().rstrip("/")
GUEST_FILE = Path.home() / ".cosmol_hydro_guest_token"


def _guest_token() -> str:
    if tok := (os.environ.get("COSMOL_GUEST_TOKEN") or "").strip():
        return tok
    if GUEST_FILE.is_file() and (tok := GUEST_FILE.read_text("utf-8").strip()):
        return tok
    tok = f"cli_{uuid.uuid4().hex[:16]}"
    try:
        GUEST_FILE.write_text(tok, encoding="utf-8")
    except Exception:
        pass
    return tok


def _headers(token: str = "", ctype: str | None = None) -> dict[str, str]:
    h = {"User-Agent": "cosmol-hydrogeo-cli/2.0.0", "X-Guest-Token": _guest_token()}
    if tok := (token or os.environ.get("COSMOL_API_TOKEN") or "").strip():
        h["Authorization"] = f"Bearer {tok}"
    return {**h, "Content-Type": ctype} if ctype else h


def _req(base: str, path: str, method: str = "GET", body: bytes | None = None, ctype: str | None = None, token: str = "") -> tuple[int, dict[str, Any]]:
    req = urllib.request.Request(f"{base.rstrip('/')}{path}", data=body, headers=_headers(token, ctype), method=method)
    try:
        with urllib.request.urlopen(req, timeout=240) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", "ignore")
        try:
            return exc.code, json.loads(raw)
        except Exception:
            return exc.code, {"error": raw or str(exc)}


def _upload(base: str, fp_str: str, up_id: str = "", token: str = "") -> dict[str, Any]:
    fp = Path(fp_str).expanduser().resolve()
    if not fp.is_file():
        raise FileNotFoundError(f"File not found: {fp}")
    q = urllib.parse.urlencode({"filename": fp.name, **({"upload_id": up_id} if up_id else {})})
    st, data = _req(base, f"/api/global/upload?{q}", "POST", fp.read_bytes(), "application/octet-stream", token)
    if st >= 400:
        raise RuntimeError(data.get("error") or f"Upload failed ({st})")
    return data


def _download_bundle(base: str, job: dict[str, Any], out_dir: str, token: str = "") -> str | None:
    jid = str(job.get("job_id") or "")
    if not jid or job.get("status") != "COMPLETED":
        return None
    url = str(job.get("bundle_zip_url") or f"{base.rstrip('/')}/api/global/jobs/{jid}/bundle.zip")
    dest_dir = Path(out_dir).expanduser().resolve()
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / f"HydroStudio_Deliverables_{jid}.zip"
    with urllib.request.urlopen(urllib.request.Request(url, headers=_headers(token)), timeout=120) as resp:
        dest.write_bytes(resp.read())
    return str(dest)


def main() -> int:
    ap = argparse.ArgumentParser(description="COSMOL HydroGeo Studio CLI (M00-M04)")
    ap.add_argument("--url", default=DEFAULT_URL, help="Base API URL (default: https://hydro.cosmolsesc.com)")
    ap.add_argument("--token", default="", help="Optional GLBH-* Bearer token")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("quota", help="Inspect quota (2+3=5 free), modules and USD pricing")
    cb = sub.add_parser("claim-bonus", help="Claim +3 bonus credits with email or GitHub handle")
    cb.add_argument("contact")
    up_p = sub.add_parser("upload", help="Upload DXF/DEM/LiDAR/GeoJSON/ZIP terrain")
    up_p.add_argument("file")
    up_p.add_argument("--upload-id", default="")
    rn_p = sub.add_parser("run", help="Run M00-M04 multi-physics simulation")
    for flg, kw in [("--module", {"default": "m01"}), ("--file", {}), ("--upload-id", {}), ("--case-id", {}), ("--scenario", {}), ("--storm-pattern", {"default": "chicago"}), ("--site-name", {}), ("--white-label", {}), ("--place", {}), ("--out-dir", {"default": "."})]:
        rn_p.add_argument(flg, default=kw.get("default", ""))
    rn_p.add_argument("--return-period", type=int, default=100)
    rn_p.add_argument("--duration-min", type=int, default=180)
    rn_p.add_argument("--rainfall-mm", type=float, default=144.0)
    rn_p.add_argument("--inflow-m3s", type=float, default=0.0)
    rn_p.add_argument("--cutoff-depth", type=float, default=18.0)
    rn_p.add_argument("--lon", type=float, default=None)
    rn_p.add_argument("--lat", type=float, default=None)
    rn_p.add_argument("--has-dam", action="store_true")
    rn_p.add_argument("--no-dosing", action="store_true")
    rn_p.add_argument("--no-lid", action="store_true")
    st_p = sub.add_parser("status", help="Inspect job status and optionally download bundle")
    st_p.add_argument("job_id")
    st_p.add_argument("--download", action="store_true")
    st_p.add_argument("--out-dir", default=".")
    sub.add_parser("redeem", help="Redeem a GLBH-* API token").add_argument("api_token")
    args = ap.parse_args()

    if args.cmd == "quota":
        st, out = _req(args.url, "/api/global/session", "POST", b"{}", "application/json", args.token)
    elif args.cmd == "claim-bonus":
        st, out = _req(args.url, "/api/global/billing/claim_email_bonus", "POST", json.dumps({"email": args.contact, "contact": args.contact}).encode("utf-8"), "application/json", args.token)
    elif args.cmd == "upload":
        st, out = 200, _upload(args.url, args.file, args.upload_id, args.token)
    elif args.cmd == "run":
        up_id = args.upload_id.strip() or (str(_upload(args.url, args.file, "", args.token)["upload_id"]) if args.file else "")
        payload: dict[str, Any] = {
            "module_id": args.module, "case_id": args.case_id, "scenario": args.scenario, "return_period": args.return_period,
            "storm_pattern": args.storm_pattern, "duration_min": args.duration_min, "rainfall_mm": args.rainfall_mm,
            "inflow_m3s": args.inflow_m3s, "cutoff_depth_m": args.cutoff_depth, "has_dam": args.has_dam,
            "no_dosing": args.no_dosing, "no_lid": args.no_lid, "site_name": args.site_name,
            "white_label_company": args.white_label, "place": args.place,
        }
        if args.lon is not None and args.lat is not None:
            payload.update({"lon": args.lon, "lat": args.lat})
        if up_id:
            payload["upload_id"] = up_id
        st, out = _req(args.url, "/api/global/run", "POST", json.dumps(payload).encode("utf-8"), "application/json", args.token)
        if st == 200 and out.get("job") and (saved := _download_bundle(args.url, out["job"], args.out_dir, args.token)):
            out["local_bundle_zip"] = saved
    elif args.cmd == "status":
        st, out = _req(args.url, f"/api/global/jobs/{urllib.parse.quote(args.job_id)}", token=args.token)
        if st == 200 and args.download and out.get("job") and (saved := _download_bundle(args.url, out["job"], args.out_dir, args.token)):
            out["local_bundle_zip"] = saved
    else:
        st, out = _req(args.url, "/api/global/billing/redeem_token", "POST", json.dumps({"api_token": args.api_token}).encode("utf-8"), "application/json", args.token)
    print(json.dumps(out, indent=2))
    return 2 if st == 402 else (0 if st < 400 else 1)


if __name__ == "__main__":
    sys.exit(main())
