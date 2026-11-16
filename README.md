# COSMOL Global 2D Flood Studio — MCP & Multi-Agent Connector (`cosmol-hydro-mcp`)

Zero-dependency Model Context Protocol (MCP) server, portable `SKILL.md` / `AGENTS.md` pack, and Python CLI connecting AI coding and research agents to **COSMOL Global 2D Flood Studio** ([https://hydro.cosmolsesc.com](https://hydro.cosmolsesc.com)).

## Features
- **Full-Momentum 2D SWE Engine**: Cloud-executed Godunov-HLLC 2D Shallow Water Equations with rain-on-grid, inflow hydrographs, hydraulic structures, and mass-balance verification (`<= 0.5%`).
- **Multi-Format Terrain Ingestion**: Upload local `.dxf`, `.tif`, `.tiff`, `.asc`, `.las`, `.laz`, `.geojson`, `.csv`, `.xyz`, or `.zip` archives with automated metric coordinate desensitisation.
- **Complete Engineering Deliverables**: Auto-downloads `HydroStudio_Deliverables_<job_id>.zip` containing `Global_2D_SWE_Hydraulic_Report.pdf`, `.dxf` CAD overlays, `.xlsx` quantity schedules, and high-resolution flood maps.
- **Complimentary Trial + Stripe USD Packs**: 2 full-resolution unwatermarked runs included free; optional `GLBH-*` Bearer tokens via Stripe Checkout (`$29` Single / `$89` Pro 4-Pack / `$249` Team 15-Pack USD).

---

## Quickstart

### 1. Remote Streamable HTTP MCP (Zero Local Install)
Connect any MCP-compatible client directly to:
```text
https://hydro.cosmolsesc.com/mcp
```

### 2. Local MCP `stdio` Bridge (Claude Desktop / Cursor / VS Code)
Download `cosmol_hydro_mcp.py` (or clone this repository) and configure `mcp.json`:
```json
{
  "mcpServers": {
    "cosmol-hydro": {
      "command": "python3",
      "args": ["cosmol_hydro_mcp.py"],
      "env": {
        "COSMOL_HYDRO_URL": "https://hydro.cosmolsesc.com",
        "COSMOL_API_TOKEN": ""
      }
    }
  }
}
```

### 3. OpenAI Codex CLI (`~/.codex/config.toml`)
Copy `codex_config.toml` into your Codex configuration:
```toml
[mcp_servers.cosmol_hydro]
command = "python3"
args = ["cosmol_hydro_mcp.py"]
env = { COSMOL_HYDRO_URL = "https://hydro.cosmolsesc.com" }
```

### 4. Portable CLI & Agent Skill (`SKILL.md` / `AGENTS.md`)
```bash
python3 scripts/hydro_cloud_cli.py quota
python3 scripts/hydro_cloud_cli.py run --file ./terrain.dxf --return-period 100 --out-dir ./outputs
```

### 5. ChatGPT Actions / Coze Global / Poe / RapidAPI
Import the OpenAPI `3.1.0` specification or AI discovery manifest directly:
- **OpenAPI 3.1.0**: `https://hydro.cosmolsesc.com/openapi-global.json`
- **AI Search Index**: `https://hydro.cosmolsesc.com/llms.txt`
- **Plugin Manifest**: `https://hydro.cosmolsesc.com/.well-known/ai-plugin.json`

## Licence
Released under the MIT Licence — see [LICENSE](LICENSE).
