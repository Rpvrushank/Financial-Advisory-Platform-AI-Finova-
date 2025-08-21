from mcp.server.fastmcp import FastMCP
import json
import sys

mcp = FastMCP("pre-made-data-server")

@mcp.tool()
def search_advisors(location: str) -> str:
    """Search for financial advisors using pre-made data.
    
    Args:
        location: City and state (e.g., "Charlotte, NC")
        
    Returns:
        str: JSON string of financial advisors
    """
    print(f"MCP Server: Searching for advisors in {location}", file=sys.stderr)
    
    advisors_data = {
        "Charlotte, NC": [
            {"name": "John Smith, CFP", "firm": "Smith Financial", "crd": "123456"},
            {"name": "Sarah Johnson, CFA", "firm": "Johnson Wealth", "crd": "234567"},
            {"name": "Amanda Williams, ChFC", "firm": "Williams Advisory Group", "crd": "345789"}
        ],
        "New York, NY": [
            {"name": "Michael Brown, ChFC", "firm": "Brown Associates", "crd": "345678"},
            {"name": "Lisa Davis, CFP", "firm": "Davis Capital", "crd": "456789"}
        ],
        "Miami, FL": [
            {"name": "Robert Wilson, CFA", "firm": "Wilson Group", "crd": "567890"},
            {"name": "Jennifer Lee, CFP", "firm": "Lee Financial", "crd": "678901"}
        ]
    }
    
   
    advisors = advisors_data.get(location, [])
    print(f" MCP Server: Found {len(advisors)} advisors for {location}", file=sys.stderr)
    
    return json.dumps(advisors)

if __name__ == "__main__":
    print("Starting Pre-made Advisor Data MCP Server...", file=sys.stderr)
    print("Server ready to handle MCP requests", file=sys.stderr)
    mcp.run(transport="stdio")