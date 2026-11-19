# COSMOL HydroGeo Studio™ v2.0 — Multi-Physics Cloud Engine & MCP (`cosmol-hydrogeo-mcp`)

[![Live Web Studio](https://img.shields.io/badge/Web_Studio-hydro.cosmolsesc.com-0ea5e9)](https://hydro.cosmolsesc.com)
[![MCP Protocol](https://img.shields.io/badge/MCP-Streamable_HTTP_2025--06--18-10b981)](https://hydro.cosmolsesc.com/mcp)
[![OpenAPI 3.1](https://img.shields.io/badge/OpenAPI-3.1.0-f59e0b)](https://hydro.cosmolsesc.com/openapi-global.json)
[![License: MIT](https://img.shields.io/badge/License-MIT-64748b)](LICENSE)

Zero-dependency Model Context Protocol (MCP) server, Python `stdio` bridge, CLI client, and `SKILL.md` / `AGENTS.md` pack connecting **Claude, Cursor, VS Code, OpenAI Codex, and custom AI agents** directly to **COSMOL HydroGeo Studio™** ([https://hydro.cosmolsesc.com](https://hydro.cosmolsesc.com)).

---

## Live Australian Benchmark Showcases (`Upper Coomera & Oxenford-Coomera, QLD · GDA2020 / MGA56`)

All 5 physics modules run genuine numerical solvers on real Australian elevation tiles and satellite imagery — zero synthetic placeholders:

| M01 · 2D SWE Flood & Rev 5 Earthwork (`731.7 m³/s` Inflow) | M02 · Coupled 2D SWE + MODFLOW 6 Seepage (`Fs = 3.20`) |
| :---: | :---: |
| ![M01 2D SWE Flood Evolution](https://hydro.cosmolsesc.com/showcase/m01/03_Module01_Dynamic_Evolution.gif) | ![M02 Coupled SW-GW Seepage Evolution](https://hydro.cosmolsesc.com/showcase/m02/03_Module02_Dynamic_Evolution.gif) |
| **M03 · 2D Erosion & HESB SESC (`31.6 mg/L` Outlet `< 50 mg/L`)** | **M04 · 1D/2D Urban Sewer & WSUD (`86.4%` Volume Capture)** |
| ![M03 Sediment Morpho & HESB TSS](https://hydro.cosmolsesc.com/showcase/m03/03_Module03_Dynamic_Evolution.gif) | ![M04 Urban LID & 1D/2D Street Flood](https://hydro.cosmolsesc.com/showcase/m04/03_Module04_Dynamic_Evolution.gif) |

- **M00 GlobalGeo CRS & D8 Mesh Animation**: [03_Module00_Dynamic_Evolution.gif](https://hydro.cosmolsesc.com/showcase/m00/03_Module00_Dynamic_Evolution.gif)
- **Sample 4-Page Compliance PDFs**: [M01 Flood & Earthwork Report](https://hydro.cosmolsesc.com/showcase/m01/01_Compliance_Engineering_Report.pdf) · [M03 Erosion & HESB Report](https://hydro.cosmolsesc.com/showcase/m03/01_Compliance_Engineering_Report.pdf)

---

## Five Integrated Modules & 9 MCP Tools

| Module | MCP Tool | Governing Physics & Outputs |
| :--- | :--- | :--- |
| **M00 GlobalGeo CRS** | `run_m00_globalgeo_crs_mesh` | Auto-UTM (`EPSG:326xx/327xx` & `GDA2020`), Priority-Flood D8 catchment & 3-tier breakline mesh |
| **M01 2D SWE Flood** | `run_2d_flood_simulation` | Explicit 2D SWE flood routing, spillway/culvert sizing & Design Rev 5 mass-haul earthwork |
| **M02 SWE + MODFLOW 6** | `run_m02_coupled_swe_modflow6` | Two-way 2D SWE + 3D MODFLOW 6 DISV+XT3D seepage, cutoff walls & Terzaghi/Sellmeijer piping |
| **M03 Erosion & SESC** | `run_m03_sediment_morpho_sesc` | Grid-RUSLE, Wu (2007) 4-fraction morphodynamics, Exner bed change & PACl+PAM HESB sizing |
| **M04 Urban LID & Sewer** | `run_m04_urban_stormwater_lid_sewer` | Preissmann 1D trunk pipe + 2D urban SWE, MUSIC WSUD/LID capture & AIDR H1-H6 hazard |

Utility MCP tools: `get_quota_and_pricing`, `claim_email_bonus_credits`, `upload_terrain_base64`, and `get_simulation_deliverables` (returns `4`-page `.pdf`, `.docx`, `.dxf` CAD, `.xlsx` BOQ, `300`-DPI atlases, animated `.gif`, interactive `.html`, and `.zip` archive).

---

## Quickstart (`0` Dependencies Required)

### 1. Remote Streamable HTTP MCP (Fastest — Cursor / Claude / Codex)
Connect directly to the hosted MCP endpoint (Protocol `2025-06-18` / `2025-03-26` / `2024-11-05`):
```json
{
  "mcpServers": {
    "cosmol-hydrogeo": {
      "url": "https://hydro.cosmolsesc.com/mcp"
    }
  }
}
```

### 2. Local `stdio` MCP Direct from GitHub (`uvx` / `pip`, Works Immediately)
```json
{
  "mcpServers": {
    "cosmol-hydrogeo": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/jc155699/cosmol-hydro-mcp", "cosmol-hydrogeo-mcp"],
      "env": { "COSMOL_HYDRO_URL": "https://hydro.cosmolsesc.com", "COSMOL_API_TOKEN": "" }
    }
  }
}
```
Or install directly with `pip`: `pip install git+https://github.com/jc155699/cosmol-hydro-mcp.git` (or `uvx cosmol-hydrogeo-mcp` / `npx -y @cosmol/hydrogeo-mcp`).

### 3. 10-Second Australian Coomera CLI Run (Bundled Sample Survey)
```bash
git clone https://github.com/jc155699/cosmol-hydro-mcp.git && cd cosmol-hydro-mcp
python3 scripts/hydro_cloud_cli.py quota
python3 scripts/hydro_cloud_cli.py run --module m00 --file examples/upper_coomera_qld/upper_coomera_catchment_survey.geojson --lon 153.215 --lat -28.055 --out-dir ./outputs
```

### 4. OpenAI Codex CLI (`~/.codex/config.toml`) & ChatGPT Custom GPT Actions
```toml
[mcp_servers.cosmol_hydrogeo]
url = "https://hydro.cosmolsesc.com/mcp"
```
ChatGPT GPT Action OpenAPI 3.1.0 URL: `https://hydro.cosmolsesc.com/openapi-global.json` · AI Discovery Index: `https://hydro.cosmolsesc.com/llms.txt`

---

## Free Trial, Account Key & USD Pricing

- **Free Trial (`2 + 3 = 5` Full-Resolution Runs)**: Start with `2` anonymous runs, then unlock `+3` bonus runs via `claim_email_bonus_credits` — or click **Sign Up Free (5 Runs)** at [https://hydro.cosmolsesc.com](https://hydro.cosmolsesc.com) (`POST /api/global/auth/register`) to obtain a persistent `GLBH-USR-*` API/MCP key synced across devices.
- **Pay-As-You-Go USD Packs (Stripe)**: Starter 4-Pack (`$39`) · Pro 15-Pack (`$99`) · Consultancy 60-Pack (`$299`).
- **Subscriptions (Stripe USD)**: Pro (`$79/mo` · `$759/yr`) · Team + White-Label PDFs (`$249/mo` · `$2,390/yr`).

## Licence
Released under the MIT Licence — see [LICENSE](LICENSE).
