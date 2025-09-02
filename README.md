# GTAF MCP Server

A Model Context Protocol (MCP) server for test automation and mathematical operations, built with FastMCP.

## 🚀 Features

- **Add Tool**: Simple addition of two integers
- **Git-based Installation**: Install directly from GitHub repository
- **Cursor Integration**: Easy setup with Cursor IDE
- **FastMCP Framework**: Built on the modern FastMCP framework

## 📋 Prerequisites

Before setting up the MCP server, ensure you have the following installed:

### Required Dependencies

1. **Python 3.12+**
   ```bash
   # Check your Python version
   python --version
   ```

2. **uv (Universal Python Package Installer)**
   ```bash
   # Install uv
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Or using pip
   pip install uv
   
   # Verify installation
   uv --version
   ```

3. **Cursor IDE**
   - Download from [cursor.sh](https://cursor.sh/)
   - Ensure you have the latest version with MCP support

## 🛠️ Setup Instructions

### Option 1: Direct Installation via Git (Recommended)

This method installs the MCP server directly from the GitHub repository:

1. **Create or update your Cursor MCP configuration file**
   
   Create/edit `~/.cursor/mcp.json` (or your Cursor settings directory):
   ```json
   {
     "mcpServers": {
       "gtaf-mcp": {
         "command": "uvx",
         "args": ["--from", "git+https://github.com/shiwantha-lakmal/gtaf-mcp.git", "mcp-server"]
       }
     }
   }
   ```

2. **Restart Cursor IDE**
   
   The MCP server will be automatically installed and started when Cursor loads.

### Option 2: Local Development Setup

For local development or customization:

1. **Clone the repository**
   ```bash
   git clone https://github.com/shiwantha-lakmal/gtaf-mcp.git
   cd gtaf-mcp
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Test the server locally**
   ```bash
   uv run mcp-server
   ```

4. **Configure Cursor for local development**
   
   Update your `~/.cursor/mcp.json`:
   ```json
   {
     "mcpServers": {
       "gtaf-mcp-local": {
         "command": "uv",
         "args": ["run", "--project", "/path/to/your/gtaf-mcp", "mcp-server"],
         "cwd": "/path/to/your/gtaf-mcp",
         "env": {
           "PYTHONPATH": "/path/to/your/gtaf-mcp/src"
         }
       }
     }
   }
   ```

## 🔧 Configuration

### MCP Server Configuration Locations

Depending on your operating system, place the `mcp.json` file in:

- **macOS**: `~/.cursor/mcp.json`
- **Windows**: `%APPDATA%\Cursor\User\mcp.json`
- **Linux**: `~/.config/cursor/mcp.json`

### Sample mcp.json Configuration

```json
{
  "mcpServers": {
    "gtaf-mcp": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/shiwantha-lakmal/gtaf-mcp.git", "mcp-server"]
    }
  }
}
```

## 🎯 Available Tools

### `add`
Adds two integers and returns the result.

**Parameters:**
- `digit1` (int): First number
- `digit2` (int): Second number

**Returns:**
- `int`: Sum of the two numbers

**Example usage in Cursor:**
```
@gtaf-mcp add 3 and 5
```

## 🧪 Testing the Setup

1. **Verify MCP server is running**
   
   In Cursor, you should see the MCP server listed in the MCP panel or status.

2. **Test the add tool**
   
   Try using the tool in Cursor:
   ```
   Can you add 10 and 15 using the MCP tool?
   ```

3. **Check for errors**
   
   If there are issues, check Cursor's developer console or MCP logs.

## 🚨 Troubleshooting

### Common Issues

1. **"uvx command not found"**
   ```bash
   # Install uv first
   curl -LsSf https://astral.sh/uv/install.sh | sh
   # Restart your terminal
   ```

2. **"MCP server failed to start"**
   - Ensure Python 3.12+ is installed
   - Check that the repository is accessible
   - Verify your `mcp.json` syntax is correct

3. **"Tool not found"**
   - Restart Cursor IDE
   - Check MCP server logs
   - Verify the server is listed in Cursor's MCP panel

4. **Permission issues**
   ```bash
   # On macOS/Linux, ensure the mcp.json file has correct permissions
   chmod 644 ~/.cursor/mcp.json
   ```

### Debug Mode

To run the server in debug mode for troubleshooting:

```bash
# Local testing
uv run mcp-server --debug

# Check server logs
uvx --from git+https://github.com/shiwantha-lakmal/gtaf-mcp.git mcp-server --verbose
```

## 🔄 Updates

The MCP server automatically pulls the latest version from the Git repository each time it starts. To force an update:

1. Restart Cursor IDE, or
2. Clear uvx cache: `uvx cache clean`

## 📚 Development

### Project Structure

```
gtaf-mcp/
├── src/
│   └── mcpserver/
│       ├── __init__.py
│       ├── __main__.py          # Entry point
│       └── deployment.py        # MCP tools definition
├── pyproject.toml               # Project configuration
├── mcp.json                     # Sample MCP configuration
└── README.md                    # This file
```

### Adding New Tools

1. Edit `src/mcpserver/deployment.py`
2. Add new tool functions with `@mcp.tool()` decorator
3. Commit and push to update the server

### Dependencies

- `mcp[cli]>=1.13.1` - Model Context Protocol framework
- `fastapi>=0.116.1` - Web framework (used by FastMCP)
- `pydantic>=2.11.7` - Data validation
- `uvicorn>=0.35.0` - ASGI server

## 📄 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📞 Support

If you encounter any issues:

1. Check the troubleshooting section above
2. Review Cursor's MCP documentation
3. Open an issue on GitHub
4. Check the MCP community resources

---

**Happy coding with GTAF MCP Server!** 🎉
