# AGENTS.md - COSMOL HydroGeo Studio Thin Connector (v2.1.0)

This repository provides a zero-dependency MCP `stdio` bridge (`cosmol_hydro_mcp.py`), portable `SKILL.md` package, `pyproject.toml`, Australian QLD benchmark GeoJSON, and CLI client (`scripts/hydro_cloud_cli.py`) for **COSMOL HydroGeo Studio** (`https://hydro.cosmolsesc.com`).

## Architecture Rules
- **Thin API/MCP Client Only**: All GIS/Auto-UTM (`M00`), 2D SWE (`M01`), 3D MODFLOW 6 seepage (`M02`), 2D sediment morphodynamics (`M03`, `global_sesc_morpho`), urban 1D/2D sewer + LID (`M04`, `global_wsud_1d2d`), 5-Jurisdiction Auto-Adapter (`US/UK/EU/AU/Global`), Koppen-Geiger regional IDF (`rainfall_mm=0`), CAD, GIF, and PDF/Excel deliverable compilation execute remotely on `https://hydro.cosmolsesc.com`. Never fabricate numerical outputs locally.
- **Universal Survey Ingestion**: Supports `EPSG:4326` GeoTIFF auto-UTM warp, Civil 3D `LWPOLYLINE` code-38 DXF contours, `elev_units` (`auto`, `m`, `ft`), `crs_label`, `(lon, lat)`, and `place` across all 5 modules (`M00`-`M04` plus `run_hydrogeo_m00..m04` aliases).
- **Zero External Dependencies**: Both `cosmol_hydro_mcp.py` and `scripts/hydro_cloud_cli.py` run cleanly on Python 3.10+ standard library.
- **Automatic Local Download**: Completed runs download `HydroStudio_Deliverables_<job_id>.zip` into `--out-dir` / `COSMOL_OUTPUT_DIR`.

## Endpoints & Configuration
- **Remote MCP Endpoint**: `https://hydro.cosmolsesc.com/mcp` (`2025-06-18`, `2025-03-26`, `2024-11-05`)
- **OpenAPI 3.1.0 & Discovery**: `https://hydro.cosmolsesc.com/openapi-global.json` | `https://hydro.cosmolsesc.com/llms.txt`
- **In-Site Free Account Key (`GLBH-USR-*`)**: `POST https://hydro.cosmolsesc.com/api/global/auth/register` (`5` free synced credits).
- **Environment Variables**:
  - `COSMOL_HYDRO_URL`: Override API origin (default `https://hydro.cosmolsesc.com`).
  - `COSMOL_API_TOKEN`: Optional `GLBH-*` Bearer token (registered account key, USD pack, or subscription).
  - `COSMOL_OUTPUT_DIR`: Optional local directory for downloaded deliverable ZIP archives.

## Agent Behaviour Guidelines
1. Inspect quota first via `get_quota_and_pricing` (`2` anonymous + `+3` email/GitHub bonus or free registration = `5` free runs).
2. Pass local terrain/CAD files (`.dxf`, `.tif`, `.asc`, `.las`, `.geojson`, `.csv`, `.zip`) via `upload_terrain_base64` / `local_file_path` or `--file`.
3. On HTTP `402` (`PAYMENT_REQUIRED`), offer `claim_email_bonus_credits` if unclaimed, or present the Stripe Checkout URL cleanly without retrying in a loop.
