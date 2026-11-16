# AGENTS.md — COSMOL 2D Flood Studio Thin Connector

This repository provides a zero-dependency MCP `stdio` bridge, portable `SKILL.md` package, and CLI client for **COSMOL Global 2D Flood Studio** (`https://hydro.cosmolsesc.com`).

## Architecture Rules
- **Thin API/MCP Client Only**: All 2D Shallow Water Equations (2D SWE) numerical modelling, CAD drawing generation, and PDF/Excel deliverable compilation execute remotely on `https://hydro.cosmolsesc.com`. Never fabricate hydraulic KPIs or flood depths locally.
- **Zero External Dependencies**: Both `cosmol_hydro_mcp.py` and `scripts/hydro_cloud_cli.py` run cleanly on Python 3.10+ standard library.
- **Automatic Local Download**: Completed simulation runs automatically download `HydroStudio_Deliverables_<job_id>.zip` into the working directory (or `--out-dir` / `COSMOL_OUTPUT_DIR`).

## Endpoints & Configuration
- **Remote MCP Endpoint**: `https://hydro.cosmolsesc.com/mcp`
- **OpenAPI 3.1.0 Spec**: `https://hydro.cosmolsesc.com/openapi-global.json`
- **AI Discovery Index**: `https://hydro.cosmolsesc.com/llms.txt`
- **Environment Variables**:
  - `COSMOL_HYDRO_URL`: Override API origin (default `https://hydro.cosmolsesc.com`).
  - `COSMOL_API_TOKEN`: Optional `GLBH-*` Bearer token for paid credit packs (`$29 / $89 / $249 USD`).
  - `COSMOL_OUTPUT_DIR`: Optional local directory for downloaded deliverable ZIP archives.

## Agent Behaviour Guidelines
1. Always inspect quota first (`get_quota_and_pricing` or `python3 scripts/hydro_cloud_cli.py quota`) if uncertain about remaining free runs (2 free full-resolution runs per anonymous client).
2. Prefer passing local terrain/CAD files (`.dxf`, `.tif`, `.asc`, `.las`, `.geojson`, `.csv`, `.zip`) through `upload_local_terrain` or `--file`; never paste large binary files into chat context.
3. On HTTP `402` (`PAYMENT_REQUIRED`), share the returned Stripe Checkout URL cleanly with the user without retrying in a loop.
