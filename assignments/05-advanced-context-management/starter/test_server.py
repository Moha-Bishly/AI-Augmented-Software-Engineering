"""Unit tests for Data Explorer MCP Server."""
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Ensure the directory containing server.py is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import httpx
import server


class TestDataExplorerServer(unittest.TestCase):
    def setUp(self):
        # Reset the cached countries list before each test
        server._countries = None

        self.mock_dataset = [
            {
                "name": {"common": "France", "official": "French Republic"},
                "capital": ["Paris"],
                "region": "Europe",
                "subregion": "Western Europe",
                "cca3": "FRA",
                "currencies": {"EUR": {"name": "Euro", "symbol": "€"}},
                "languages": {"fra": "French"},
                "borders": ["AND", "BEL", "DEU", "ITA", "LUX", "MCO", "ESP", "CHE"],
            },
            {
                "name": {"common": "Japan", "official": "Japan"},
                "capital": ["Tokyo"],
                "region": "Asia",
                "subregion": "Eastern Asia",
                "cca3": "JPN",
                "currencies": {"JPY": {"name": "Japanese Yen", "symbol": "¥"}},
                "languages": {"jpn": "Japanese"},
                "borders": [],
            },
        ]

    # --- search_countries tests ---

    def test_search_countries_empty_input(self):
        res = server.search_countries("")
        self.assertEqual(res, [{"error": "query must not be empty"}])

        res_spaces = server.search_countries("   ")
        self.assertEqual(res_spaces, [{"error": "query must not be empty"}])

    @patch("server.load_countries")
    def test_search_countries_success(self, mock_load):
        mock_load.return_value = self.mock_dataset

        res = server.search_countries("france", limit=1)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["name"], "France")
        self.assertEqual(res[0]["capital"], "Paris")
        self.assertEqual(res[0]["region"], "Europe")
        self.assertEqual(res[0]["subregion"], "Western Europe")

    @patch("server.load_countries")
    def test_search_countries_no_matches(self, mock_load):
        mock_load.return_value = self.mock_dataset

        res = server.search_countries("nonexistentcountryxyz")
        self.assertEqual(res, [])

    @patch("server.load_countries")
    def test_search_countries_timeout(self, mock_load):
        mock_load.side_effect = httpx.TimeoutException("Connection timed out")
        res = server.search_countries("france")
        self.assertIn("error", res[0])
        self.assertIn("timed out", res[0]["error"].lower())

    @patch("server.load_countries")
    def test_search_countries_http_error(self, mock_load):
        request = httpx.Request("GET", server.DATA_URL)
        response = httpx.Response(500, request=request)
        mock_load.side_effect = httpx.HTTPStatusError("500 Internal Error", request=request, response=response)

        res = server.search_countries("test")
        self.assertIn("error", res[0])
        self.assertIn("500", res[0]["error"])

    # --- get_country_details tests ---

    def test_get_country_details_empty_input(self):
        res = server.get_country_details("")
        self.assertEqual(res, {"error": "country name must not be empty"})

        res_spaces = server.get_country_details("   ")
        self.assertEqual(res_spaces, {"error": "country name must not be empty"})

    @patch("server.load_countries")
    def test_get_country_details_success(self, mock_load):
        mock_load.return_value = self.mock_dataset

        res = server.get_country_details("france")
        self.assertEqual(res["name"], "France")
        self.assertEqual(res["official_name"], "French Republic")
        self.assertEqual(res["capital"], "Paris")
        self.assertEqual(res["region"], "Europe")
        self.assertEqual(res["subregion"], "Western Europe")
        self.assertEqual(res["currencies"], [{"code": "EUR", "name": "Euro", "symbol": "€"}])
        self.assertEqual(res["languages"], ["French"])
        self.assertEqual(
            res["borders"],
            ["AND", "BEL", "DEU", "ITA", "LUX", "MCO", "ESP", "CHE"],
        )
        self.assertEqual(
            res["flag_url"],
            "https://raw.githubusercontent.com/mledoze/countries/master/data/fra.svg",
        )

    @patch("server.load_countries")
    def test_get_country_details_island_no_borders(self, mock_load):
        mock_load.return_value = self.mock_dataset

        res = server.get_country_details("japan")
        self.assertEqual(res["name"], "Japan")
        self.assertEqual(res["borders"], [])
        self.assertEqual(
            res["flag_url"],
            "https://raw.githubusercontent.com/mledoze/countries/master/data/jpn.svg",
        )

    @patch("server.load_countries")
    def test_get_country_details_not_found(self, mock_load):
        mock_load.return_value = self.mock_dataset

        res = server.get_country_details("fakeland")
        self.assertIn("error", res)
        self.assertIn("fakeland", res["error"])

    @patch("server.load_countries")
    def test_get_country_details_timeout(self, mock_load):
        mock_load.side_effect = httpx.TimeoutException("Connection timed out")
        res = server.get_country_details("france")
        self.assertIn("error", res)
        self.assertIn("timed out", res["error"].lower())

    @patch("server.load_countries")
    def test_get_country_details_http_error(self, mock_load):
        request = httpx.Request("GET", server.DATA_URL)
        response = httpx.Response(502, request=request)
        mock_load.side_effect = httpx.HTTPStatusError("502 Bad Gateway", request=request, response=response)

        res = server.get_country_details("test")
        self.assertIn("error", res)
        self.assertIn("502", res["error"])


if __name__ == "__main__":
    unittest.main()
