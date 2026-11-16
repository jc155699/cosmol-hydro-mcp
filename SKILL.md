---
name: cosmol-2d-flood-studio
description: Execute cloud 2D Full-Momentum Shallow Water Equations (2D SWE) flood modelling, hydraulic structure sizing, and civil earthwork balances from local DXF, GeoTIFF, ASCII grid, LiDAR, GeoJSON, or ZIP files via COSMOL Global 2D Flood Studio.
---

# COSMOL 2D Flood Studio Agent Skill

Use this skill when the user asks to model 2D overland flooding, riverine inundation, dam breach / spillway hydraulics, stormwater culvert drainage, or cut-and-fill earthworks from terrain or CAD survey inputs.

## Capabilities & Supported Inputs
- **Supported Formats**: `.dxf`, `.tif`, `.tiff`, `.asc`, `.las`, `.laz`, `.geojson`, `.csv`, `.xyz`, `.zip` (automatically desensitised to local metric coordinates before cloud transmission).
- **Governing Engine**: Godunov-HLLC 2D Full-Momentum Shallow Water Equations (2D SWE), rain-on-grid / inflow hydrographs, hydraulic structures, and mass-balance QA (`<= 0.5%` error gate).
- **Deliverables**: `Global_2D_SWE_Hydraulic_Report.pdf`, georeferenced `.dxf` CAD flood/structure layers, `.xlsx` quantity schedules, 300-DPI compliance figures, and `HydroStudio_Deliverables_<job_id>.zip`.

## Quota & Billing
- **Complimentary Trial**: 2 full-resolution unwatermarked runs per anonymous client (`X-Guest-Token` persisted locally or supplied via `COSMOL_GUEST_TOKEN`).
- **Paid USD Packs (Stripe Checkout)**: Single Pack (`$29 USD` / 1 run), Pro Pack (`$89 USD` / 4 runs), Team Pack (`$249 USD` / 15 runs).
- **Bearer Token**: Set `COSMOL_API_TOKEN="GLBH-..."` after purchase or pass `--token`.

## Execution Workflow

### Option A — Local CLI (`scripts/hydro_cloud_cli.py`)
1. Check quota and USD plans:
   ```bash
   python3 scripts/hydro_cloud_cli.py quota
   ```
2. Upload terrain and run 2D flood simulation (auto-downloads `HydroStudio_Deliverables_<job_id>.zip`):
   ```bash
   python3 scripts/hydro_cloud_cli.py run \
     --file ./site_contours.dxf \
     --return-period 100 \
     --storm-pattern alternating_block \
     --duration-min 120 \
     --rainfall-mm 180 \
     --out-dir ./outputs
   ```
3. Check status or re-download deliverables for an existing `job_id`:
   ```bash
   python3 scripts/hydro_cloud_cli.py status <job_id> --download --out-dir ./outputs
   ```

### Option B — MCP Server (`cosmol_hydro_mcp.py` or Remote HTTP)
- **Local stdio MCP** (`cosmol_hydro_mcp.py`): exposes `get_quota_and_pricing`, `upload_local_terrain`, `run_2d_flood_simulation`, and `get_simulation_deliverables`.
- **Remote Streamable HTTP MCP**: `https://hydro.cosmolsesc.com/mcp` (`protocolVersion: 2024-11-05`).
- **OpenAPI 3.1.0 Spec**: `https://hydro.cosmolsesc.com/openapi-global.json`.

## Handling Quota Exhaustion (`402 PAYMENT_REQUIRED`)
- If `run` exits with code `2` (`PAYMENT_REQUIRED`) or returns a Stripe Checkout URL, present the Stripe Checkout URL (`$29 / $89 / $249 USD`) clearly to the user so they can top up credits and supply their `GLBH-*` token.
