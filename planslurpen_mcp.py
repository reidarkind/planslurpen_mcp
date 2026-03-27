#!/usr/bin/env python3
"""
Planslurpen MCP Server

A Model Context Protocol server for interacting with Planslurpen API, which provides
AI-powered interpretation of Norwegian zoning and regulation plans (reguleringsplaner).

This server enables LLMs to:
- Retrieve plan interpretations by kommune and plan ID
- Download plan outputs in JSON and XML formats
- Look up plans by property address
- Get available fields and classifications
- Access plan provisions (planbestemmelser)
"""

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List, Dict, Any, Literal
from enum import Enum
import httpx
import json
import re

# Initialize FastMCP server
mcp = FastMCP("planslurpen_mcp")

# Constants
API_BASE_URL = "https://planslurpen.no/api"
CHARACTER_LIMIT = 25000
DEFAULT_TIMEOUT = 30.0

# ============================================================================
# Enums and Models
# ============================================================================

class ResponseFormat(str, Enum):
    """Response format options"""
    JSON = "json"
    MARKDOWN = "markdown"


# ============================================================================
# Shared Utilities
# ============================================================================

async def make_api_request(
    endpoint: str,
    method: str = "GET",
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    data: Optional[Dict[str, Any]] = None,
    files: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Make an HTTP request to the Planslurpen API.
    
    Args:
        endpoint: API endpoint path (e.g., '/planslurp/{kommune}/{planId}')
        method: HTTP method (GET, POST, etc.)
        params: Query parameters
        headers: HTTP headers
        data: Request body data
        files: Files to upload
        
    Returns:
        Dict containing the API response
        
    Raises:
        Exception with descriptive error messages for API failures
    """
    url = f"{API_BASE_URL}{endpoint}"
    
    try:
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            response = await client.request(
                method=method,
                url=url,
                params=params,
                headers=headers,
                json=data if data and not files else None,
                files=files
            )
            
            # Check for errors
            if response.status_code == 404:
                raise Exception(
                    f"Plan not found. Please verify the kommune number and plan ID are correct. "
                    f"Visit https://planslurpen.no/ to search for available plans."
                )
            elif response.status_code == 400:
                raise Exception(
                    f"Bad request: {response.text}. Please check your parameters. "
                    f"Ensure kommune number and plan ID are valid strings."
                )
            elif response.status_code == 401 or response.status_code == 403:
                raise Exception(
                    f"Authentication error. If using the upload endpoint, ensure you provide a valid X-API-KEY header."
                )
            elif response.status_code >= 500:
                raise Exception(
                    f"Planslurpen API server error (status {response.status_code}). "
                    f"The service may be temporarily unavailable. Please try again later."
                )
            
            response.raise_for_status()
            
            # Try to parse as JSON, fallback to text
            try:
                return response.json()
            except:
                return {"content": response.text}
                
    except httpx.TimeoutException:
        raise Exception(
            f"Request timed out after {DEFAULT_TIMEOUT} seconds. "
            f"The plan data may be large. Try using filters to reduce the response size."
        )
    except httpx.NetworkError as e:
        raise Exception(
            f"Network error occurred: {str(e)}. Please check your internet connection."
        )
    except Exception as e:
        if "Plan not found" in str(e) or "Bad request" in str(e) or "Authentication error" in str(e):
            raise
        raise Exception(f"API request failed: {str(e)}")


def truncate_content(content: str, max_length: int = CHARACTER_LIMIT) -> str:
    """
    Truncate content to fit within character limit.
    
    Args:
        content: Content to truncate
        max_length: Maximum length in characters
        
    Returns:
        Truncated content with informative message
    """
    if len(content) <= max_length:
        return content
        
    truncated = content[:max_length]
    return f"{truncated}\n\n[Content truncated at {max_length} characters. Use filters or specify fields to reduce response size.]"


def format_response_json(data: Any) -> str:
    """Format data as JSON string."""
    return json.dumps(data, ensure_ascii=False, indent=2)


def format_plan_markdown(data: Dict[str, Any]) -> str:
    """
    Format plan data as Markdown for better readability.
    
    Args:
        data: Plan data from API
        
    Returns:
        Formatted Markdown string
    """
    md_parts = ["# Planslurpen - Plan Information\n"]
    
    # Basic info
    if "kommunenummer" in data:
        md_parts.append(f"**Kommune Number**: {data['kommunenummer']}\n")
    if "planId" in data:
        md_parts.append(f"**Plan ID**: {data['planId']}\n")
    if "planNavn" in data:
        md_parts.append(f"**Plan Name**: {data['planNavn']}\n")
    if "versjon" in data:
        md_parts.append(f"**Version**: {data['versjon']}\n")
        
    # Add sections
    if "delomrader" in data and data["delomrader"]:
        md_parts.append("\n## Delområder (Sub-areas)\n")
        for i, delomrade in enumerate(data["delomrader"][:10], 1):  # Limit to first 10
            md_parts.append(f"\n### {i}. {delomrade.get('navn', 'Unknown')}\n")
            if "felter" in delomrade:
                for felt in delomrade["felter"][:5]:  # Limit fields
                    md_parts.append(f"- **{felt.get('navn', 'Unknown')}**: {felt.get('verdi', 'N/A')}\n")
    
    # Truncate if needed
    result = "".join(md_parts)
    return truncate_content(result)


# ============================================================================
# Tool Input Models
# ============================================================================

class GetPlanInput(BaseModel):
    """Input for retrieving plan interpretation by kommune and plan ID."""
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')
    
    kommunenummer: str = Field(
        ...,
        description="Kommune (municipality) number as a string (e.g., '1106' for Haugesund, '0301' for Oslo)",
        min_length=4,
        max_length=4,
        pattern=r'^\d{4}$'
    )
    plan_id: str = Field(
        ...,
        description="Plan ID as a string (e.g., 'RL791', '20220001')",
        min_length=1,
        max_length=50
    )
    versjon: Optional[int] = Field(
        default=None,
        description="Optional version number to retrieve a specific version",
        ge=1
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.JSON,
        description="Response format: 'json' for structured data or 'markdown' for human-readable format"
    )
    
    @field_validator('kommunenummer')
    @classmethod
    def validate_kommunenummer(cls, v: str) -> str:
        if not v.isdigit():
            raise ValueError("Kommune number must contain only digits")
        return v


class GetPlanByIdInput(BaseModel):
    """Input for retrieving plan interpretation by UUID."""
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')
    
    plan_uuid: str = Field(
        ...,
        description="UUID of the plan (e.g., '123e4567-e89b-12d3-a456-426614174000')",
        min_length=36,
        max_length=36,
        pattern=r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.JSON,
        description="Response format: 'json' for structured data or 'markdown' for human-readable format"
    )


class GetPlanOutputInput(BaseModel):
    """Input for downloading plan output JSON with optional filters."""
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')
    
    kommunenummer: str = Field(
        ...,
        description="Kommune number (e.g., '1106')",
        pattern=r'^\d{4}$'
    )
    plan_id: str = Field(
        ...,
        description="Plan ID (e.g., 'RL791')"
    )
    versjon: Optional[int] = Field(
        default=None,
        description="Version number",
        ge=1
    )
    felt_kode: Optional[str] = Field(
        default=None,
        description="Field code to filter content (e.g., 'utnyttingsgrad', 'byggehøyde')"
    )
    klassifikasjoner: Optional[List[str]] = Field(
        default=None,
        description="List of classifications to filter content",
        max_items=20
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.JSON,
        description="Response format"
    )


class GetPlanFieldsInput(BaseModel):
    """Input for getting available fields and classifications."""
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')
    
    kommunenummer: str = Field(
        ...,
        description="Kommune number",
        pattern=r'^\d{4}$'
    )
    plan_id: str = Field(
        ...,
        description="Plan ID"
    )
    versjon: Optional[int] = Field(
        default=None,
        description="Version number",
        ge=1
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.JSON,
        description="Response format"
    )


class GetPlanProvisionsInput(BaseModel):
    """Input for downloading plan provisions (planbestemmelser)."""
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')
    
    kommunenummer: str = Field(
        ...,
        description="Kommune number",
        pattern=r'^\d{4}$'
    )
    plan_id: str = Field(
        ...,
        description="Plan ID"
    )
    versjon: Optional[int] = Field(
        default=None,
        description="Version number",
        ge=1
    )


class GetPlanOutputXMLInput(BaseModel):
    """Input for downloading plan output in XML (NPAD format)."""
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')
    
    kommunenummer: str = Field(
        ...,
        description="Kommune number",
        pattern=r'^\d{4}$'
    )
    plan_id: str = Field(
        ...,
        description="Plan ID"
    )
    versjon: Optional[int] = Field(
        default=None,
        description="Version number",
        ge=1
    )


class LookupPropertyInput(BaseModel):
    """Input for looking up plans by property address."""
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')
    
    kommunenummer: str = Field(
        ...,
        description="Kommune number",
        pattern=r'^\d{4}$'
    )
    gardsnummer: str = Field(
        ...,
        description="Gards number (cadastral number)",
        min_length=1
    )
    bruksnummer: str = Field(
        ...,
        description="Bruks number (parcel number)",
        min_length=1
    )
    festenummer: Optional[str] = Field(
        default=None,
        description="Optional feste number (leasehold number)"
    )
    seksjonsnummer: Optional[str] = Field(
        default=None,
        description="Optional seksjon number (section number)"
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.JSON,
        description="Response format"
    )


# ============================================================================
# MCP Tools
# ============================================================================

@mcp.tool(
    name="planslurpen_get_plan",
    annotations={
        "title": "Get Plan Interpretation",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def planslurpen_get_plan(params: GetPlanInput) -> str:
    """
    Retrieve AI-interpreted regulation plan data by kommune number and plan ID.
    
    This tool fetches the complete interpretation of a Norwegian zoning/regulation plan,
    including all sub-areas (delområder), fields, and classifications extracted by AI.
    
    Use this when you need:
    - Complete plan interpretation data
    - Information about specific regulation plans
    - Details about plan sub-areas and their properties
    
    Args:
        params (GetPlanInput): Contains:
            - kommunenummer (str): 4-digit kommune number (e.g., '1106')
            - plan_id (str): Plan identifier (e.g., 'RL791')
            - versjon (Optional[int]): Specific version number
            - response_format (str): 'json' or 'markdown'
            
    Returns:
        str: Plan interpretation data in requested format
        
    Example usage:
        - Get plan for Haugesund: kommunenummer='1106', plan_id='RL791'
        - Get specific version: kommunenummer='1106', plan_id='RL791', versjon=3
    """
    query_params = {}
    if params.versjon:
        query_params['versjon'] = params.versjon
    
    data = await make_api_request(
        f"/planslurp/{params.kommunenummer}/{params.plan_id}",
        params=query_params
    )
    
    if params.response_format == ResponseFormat.MARKDOWN:
        return format_plan_markdown(data)
    else:
        result = format_response_json(data)
        return truncate_content(result)


@mcp.tool(
    name="planslurpen_get_plan_by_id",
    annotations={
        "title": "Get Plan by UUID",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def planslurpen_get_plan_by_id(params: GetPlanByIdInput) -> str:
    """
    Retrieve plan interpretation data by its unique UUID identifier.
    
    Use this when you have a plan's UUID from a previous query or reference.
    
    Args:
        params (GetPlanByIdInput): Contains:
            - plan_uuid (str): UUID of the plan
            - response_format (str): 'json' or 'markdown'
            
    Returns:
        str: Plan interpretation data in requested format
    """
    data = await make_api_request(f"/planslurp/{params.plan_uuid}")
    
    if params.response_format == ResponseFormat.MARKDOWN:
        return format_plan_markdown(data)
    else:
        result = format_response_json(data)
        return truncate_content(result)


@mcp.tool(
    name="planslurpen_get_plan_output_json",
    annotations={
        "title": "Download Plan Output JSON",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def planslurpen_get_plan_output_json(params: GetPlanOutputInput) -> str:
    """
    Download complete plan output in JSON format with optional filtering.
    
    This provides the full output data structure. Use filters to reduce response size:
    - Use felt_kode to get specific fields (e.g., 'byggehøyde', 'utnyttingsgrad')
    - Use klassifikasjoner to filter by classification types
    
    If response is truncated, use filters to narrow down the data you need.
    First call planslurpen_get_plan_fields to see available filters.
    
    Args:
        params (GetPlanOutputInput): Contains:
            - kommunenummer (str): Kommune number
            - plan_id (str): Plan ID
            - versjon (Optional[int]): Version number
            - felt_kode (Optional[str]): Field code filter
            - klassifikasjoner (Optional[List[str]]): Classification filters
            - response_format (str): 'json' or 'markdown'
            
    Returns:
        str: Complete plan output data
        
    Tip: If output is too large, call planslurpen_get_plan_fields first to see
    available filters, then use those filters here to get targeted data.
    """
    query_params = {}
    if params.versjon:
        query_params['versjon'] = params.versjon
    if params.felt_kode:
        query_params['feltKode'] = params.felt_kode
    if params.klassifikasjoner:
        query_params['klassifikasjoner'] = params.klassifikasjoner
    
    data = await make_api_request(
        f"/nedlasting/output/{params.kommunenummer}/{params.plan_id}",
        params=query_params
    )
    
    if params.response_format == ResponseFormat.MARKDOWN:
        return format_plan_markdown(data)
    else:
        result = format_response_json(data)
        return truncate_content(result)


@mcp.tool(
    name="planslurpen_get_plan_fields",
    annotations={
        "title": "Get Available Plan Fields and Classifications",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def planslurpen_get_plan_fields(params: GetPlanFieldsInput) -> str:
    """
    Get list of available fields and classifications for a plan.
    
    Use this to discover what data is available in a plan before downloading
    the full output. The response shows all fields that can be used as filters
    in planslurpen_get_plan_output_json.
    
    Args:
        params (GetPlanFieldsInput): Contains:
            - kommunenummer (str): Kommune number
            - plan_id (str): Plan ID
            - versjon (Optional[int]): Version number
            - response_format (str): 'json' or 'markdown'
            
    Returns:
        str: Available fields and classifications
        
    Use case: Call this first to see what filters are available, then use those
    filters in planslurpen_get_plan_output_json to get specific data.
    """
    query_params = {}
    if params.versjon:
        query_params['versjon'] = params.versjon
    
    data = await make_api_request(
        f"/nedlasting/output/{params.kommunenummer}/{params.plan_id}/felterOgKlassifikasjoner",
        params=query_params
    )
    
    result = format_response_json(data)
    return truncate_content(result)


@mcp.tool(
    name="planslurpen_get_plan_provisions",
    annotations={
        "title": "Download Plan Provisions",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def planslurpen_get_plan_provisions(params: GetPlanProvisionsInput) -> str:
    """
    Download plan provisions (planbestemmelser) - the legal text of the plan.
    
    This retrieves the original plan provisions document that was used as input
    for the AI interpretation.
    
    Args:
        params (GetPlanProvisionsInput): Contains:
            - kommunenummer (str): Kommune number
            - plan_id (str): Plan ID
            - versjon (Optional[int]): Version number
            
    Returns:
        str: Plan provisions document content
    """
    query_params = {}
    if params.versjon:
        query_params['versjon'] = params.versjon
    
    data = await make_api_request(
        f"/nedlasting/planbestemmelser/{params.kommunenummer}/{params.plan_id}",
        params=query_params
    )
    
    # This likely returns text content
    if isinstance(data, dict) and "content" in data:
        return truncate_content(data["content"])
    else:
        result = format_response_json(data)
        return truncate_content(result)


@mcp.tool(
    name="planslurpen_get_plan_output_xml",
    annotations={
        "title": "Download Plan Output XML (NPAD)",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def planslurpen_get_plan_output_xml(params: GetPlanOutputXMLInput) -> str:
    """
    Download plan output in NPAD XML format.
    
    NPAD (Norwegian Planning Data) is a standardized XML format for planning data.
    Use this when you need the plan data in XML format for integration with
    other systems.
    
    Args:
        params (GetPlanOutputXMLInput): Contains:
            - kommunenummer (str): Kommune number
            - plan_id (str): Plan ID
            - versjon (Optional[int]): Version number
            
    Returns:
        str: Plan data in NPAD XML format
    """
    query_params = {}
    if params.versjon:
        query_params['versjon'] = params.versjon
    
    data = await make_api_request(
        f"/nedlasting/output/{params.kommunenummer}/{params.plan_id}/xml",
        params=query_params
    )
    
    # XML content
    if isinstance(data, dict) and "content" in data:
        return truncate_content(data["content"])
    else:
        result = format_response_json(data)
        return truncate_content(result)


@mcp.tool(
    name="planslurpen_lookup_property",
    annotations={
        "title": "Look Up Plans by Property Address",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def planslurpen_lookup_property(params: LookupPropertyInput) -> str:
    """
    Look up regulation plans for a specific property by its cadastral address.
    
    Norwegian properties are identified by:
    - Kommunenummer (municipality)
    - Gardsnummer (farm number)
    - Bruksnummer (parcel number)
    - Optional: Festenummer (leasehold) and Seksjonsnummer (section)
    
    Use this to find which plans apply to a specific property address.
    
    Args:
        params (LookupPropertyInput): Contains:
            - kommunenummer (str): Kommune number
            - gardsnummer (str): Farm/cadastral number
            - bruksnummer (str): Parcel number
            - festenummer (Optional[str]): Leasehold number
            - seksjonsnummer (Optional[str]): Section number
            - response_format (str): 'json' or 'markdown'
            
    Returns:
        str: List of plans that apply to the property
        
    Example: Look up property 1106-45-123:
        kommunenummer='1106', gardsnummer='45', bruksnummer='123'
    """
    query_params = {}
    if params.festenummer:
        query_params['festenummer'] = params.festenummer
    if params.seksjonsnummer:
        query_params['seksjonsnummer'] = params.seksjonsnummer
    
    data = await make_api_request(
        f"/planregister/{params.kommunenummer}/{params.gardsnummer}/{params.bruksnummer}",
        params=query_params
    )
    
    if params.response_format == ResponseFormat.MARKDOWN:
        # Format property lookup results
        md = f"# Property Plans Lookup\n\n"
        md += f"**Property**: {params.kommunenummer}-{params.gardsnummer}-{params.bruksnummer}\n\n"
        
        if isinstance(data, list):
            md += f"## Found {len(data)} plan(s)\n\n"
            for i, plan in enumerate(data[:20], 1):  # Limit to first 20
                md += f"### {i}. {plan.get('planNavn', 'Unknown Plan')}\n"
                md += f"- **Plan ID**: {plan.get('planId', 'N/A')}\n"
                md += f"- **Kommune**: {plan.get('kommunenummer', 'N/A')}\n"
                if 'status' in plan:
                    md += f"- **Status**: {plan['status']}\n"
                md += "\n"
        else:
            md += str(data)
        
        return truncate_content(md)
    else:
        result = format_response_json(data)
        return truncate_content(result)



# ============================================================================
# Server Entry Point
# ============================================================================

def main():
    # Run the MCP server
    mcp.run()


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
