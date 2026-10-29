# Week 5 Reflection & Agent Transcript — Advanced Context Management

## 1. MCP Client Registration

The `data-explorer` MCP server was registered as a local STDIO subprocess in the agent's MCP configuration:

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

Upon initialization, the MCP client performs the standard handshake, discovering two exposed tools:
- `search_countries(query: str, limit: int = 5)`
- `get_country_details(name: str)`

---

## 2. Agent Interaction Transcript

Below is a transcript demonstrating an AI agent actively discovering, querying, and receiving structured context from the `data-explorer` MCP server over STDIO.

### Turn 1: High-Level Country Discovery
**User**:
> "Can you find European countries matching 'france' and tell me the capital and region?"

**Agent (calling tool)**:
```json
{
  "tool": "search_countries",
  "arguments": {
    "query": "france",
    "limit": 1
  }
}
```

**MCP Server Output**:
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

**Agent Response**:
> France was found in Western Europe. Its capital is Paris.

---

### Turn 2: Deep-Dive Retrieval (`get_country_details`)
**User**:
> "What languages are spoken in France, what currency do they use, and which countries share its borders?"

**Agent (calling tool)**:
```json
{
  "tool": "get_country_details",
  "arguments": {
    "name": "France"
  }
}
```

**MCP Server Output**:
```json
{
  "name": "France",
  "official_name": "French Republic",
  "capital": "Paris",
  "region": "Europe",
  "subregion": "Western Europe",
  "currencies": [
    {
      "code": "EUR",
      "name": "Euro",
      "symbol": "€"
    }
  ],
  "languages": [
    "French"
  ],
  "borders": [
    "AND",
    "BEL",
    "DEU",
    "ITA",
    "LUX",
    "MCO",
    "ESP",
    "CHE"
  ],
  "flag_url": "https://raw.githubusercontent.com/mledoze/countries/master/data/fra.svg"
}
```

**Agent Response**:
> France (officially the French Republic) uses the Euro (`EUR`, `€`), and its official language is French. It shares land borders with Andorra, Belgium, Germany, Italy, Luxembourg, Monaco, Spain, and Switzerland. Its national flag is accessible at `https://raw.githubusercontent.com/mledoze/countries/master/data/fra.svg`.

---

### Turn 3: Handling Missing Border Data (Island State)
**User**:
> "What are Japan's land borders, currencies, and official flag?"

**Agent (calling tool)**:
```json
{
  "tool": "get_country_details",
  "arguments": {
    "name": "Japan"
  }
}
```

**MCP Server Output**:
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

**Agent Response**:
> Japan uses the Japanese Yen (`JPY`, `¥`). Because Japan is an island nation, it has no direct land borders (`borders: []`). Its official flag can be found at `https://raw.githubusercontent.com/mledoze/countries/master/data/jpn.svg`.

---

### Turn 4: Error Handling — Empty Input Validation
**User**:
> "Search countries with an empty string."

**Agent (calling tool)**:
```json
{
  "tool": "search_countries",
  "arguments": {
    "query": "   "
  }
}
```

**MCP Server Output**:
```json
[
  {
    "error": "query must not be empty"
  }
]
```

**Agent Response**:
> The tool rejected the request because the search query cannot be empty. Please provide a valid country name.

---

### Turn 5: Error Handling — Non-Existent Entity
**User**:
> "Get the details for the country of Atlantis."

**Agent (calling tool)**:
```json
{
  "tool": "get_country_details",
  "arguments": {
    "name": "Atlantis"
  }
}
```

**MCP Server Output**:
```json
{
  "error": "country 'Atlantis' not found"
}
```

**Agent Response**:
> No country named 'Atlantis' was found in the dataset.

---

## 3. Error Handling Architecture

The server adopts a multi-tiered defensive design to guarantee that tool execution never crashes the host MCP transport:

1. **Pre-flight Input Sanitization**: Before dispatching any operations, tools check that arguments are non-empty strings. Malformed inputs immediately return deterministic error dicts, preserving compute and memory.
2. **Missing Entity & Search Miss Mapping**:
   - `search_countries`: When no countries match a search query, zero results is not an exceptional error, so the tool returns an empty list `[]` to allow the model to reason naturally about the absence of matches.
   - `get_country_details`: A failure to find a specific entity is mapped to a clean structured dictionary `{"error": "country '<name>' not found"}`.
3. **Network & Timeout Resiliency**: Network dataset calls use `httpx.get` configured with explicit 30-second timeouts. `httpx.TimeoutException`, `httpx.HTTPStatusError`, and generic `httpx.HTTPError` are caught explicitly and converted into structured error objects instead of bubbling up unhandled tracebacks.
4. **Data Normalization & Null Safety**: Country records have variable shapes (e.g. island nations lack border entries, some territories lack standard capitals, currency records are nested dictionaries). The parser uses safe `.get()` defaults and list comprehensions to produce consistent shapes (`borders: []`, `capital: None`, standardized currency lists).

---

## 4. What I Learned (Reflection)

Controlling the context an agent can reach is the single most critical factor in building reliable AI systems. Raw API datasets contain bloated JSON records with hundreds of irrelevant fields, which needlessly exhaust context windows, increase latency, and increase the likelihood of hallucination. By encapsulating external data sources within tailored MCP tools, we create an intentional semantic abstraction layer that curates only high-signal information for the model. Furthermore, designing tools that return structured error dictionaries instead of throwing unhandled exceptions gives agents the feedback they need to self-correct within the prompt loop, resulting in robust, fault-tolerant autonomous workflows.
