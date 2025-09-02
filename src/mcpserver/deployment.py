from mcp.server.fastmcp import FastMCP

mcp = FastMCP("deployment")

@mcp.tool()
# add 2 digit and return the result
def add(digit1: int, digit2: int) -> int:
    """Add 2 digit and return the result"""
    return digit1 + digit2

    