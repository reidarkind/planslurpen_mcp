# Planslurpen MCP Server

A Model Context Protocol (MCP) server for interacting with [Planslurpen](https://planslurpen.no/), a Norwegian service that uses AI to interpret zoning and regulation plans (reguleringsplaner).

## About Planslurpen

Planslurpen is a beta service from Direktoratet for byggkvalitet that provides machine-based interpretation of Norwegian regulation plans. It uses artificial intelligence to extract parameters from regulation plans, split by sub-areas (delområder) when available. The goal is to provide structured plan information for systems that need it.

## Features

This MCP server provides tools to:

- **Retrieve plan interpretations** by kommune number and plan ID
- **Look up plans by property address** using cadastral numbers
- **Download plan outputs** in JSON and XML (NPAD) formats
- **Get available fields and classifications** for filtering
- **Access plan provisions** (planbestemmelser) - the original legal text
- **Flexible response formats** (JSON or Markdown)

## Installation

### Prerequisites

- Python 3.10 or higher
- pip

### Setup

1. Clone or download this directory

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Make the server executable (optional):
```bash
chmod +x planslurpen_mcp.py
```

## Usage

### Running the Server

The server can be run directly:

```bash
python planslurpen_mcp.py
```

### Claude Desktop Configuration

Add this to your Claude Desktop configuration file:

**On macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**On Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "planslurpen": {
      "command": "python",
      "args": ["/absolute/path/to/planslurpen_mcp/planslurpen_mcp.py"]
    }
  }
}
```

Replace `/absolute/path/to/planslurpen_mcp/` with the actual path to this directory.

## Available Tools

### 1. `planslurpen_get_plan`
Retrieve AI-interpreted plan data by kommune number and plan ID.

**Parameters:**
- `kommunenummer` (required): 4-digit kommune number (e.g., "1106" for Haugesund)
- `plan_id` (required): Plan identifier (e.g., "RL791")
- `versjon` (optional): Specific version number
- `response_format` (optional): "json" or "markdown" (default: "json")

**Example:**
```
Get plan interpretation for Haugesund kommune 1106, plan RL791, version 3
```

### 2. `planslurpen_get_plan_by_id`
Retrieve plan data by its UUID.

**Parameters:**
- `plan_uuid` (required): UUID of the plan
- `response_format` (optional): "json" or "markdown"

### 3. `planslurpen_get_plan_output_json`
Download complete plan output in JSON format with optional filtering.

**Parameters:**
- `kommunenummer` (required): Kommune number
- `plan_id` (required): Plan ID
- `versjon` (optional): Version number
- `felt_kode` (optional): Field code to filter (e.g., "byggehøyde", "utnyttingsgrad")
- `klassifikasjoner` (optional): List of classifications to filter
- `response_format` (optional): "json" or "markdown"

**Tip:** Call `planslurpen_get_plan_fields` first to see available filters!

### 4. `planslurpen_get_plan_fields`
Get list of available fields and classifications for a plan.

**Parameters:**
- `kommunenummer` (required): Kommune number
- `plan_id` (required): Plan ID
- `versjon` (optional): Version number
- `response_format` (optional): "json" or "markdown"

**Use case:** Call this first to discover what filters you can use in other tools.

### 5. `planslurpen_get_plan_provisions`
Download plan provisions (planbestemmelser) - the original legal text.

**Parameters:**
- `kommunenummer` (required): Kommune number
- `plan_id` (required): Plan ID
- `versjon` (optional): Version number

### 6. `planslurpen_get_plan_output_xml`
Download plan output in NPAD XML format.

**Parameters:**
- `kommunenummer` (required): Kommune number
- `plan_id` (required): Plan ID
- `versjon` (optional): Version number

### 7. `planslurpen_lookup_property`
Look up regulation plans for a specific property by its cadastral address.

**Parameters:**
- `kommunenummer` (required): Kommune number
- `gardsnummer` (required): Farm/cadastral number
- `bruksnummer` (required): Parcel number
- `festenummer` (optional): Leasehold number
- `seksjonsnummer` (optional): Section number
- `response_format` (optional): "json" or "markdown"

**Example:**
```
Look up plans for property 1106-45-123
```

## Example Queries

Here are some example queries you can try with Claude:

1. **Get a plan interpretation:**
   > "Get the plan interpretation for Haugesund kommune 1106, plan RL791, version 3"

2. **Look up a property:**
   > "What regulation plans apply to property 1106-45-123 in Haugesund?"

3. **Explore available data:**
   > "What fields and classifications are available for plan RL791 in kommune 1106?"

4. **Get filtered data:**
   > "Get the byggeh høyde (building height) data for plan 1106/RL791"

## Norwegian Terms

- **Kommune**: Municipality
- **Reguleringsplan**: Zoning/regulation plan
- **Planbestemmelser**: Plan provisions (legal text)
- **Delområde**: Sub-area within a plan
- **Gardsnummer**: Farm/cadastral number
- **Bruksnummer**: Parcel number
- **Festenummer**: Leasehold number
- **Seksjonsnummer**: Section number
- **Utnyttingsgrad**: Utilization degree/floor area ratio
- **Byggehøyde**: Building height
- **NPAD**: Norwegian Planning Data (XML standard)

## API Information

- **Base URL**: https://planslurpen.no/api
- **Swagger Documentation**: https://planslurpen.no/api/swagger/index.html
- **Website**: https://planslurpen.no/

## Character Limits

The server implements a 25,000 character limit on responses. If responses are truncated:
- Use the `planslurpen_get_plan_fields` tool to see available filters
- Apply filters using `felt_kode` or `klassifikasjoner` parameters
- Request specific fields instead of full output

## Error Handling

The server provides clear, actionable error messages:
- **404 Not Found**: Plan doesn't exist - verify kommune number and plan ID
- **400 Bad Request**: Invalid parameters - check parameter format
- **Timeout**: Response too large - use filters to reduce size
- **Network errors**: Connection issues - check internet connection

## Development

This server follows MCP best practices:
- Uses Pydantic v2 for input validation
- Implements proper error handling with descriptive messages
- Supports multiple response formats (JSON and Markdown)
- Includes character limits and truncation
- All tools are read-only and idempotent
- Comprehensive docstrings and type hints

## Beta Notice

Planslurpen is currently in beta. The quality of AI interpretation may vary, and the service is actively seeking feedback. If you encounter issues or have feedback about the interpretation quality, visit https://planslurpen.no/ to report it.

## License

This MCP server is provided as-is for use with Planslurpen API. Please refer to Planslurpen's terms of service for API usage restrictions.

## Links

- Planslurpen Website: https://planslurpen.no/
- MCP Documentation: https://modelcontextprotocol.io/
- Example Plan: https://planslurpen.no/1106/RL791/3

## Support

For issues with:
- **This MCP server**: Open an issue in the repository
- **Planslurpen service**: Visit https://planslurpen.no/ for contact information
- **MCP protocol**: Refer to https://modelcontextprotocol.io/

---

Built with ❤️ for the Norwegian planning community