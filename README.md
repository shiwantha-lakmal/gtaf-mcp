# Generic Test Automation MCP Server

A comprehensive Model Context Protocol (MCP) server for test automation frameworks, providing AI-powered access to test results, failure analysis, and knowledge database management.

## 🚀 Features

- **Dynamic Project Selection**: Access test data from any project using partial name matching
- **Intelligent Failure Analysis**: Process and analyze test failures with AI-optimized summaries
- **Knowledge Database**: Persistent storage and retrieval of test failure patterns and analysis
- **LLM-Optimized Responses**: Token-efficient outputs designed for AI consumption
- **Real-time Test Results**: Access to latest test execution reports and metrics

## 📋 Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Available Tools](#available-tools)
- [Usage Examples](#usage-examples)
- [API Reference](#api-reference)
- [Knowledge Database](#knowledge-database)
- [Development](#development)
- [Troubleshooting](#troubleshooting)

## 🔧 Installation

### Prerequisites

- Python 3.12 or higher
- Access to testing platform API endpoints
- Valid API keys for Ordino services

### Install from Source

```bash
git clone <repository-url>
cd gtaf-mcp
pip install -e .
```

### Install via UV

```bash
uvx --from git+https://github.com/your-org/gtaf-mcp.git mcp-server
```

## ⚙️ Configuration

### MCP Configuration

Add to your MCP client configuration (e.g., `~/.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "gtaf-mcp": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/your-org/gtaf-mcp.git", "mcp-server"],
      "env": {
        "ORDINO_CLI_API_KEY": "your-cli-api-key",
        "ORDINO_SYSTEM_API_KEY": "your-system-api-key"
      }
    }
  }
}
```

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `ORDINO_CLI_API_KEY` | API key for project and failure data access | Yes |
| `ORDINO_SYSTEM_API_KEY` | API key for test report analysis | Yes |

## 🛠️ Available Tools

### 1. Mathematical Operations

#### `add(digit1: int, digit2: int) -> int`

Performs mathematical addition of two integers.

**Parameters:**
- `digit1`: First integer operand
- `digit2`: Second integer operand

**Example:**
```json
{
  "tool": "add",
  "parameters": {
    "digit1": 5,
    "digit2": 3
  }
}
```

**Response:**
```json
8
```

---

### 2. Project Management

#### `get_projects(mode: str = "summary") -> str`

Get all active projects from testing platform.

**Parameters:**
- `mode`: Detail level (`"summary"` or `"full"`)
  - `"summary"`: Returns only ID and name (default)
  - `"full"`: Returns extended technical details

**Example:**
```json
{
  "tool": "get_projects",
  "parameters": {
    "mode": "summary"
  }
}
```

**Response:**
```json
[
  {
    "id": "23173222-4ecd-4b1c-8024-b83523f4572b",
    "name": "web-portal-app"
  },
  {
    "id": "b4d4abee-6eab-48f1-b92c-55ce73fedc9c", 
    "name": "ui-integration-platform"
  },
  {
    "id": "0a180944-8df0-4fc5-9f38-98a36bfda85c",
    "name": "reporting-service"
  }
]
```

---

### 3. Failure Analysis

#### `get_failures_by_project(project_name: str, mode: str = "summary") -> str`

Get test failure details for a specific project by name.

**Parameters:**
- `project_name`: Project name or partial name (e.g., "portal", "reporting")
- `mode`: Detail level (`"summary"` or `"full"`)
  - `"summary"`: Essential failure info to understand situation
  - `"full"`: Detailed root cause analysis with complete stack traces

**Examples:**

**Summary Mode:**
```json
{
  "tool": "get_failures_by_project",
  "parameters": {
    "project_name": "portal",
    "mode": "summary"
  }
}
```

**Response:**
```json
{
  "matched_project": "web-portal-app",
  "total_failures": 5,
  "success": false,
  "failures": [
    {
      "test_case": "Login Flow Test",
      "status": "failed",
      "error": "Element not found: #login-button",
      "file_path": "tests/auth/login.spec.js",
      "failed_step": "Click login button",
      "occurrence_count": 3,
      "is_recurring": true
    }
  ]
}
```

**Full Mode:**
```json
{
  "tool": "get_failures_by_project", 
  "parameters": {
    "project_name": "reporting",
    "mode": "full"
  }
}
```

---

### 4. Knowledge Database

#### `get_knowledge_db_documents(partial_testcase_name: str) -> str`

Fetch documents from knowledge database using partial test case name matching.

**Parameters:**
- `partial_testcase_name`: Partial or full test case name to search for

**Example:**
```json
{
  "tool": "get_knowledge_db_documents",
  "parameters": {
    "partial_testcase_name": "Login"
  }
}
```

**Response:**
```json
{
  "search_term": "Login",
  "matched_documents": [
    {
      "testCase": "Login_Flow_Test_Scenario_01",
      "total_failures": 5,
      "unique_errors": 2,
      "last_updated": "2024-01-15T10:30:00Z",
      "failure_history": [
        {
          "failure_id": "abc123def456",
          "first_seen": "2024-01-10T09:00:00Z",
          "occurrence_count": 3,
          "recent_occurrences": [
            {
              "timestamp": "2024-01-15T10:30:00Z",
              "error": "Element not found: #login-button",
              "stackTrace": "...",
              "isBug": null,
              "tester_notes": []
            }
          ]
        }
      ]
    }
  ]
}
```

---

### 5. Failure Processing

#### `process_and_save_all_failures(project_name: str = "") -> str`

Fetch and save test failures to knowledge database for specific project.

**Parameters:**
- `project_name`: Project name or partial name (optional)
  - If empty: Processes all projects
  - If specified: Processes only matching project

**Examples:**

**Process Specific Project:**
```json
{
  "tool": "process_and_save_all_failures",
  "parameters": {
    "project_name": "portal"
  }
}
```

**Process All Projects:**
```json
{
  "tool": "process_and_save_all_failures",
  "parameters": {
    "project_name": ""
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Processed 15 cases",
  "projects_processed": ["web-portal-app"],
  "total_cases_saved": 15,
  "available_projects": [
    "web-portal-app",
    "ui-integration-platform", 
    "reporting-service"
  ]
}
```

---

### 6. Test Result Analysis

#### `get_latest_result_analysis(project_name: str, mode: str = "summary") -> str`

Get latest test result analysis from test report with summary and full detail modes.

**Parameters:**
- `project_name`: Project name or partial name
- `mode`: Analysis mode (`"summary"` or `"full"`)
  - `"summary"`: Key metrics and highlights (default)
  - `"full"`: Complete details with full test breakdown

**Examples:**

**Summary Analysis:**
```json
{
  "tool": "get_latest_result_analysis",
  "parameters": {
    "project_name": "ui-integration",
    "mode": "summary"
  }
}
```

**Response:**
```json
{
  "setup_id": "b4d4abee-6eab-48f1-b92c-55ce73fedc9c",
  "matched_project": "ui-integration-platform",
  "total": 82,
  "passed": 70,
  "failed": 12,
  "pass_rate": 85.4,
  "failures": [
    {
      "name": "Scenario 01: Order lifecycle statuses",
      "error": "AssertionError: Timed out retrying after 25000ms...",
      "duration": 52968
    },
    {
      "name": "Scenario 05: Delivery lifecycle statuses", 
      "error": "AssertionError: Expected to find element...",
      "duration": 53171
    },
    {
      "name": "Scenario 02: Get Store Working Mode Quiet",
      "error": "AssertionError: expected '<button.mantine...",
      "duration": 28978
    }
  ],
  "_saved_to_knowledge_db": "knowledge_db/analysis/ui_integration/test_analysis_20240115_143022.json"
}
```

---

### 7. Database Management

#### `cleanup_knowledge_database() -> str`

Fully clean knowledge database - removes all testcases, analysis files & directories.

**⚠️ WARNING:** This action is irreversible and permanently deletes all knowledge database content.

**Example:**
```json
{
  "tool": "cleanup_knowledge_database",
  "parameters": {}
}
```

**Response:**
```json
{
  "success": true,
  "testcases_removed": 45,
  "analysis_files_removed": 23,
  "analysis_dirs_removed": 8,
  "status": "completed"
}
```

## 📊 Usage Examples

### Common Workflows

#### 1. Analyze Project Health

```bash
# Get project overview
get_projects(mode="summary")

# Analyze specific project's latest results
get_latest_result_analysis(project_name="portal", mode="summary")

# Get detailed failure information
get_failures_by_project(project_name="portal", mode="full")
```

#### 2. Process and Store Failures

```bash
# Process failures for specific project
process_and_save_all_failures(project_name="reporting")

# Process all projects
process_and_save_all_failures(project_name="")

# Search historical failures
get_knowledge_db_documents(partial_testcase_name="Login")
```

#### 3. Maintenance Operations

```bash
# Clean up old data
cleanup_knowledge_database()

# Re-process current failures
process_and_save_all_failures(project_name="")
```

## 🗃️ Knowledge Database

The system maintains a persistent knowledge database that stores:

### Structure

```
knowledge_db/
├── testcases/           # Individual test case failure histories
│   ├── Test_Case_Name_1.json
│   └── Test_Case_Name_2.json
└── analysis/            # Project-specific analysis results
    ├── project_name_1/
    │   └── test_analysis_YYYYMMDD_HHMMSS.json
    └── project_name_2/
        └── test_analysis_YYYYMMDD_HHMMSS.json
```

### Data Types

#### Test Case Records
- Failure history and occurrence counts
- Error patterns and stack traces
- Bug classification status
- Tester notes and analysis

#### Analysis Records
- Test execution summaries
- Pass/fail rates and metrics
- Failure highlights and patterns
- Historical trend data

## 🔍 API Reference

### Project Selection

All project-aware tools support flexible project selection:

- **Exact Match**: `"web-portal-app"`
- **Partial Match**: `"portal"`, `"reporting"`, `"integration"`
- **Case Insensitive**: `"PORTAL"`, `"Portal"`, `"portal"`

### Response Formats

#### Success Response
```json
{
  "success": true,
  "data": { ... },
  "metadata": { ... }
}
```

#### Error Response  
```json
{
  "success": false,
  "error": "Error description",
  "available_projects": [...],
  "suggestion": "Use exact or partial project names from the list above"
}
```

### LLM Optimization Features

- **Token Efficiency**: Responses optimized for minimal token usage
- **Semantic Metadata**: Keyword arrays for better AI understanding
- **Structured Data**: Consistent JSON schemas across all tools
- **Failure Limits**: Top 3 failures shown to reduce token consumption
- **Truncated Messages**: Long error messages condensed to essential information

## 🚦 Development

### Running Locally

```bash
# Install dependencies
uv sync

# Run MCP server
uv run mcp-server

# Run in development mode
mcp dev src/mcpserver/service.py
```

### Testing

```bash
# Run basic functionality tests
python -c "
import sys; sys.path.insert(0, 'src')
from mcpserver.service import *
print('✅ All imports successful')
"

# Test specific tool
python -c "
import sys; sys.path.insert(0, 'src')
from mcpserver.service import get_projects
result = get_projects('summary')
print(result)
"
```

### Project Structure

```
gtaf-mcp/
├── src/
│   └── mcpserver/
│       ├── __init__.py
│       ├── __main__.py          # Entry point
│       ├── service.py           # MCP tools definitions
│       └── facade/
│           ├── __init__.py
│           ├── result_client.py # API client
│           └── knowledge_db.py  # Database operations
├── knowledge_db/                # Persistent data storage
│   ├── testcases/
│   └── analysis/
├── pyproject.toml              # Project configuration
├── mcp.json                    # Local MCP configuration
└── README.md                   # This file
```

## 🐛 Troubleshooting

### Common Issues

#### 1. API Authentication Errors

**Problem**: `401 Unauthorized` responses

**Solution**: 
- Verify API keys are set correctly in environment variables
- Check key validity and permissions
- Ensure proper MCP configuration

```bash
# Check environment variables
echo $ORDINO_CLI_API_KEY
echo $ORDINO_SYSTEM_API_KEY
```

#### 2. Project Not Found

**Problem**: `Project 'name' not found` errors

**Solution**:
- Use `get_projects()` to see available projects
- Try partial matching (e.g., "portal" instead of full name)
- Check project name spelling and case sensitivity

#### 3. Knowledge Database Issues

**Problem**: Database corruption or access errors

**Solution**:
- Run `cleanup_knowledge_database()` to reset
- Check file system permissions
- Verify disk space availability

#### 4. Performance Issues

**Problem**: Slow responses or timeouts

**Solution**:
- Use `"summary"` mode instead of `"full"` for faster responses
- Process specific projects instead of all projects
- Check network connectivity to API endpoints

### Debug Mode

Enable verbose logging by setting environment variable:

```bash
export MCP_DEBUG=1
mcp dev src/mcpserver/service.py
```

## 📄 License

[Add your license information here]

## 🤝 Contributing

[Add contribution guidelines here]

## 📞 Support

[Add support contact information here]

---

**Built with ❤️ for Ordino Test Automation**
