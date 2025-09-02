from js import Response

async def on_fetch(request, env):
    """
    Handle incoming HTTP requests in Cloudflare Workers
    """
    return Response.new("Hello from gtaf-mcp Python Worker!", {
        "status": 200,
        "headers": {
            "Content-Type": "text/plain"
        }
    })

# Export the handler for Cloudflare Workers
export = {
    "fetch": on_fetch
}
