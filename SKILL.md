---
name: cosmol-hydrogeo-studio
description: Execute cloud Global GIS/CRS (M00), 2D SWE Flood & Earthworks (M01), Coupled 2D SWE + 3D MODFLOW 6 Seepage (M02), 2D Erosion & HESB Sediment Morphodynamics (M03), and Urban Stormwater LID/WSUD & 1D/2D Sewer (M04) via COSMOL HydroGeo Studio.
---

# COSMOL HydroGeo Studio Agent Skill (M00-M04, v2.1.0)

Use this skill when the user asks to model global GIS/UTM catchments, 2D shallow-water overland flooding, coupled surface-groundwater MODFLOW 6 seepage/piping, 2D erosion & sediment morphodynamics (SESC/HESB), or urban LID/SuDS/WSUD 1D/2D sewer drainage.

## Five Integrated Modules & Universal v2.1.0 Features
- **M00 (`run_m00_globalgeo_crs_mesh`)**: `EPSG:4326` GeoTIFF auto-UTM warp (`EPSG:32601..32760`), Civil 3D `LWPOLYLINE` code-38 DXF contours, `elev_units` (`auto`/`m`/`ft`), `(E0, N0)` metric shift, D8 catchment & 3-tier adaptive mesh.
- **M01 (`run_2d_flood_simulation`)**: 2D Full-Momentum SWE flood routing, Koppen-Geiger regional IDF (`rainfall_mm=0`), spillway/culvert sizing & Design Rev 5 cut/fill earthworks.
- **M02 (`run_m02_coupled_swe_modflow6`)**: Two-way 2D SWE + 3D MODFLOW 6 DISV+XT3D seepage, Theis/Cooper-Jacob, cutoff walls & Terzaghi/Sellmeijer piping checks.
- **M03 (`run_m03_sediment_morpho_sesc`)**: 2D Grid-RUSLE, Wu (2007) sediment morphodynamics & PACl+PAM HESB sizing (`scenario="global_sesc_morpho"`).
- **M04 (`run_m04_urban_stormwater_lid_sewer`)**: Preissmann 1D sewer + 2D urban SWE, LID/SuDS/WSUD & flood hazard (`scenario="global_wsud_1d2d"`).
- **5-Jurisdiction Auto-Adapter**: Automatically resolves statutory standards across `US/CA`, `UK`, `EU`, `AU/NZ`, and `Global` from `(lon, lat)`, `place`, or `crs_label`.

## Supported Inputs & Deliverables
- **Formats**: `.dxf`, `.tif`, `.tiff`, `.asc`, `.las`, `.laz`, `.geojson`, `.shp`, `.csv`, `.xyz`, `.zip` (sample GeoJSON in `examples/upper_coomera_qld/upper_coomera_catchment_survey.geojson`).
- **Deliverables**: `01_Compliance_Engineering_Report.pdf` (4-page), `.docx`, A3 blueprint PDFs, `.dxf` CAD overlays, `.xlsx` KPI/BOQ schedules, 300-DPI 6-panel atlases, 1200x640 animated `.gif`, interactive `.html` viewers, and `HydroStudio_Deliverables_<job_id>.zip`.

## Quota, Free Registration & Billing (USD)
- **Free Trial (`2 + 3 = 5` Runs)**: `2` anonymous runs + `3` bonus runs via `claim_email_bonus_credits` (email or GitHub handle), or register for free at `https://hydro.cosmolsesc.com` (`POST /api/global/auth/register`) to unlock `5` synced credits and a persistent `GLBH-USR-*` key.
- **Credit Packs**: Starter 4-Pack (`$39 USD`), Pro 15-Pack (`$99 USD`), Consultancy 60-Pack (`$299 USD`).
- **Subscriptions**: Pro (`$79/mo` or `$759/yr`), Team White-Label (`$249/mo` or `$2,390/yr` with custom company branding).
- **Bearer Token**: Set `COSMOL_API_TOKEN="GLBH-..."` or pass `--token`.

## Execution Options
- **Remote Streamable HTTP MCP**: `https://hydro.cosmolsesc.com/mcp` (`2025-06-18`)
- **GitHub `uvx` (No PyPI Wait)**: `uvx --from git+https://github.com/jc155699/cosmol-hydro-mcp cosmol-hydrogeo-mcp`
- **PyPI / npm**: `uvx cosmol-hydrogeo-mcp` | `npx -y @cosmol/hydrogeo-mcp`
- **OpenAPI 3.1.0**: `https://hydro.cosmolsesc.com/openapi-global.json`
- **Sample CLI Run**: `python3 scripts/hydro_cloud_cli.py run --module m00 --file examples/upper_coomera_qld/upper_coomera_catchment_survey.geojson --lon 153.215 --lat -28.055 --out-dir ./outputs`
