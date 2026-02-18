"""
Test suite for the Weather Data Analyzer.
"""

import pytest
import pandas as pd
import logging
from unittest.mock import Mock, patch
from pathlib import Path

import script


class TestParseArgs:
    def test_default_log_level(self):
        args = script.parse_args([])
        assert args.log_level == "INFO"

    def test_custom_log_level(self):
        args = script.parse_args(["-l", "DEBUG"])
        assert args.log_level == "DEBUG"


def test_is_interesting_record():
    """Test the filtering predicate function."""
    assert script._is_interesting_record(
        {"Location": "Cairns", "Rainfall": 10.0, "Humidity3pm": 50.0}, "Cairns"
    )
    assert script._is_interesting_record(
        {"Location": "Cairns", "Rainfall": 0.0, "Humidity3pm": 90.0}, "Cairns"
    )
    assert not script._is_interesting_record(
        {"Location": "Cairns", "Rainfall": 0.0, "Humidity3pm": 50.0}, "Cairns"
    )
    assert not script._is_interesting_record(
        {"Location": "Sydney", "Rainfall": 10.0, "Humidity3pm": 90.0}, "Cairns"
    )


def test_filter_interesting_data():
    """Test the filtering logic."""
    data = [
        {"Location": "Cairns", "Rainfall": 10.0, "Humidity3pm": 50.0},
        {"Location": "Cairns", "Rainfall": 0.0, "Humidity3pm": 90.0},
        {"Location": "Cairns", "Rainfall": 0.0, "Humidity3pm": 50.0},
        {"Location": "Sydney", "Rainfall": 10.0, "Humidity3pm": 90.0},
    ]

    result = script.filter_interesting_data(data, location="Cairns")
    assert len(result) == 2
    assert all(r["Location"] == "Cairns" for r in result)


def test_compute_comfort():
    """Test the transformation logic."""
    record = {"MinTemp": 10.0, "MaxTemp": 20.0, "Humidity3pm": 50.0, "Temp3pm": 22.0}

    result = script._compute_comfort(record)
    assert result["TempRange"] == 10.0
    assert result["ComfortScore"] == 100.0


def test_transform_data():
    """Test the data transformation."""
    data = [
        {"MinTemp": 20.0, "MaxTemp": 30.0, "Humidity3pm": 50.0, "Temp3pm": 25.0},
    ]

    result = script.transform_data(data)
    assert len(result) == 1
    assert result[0]["TempRange"] == 10.0
    assert "TempRange" in result[0]
    assert "ComfortScore" in result[0]


@patch("script.parse_args")
@patch("script.get_dataset_path")
@patch("script.load_csv_data")
@patch("script.visualize_weather")
def test_main_flow(mock_viz, mock_load, mock_path, mock_parse):
    """Test the main pipeline orchestration."""
    mock_parse.return_value = Mock(log_level="INFO")
    mock_path.return_value = "/fake/path"
    mock_load.return_value = pd.DataFrame(
        [
            {
                "Date": "2021-01-01",
                "Location": "Cairns",
                "Rainfall": 10.0,
                "Humidity3pm": 50.0,
                "MinTemp": 20,
                "MaxTemp": 30,
                "Temp3pm": 25,
                "RainToday": "Yes",
                "RainTomorrow": "No",
            }
        ]
    )

    script.main()
    mock_viz.assert_called_once()


def test_load_csv_data_empty(tmp_path):
    """Test loading data from an empty directory."""
    result = script.load_csv_data(str(tmp_path))
    assert result.empty


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
