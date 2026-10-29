"""Data Explorer — MCP server for Week 5.

Wraps an open country dataset and exposes it to an agent as MCP tools over STDIO.

Data source: the open `mledoze/countries` dataset (the data REST Countries was built
on), served as one JSON file from GitHub. No API key. It is fetched over HTTPS on the
first call and cached in memory, so HTTP errors and timeouts are still real failure
modes your tools must handle.

Setup:
    pip install -r requirements.txt
Run (STDIO) — register this command in your MCP client (e.g. Claude Desktop / an IDE):
    python server.py
"""
from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

DATA_URL = "https://raw.githubusercontent.com/mledoze/countries/master/countries.json"
# Each country has a 3-letter `cca3` code; its flag lives at this URL.
FLAG_URL = "https://raw.githubusercontent.com/mledoze/countries/master/data/{cca3}.svg"

mcp = FastMCP("data-explorer")

_countries: list[dict] | None = None  # in-memory cache of the dataset


def load_countries() -> list[dict]:
    """Download the dataset once and cache it. Raises httpx.HTTPError on failure."""
    global _countries
    if _countries is None:
        resp = httpx.get(DATA_URL, timeout=30, follow_redirects=True)
        resp.raise_for_status()
        _countries = resp.json()
    return _countries


@mcp.tool()
def search_countries(query: str, limit: int = 5) -> list[dict[str, Any]]:
    """Search countries by name. Returns a list of {name, capital, region, subregion}.

    This tool is a WORKED EXAMPLE — study how it validates input, fetches the data,
    handles errors, and returns model-friendly data.
    """
    if not isinstance(query, str) or not query.strip():
        return [{"error": "query must not be empty"}]

    safe_limit = 5 if limit <= 0 else limit

    try:
        countries = load_countries()
    except httpx.TimeoutException:
        return [{"error": "upstream request timed out while downloading country dataset"}]
    except httpx.HTTPStatusError as exc:
        return [{"error": f"upstream service returned error (HTTP {exc.response.status_code})"}]
    except httpx.HTTPError as exc:
        return [{"error": f"upstream request failed: {exc}"}]
    except Exception as exc:
        return [{"error": f"unexpected error: {exc}"}]

    q = query.strip().lower()
    matches = [
        c
        for c in countries
        if isinstance(c.get("name"), dict)
        and (
            q in c["name"].get("common", "").lower()
            or q in c["name"].get("official", "").lower()
        )
    ]
    # No matches is not an error: return an empty list.
    results = []
    for c in matches[:safe_limit]:
        results.append(
            {
                "name": c.get("name", {}).get("common"),
                "capital": (c.get("capital") or [None])[0],
                "region": c.get("region"),
                "subregion": c.get("subregion"),
            }
        )
    return results


@mcp.tool()
def get_country_details(name: str) -> dict[str, Any]:
    """Get comprehensive details for a specific country by name.

    Returns currencies, languages, borders, and the flag URL.

    Args:
        name: The common or official name of the country.

    Returns:
        A dictionary containing country details or an error message.
    """
    if not isinstance(name, str) or not name.strip():
        return {"error": "country name must not be empty"}

    try:
        countries = load_countries()
    except httpx.TimeoutException:
        return {"error": "upstream request timed out while downloading country dataset"}
    except httpx.HTTPStatusError as exc:
        return {"error": f"upstream service returned error (HTTP {exc.response.status_code})"}
    except httpx.HTTPError as exc:
        return {"error": f"upstream request failed: {exc}"}
    except Exception as exc:
        return {"error": f"unexpected error: {exc}"}

    q = name.strip().lower()

    # Find exact match first (case-insensitive on common or official name)
    matched_country = None
    for c in countries:
        if not isinstance(c.get("name"), dict):
            continue
        common = c["name"].get("common", "").lower()
        official = c["name"].get("official", "").lower()
        if q == common or q == official:
            matched_country = c
            break

    # If no exact match, fallback to substring match
    if matched_country is None:
        for c in countries:
            if not isinstance(c.get("name"), dict):
                continue
            common = c["name"].get("common", "").lower()
            official = c["name"].get("official", "").lower()
            if q in common or q in official:
                matched_country = c
                break

    if matched_country is None:
        return {"error": f"country '{name.strip()}' not found"}

    c = matched_country

    # Currencies: {"EUR": {"name": "Euro", "symbol": "€"}, ...}
    currencies_raw = c.get("currencies") or {}
    currencies = [
        {
            "code": code,
            "name": info.get("name"),
            "symbol": info.get("symbol"),
        }
        for code, info in currencies_raw.items()
        if isinstance(info, dict)
    ]

    # Languages: {"deu": "German", ...}
    languages_raw = c.get("languages") or {}
    languages = list(languages_raw.values()) if isinstance(languages_raw, dict) else []

    # Borders: ["AUT", "BEL", ...] (cca3 codes of neighbours)
    borders = c.get("borders") or []

    # Flag URL: based on cca3 code (e.g., DEU -> deu.svg)
    cca3 = str(c.get("cca3", "")).lower()
    flag_url = FLAG_URL.format(cca3=cca3) if cca3 else None

    return {
        "name": c.get("name", {}).get("common"),
        "official_name": c.get("name", {}).get("official"),
        "capital": (c.get("capital") or [None])[0],
        "region": c.get("region"),
        "subregion": c.get("subregion"),
        "currencies": currencies,
        "languages": languages,
        "borders": borders,
        "flag_url": flag_url,
    }


if __name__ == "__main__":
    mcp.run()
