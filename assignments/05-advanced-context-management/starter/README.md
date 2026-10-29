# Data Explorer — Custom MCP Server

A robust Model Context Protocol (MCP) server built with `FastMCP` that wraps the open, no-key **[mledoze/countries](https://github.com/mledoze/countries)** dataset and exposes structured geographic data tools to AI agents over standard I/O (STDIO).

> **Data Source Note**: REST Countries retired its free v3.1 API in October 2026. This server fetches the open `mledoze/countries` dataset directly from GitHub (cached in memory after the first fetch), preserving realistic HTTPS failure modes (timeouts, network errors, malformed responses).

---

## Table of Contents
- [Overview](#overview)
- [Prerequisites & Installation](#prerequisites--installation)
- [Running the Server](#running-the-server)
- [Registering in MCP Clients](#registering-in-mcp-clients)
  - [Claude Desktop](#1-claude-desktop)
  - [Cursor / VS Code (MCP Extension)](#2-cursor--vs-code)
  - [Antigravity / Gemini Agents](#3-antigravity--gemini-agents)
- [Tool Reference](#tool-reference)
  - [`search_countries`](#1-search_countries)
  - [`get_country_details`](#2-get_country_details)
- [Error Handling Strategy](#error-handling-strategy)
- [Running Automated Tests](#running-automated-tests)

---

## Overview

Large Language Model agents need structured interfaces to external data. This server provides two core capabilities:
1. Fast, high-level country discovery (`search_countries`) with essential summary attributes.
2. Deep-dive entity retrieval (`get_country_details`) returning currencies, languages, neighboring land borders, and official flag vector graphics.

All tools communicate over standard STDIO transport and enforce defensive input validation and exception containment so the server process never crashes.

---

## Prerequisites & Installation

- Python 3.10 or higher
- `pip`

Clone or open the repository folder and install dependencies:

```bash
cd starter
pip install -r requirements.txt
```

Dependencies (`requirements.txt`):
- `mcp<2`: Model Context Protocol Python SDK (`FastMCP` 1.x API)
- `httpx`: High-performance HTTP client with timeout and connection management

---

## Running the Server

Run directly over STDIO:

```bash
python server.py
```

The server listens on standard input/output. It prints nothing and waits for an MCP client to initiate the JSON-RPC handshake; that is normal.

---

## Registering in MCP Clients

### 1. Claude Desktop
Add the server entry to your Claude Desktop configuration file:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "data-explorer": {
      "command": "python",
      "args": [
        "C:\\Users\\maste\\OneDrive\\Desktop\\python\\AI-Augmented-Software-Engineering\\assignments\\05-advanced-context-management\\starter\\server.py"
      ]
    }
  }
}
```

### 2. Cursor / VS Code
In your project or workspace `.cursor/mcp.json` (or VS Code MCP configuration):

```json
{
  "mcpServers": {
    "data-explorer": {
      "command": "python",
      "args": [
        "assignments/05-advanced-context-management/starter/server.py"
      ]
    }
  }
}
```

### 3. Antigravity / Gemini Agents
In your Antigravity agent configuration or `mcp_servers` configuration:

```json
{
  "mcp_servers": {
    "data-explorer": {
      "command": "python",
      "args": [
        "assignments/05-advanced-context-management/starter/server.py"
      ]
    }
  }
}
```

---

## Tool Reference

### 1. `search_countries`
Searches countries matching a given query string against common and official names and returns a model-friendly summary list.

- **Parameters**:
  - `query` (`string`, required): Search string (common or partial country name).
  - `limit` (`integer`, optional, default: `5`): Maximum number of results returned (must be $\ge 1$).

- **Example Invocation**:
  ```json
  {
    "query": "france",
    "limit": 1
  }
  ```

- **Example Output**:
  ```json
  [
    {
      "name": "France",
      "capital": "Paris",
      "region": "Europe",
      "subregion": "Western Europe"
    }
  ]
  ```

- **No Match Output**:
  Returns an empty list `[]` when no countries match the query (no error thrown).

---

### 2. `get_country_details`
Retrieves comprehensive details for a specific country, including currencies, official languages, border countries (cca3 codes), and the official flag SVG URL.

- **Parameters**:
  - `name` (`string`, required): Country name (e.g., `"Germany"`, `"Japan"`, `"Saudi Arabia"`).

- **Example Invocation**:
  ```json
  {
    "name": "Japan"
  }
  ```

- **Example Output**:
  ```json
  {
    "name": "Japan",
    "official_name": "Japan",
    "capital": "Tokyo",
    "region": "Asia",
    "subregion": "Eastern Asia",
    "currencies": [
      {
        "code": "JPY",
        "name": "Japanese Yen",
        "symbol": "¥"
      }
    ],
    "languages": [
      "Japanese"
    ],
    "borders": [],
    "flag_url": "https://raw.githubusercontent.com/mledoze/countries/master/data/jpn.svg"
  }
  ```

---

## Error Handling Strategy

The server is built with defensive programming patterns so that upstream issues, missing data, or bad inputs never cause unhandled exceptions:

1. **Input Validation**: Empty strings or non-string inputs return an explicit structured error object immediately without running queries:
   ```json
   {"error": "country name must not be empty"}
   ```
2. **Missing Entities**:
   - For `search_countries`: returns `[]` (empty list), allowing the model to recognize that zero matches were found.
   - For `get_country_details`: returns `{"error": "country '<name>' not found"}`.
3. **Network Timeouts**:
   - `httpx.TimeoutException` is trapped and returns a structured timeout explanation instead of crashing.
4. **Upstream HTTP Status Errors**:
   - Upstream 5xx or unexpected 4xx codes return `{"error": "upstream service returned error (HTTP <status>)"}`.
5. **Exact Match with Substring Fallback**:
   - `get_country_details` checks for an exact name match first (case-insensitive on common or official names), and falls back gracefully to substring matching if needed.

---

## Running Automated Tests

A comprehensive suite of unit tests covers both normal execution and edge cases (empty inputs, 404s, timeouts, 502/500 errors, island countries with no borders):

```bash
python test_server.py
```
