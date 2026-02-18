"""
Comprehensive test suite for the Kaggle Dataset Profiler script.

Uses pytest fixtures and mocking to test functionality without
requiring actual Kaggle downloads or external dependencies.
"""

import pytest
import pandas as pd
import numpy as np
import logging
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import shutil

# Import the module under test
import script


class TestParseArgs:
    """Test cases for the parse_args function."""

    def test_default_log_level(self):
        """Test that default log level is INFO."""
        args = script.parse_args([])
        assert args.log_level == "INFO"

    def test_custom_log_level(self):
        """Test that custom log levels are parsed correctly."""
        for level in ["DEBUG", "WARNING", "ERROR", "CRITICAL"]:
            args = script.parse_args(["-l", level])
            assert args.log_level == level

            args = script.parse_args(["--log-level", level])
            assert args.log_level == level

    def test_invalid_log_level(self):
        """Test that invalid log levels raise an error."""
        with pytest.raises(SystemExit):
            script.parse_args(["-l", "INVALID"])


class TestSetupLogging:
    """Test cases for the setup_logging function."""

    def test_setup_logging_creates_handlers(self, tmp_path):
        """Test that logging setup creates file and stream handlers."""
        log_file = tmp_path / "test.log"
        script.setup_logging("DEBUG", str(log_file))

        root_logger = logging.getLogger()
        assert root_logger.level == logging.DEBUG

        # Check that handlers were added
        handler_types = [type(h) for h in root_logger.handlers]
        assert logging.FileHandler in handler_types
        assert logging.StreamHandler in handler_types

        # Cleanup
        root_logger.handlers = []

    def test_setup_logging_different_levels(self, tmp_path):
        """Test that different log levels are set correctly."""
        log_file = tmp_path / "test.log"

        for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            script.setup_logging(level, str(log_file))
            root_logger = logging.getLogger()
            assert root_logger.level == getattr(logging, level)
            root_logger.handlers = []


class TestKaggleDataManager:
    """Test cases for the KaggleDataManager class."""

    def test_init_without_auto_download(self):
        """Test that initialization without auto_download doesn't call download."""
        manager = script.KaggleDataManager("test/slug", auto_download=False)
        assert manager.dataset_slug == "test/slug"
        assert manager.download_path == ""

    def test_init_with_auto_download(self):
        """Test that initialization with auto_download calls download."""
        mock_download = Mock(return_value="/fake/path")
        manager = script.KaggleDataManager(
            "test/slug", auto_download=True, download_func=mock_download
        )
        assert manager.download_path == "/fake/path"
        mock_download.assert_called_once_with("test/slug")

    def test_download_with_injected_function(self):
        """Test download using injected function."""
        mock_download = Mock(return_value="/fake/path")
        manager = script.KaggleDataManager(
            "test/slug", auto_download=False, download_func=mock_download
        )

        result = manager.download()
        assert result == "/fake/path"
        mock_download.assert_called_once_with("test/slug")

    def test_download_caches_result(self):
        """Test that download caches the path after first call."""
        mock_download = Mock(return_value="/fake/path")
        manager = script.KaggleDataManager(
            "test/slug", auto_download=False, download_func=mock_download
        )

        manager.download()
        manager.download()  # Second call
        mock_download.assert_called_once()  # Should only be called once

    def test_get_csv_file_no_download_path(self, caplog):
        """Test get_csv_file when download path is not set."""
        manager = script.KaggleDataManager("test/slug", auto_download=False)

        with caplog.at_level(logging.ERROR):
            result = manager.get_csv_file(index=0)

        assert result.empty
        assert "Download path not set" in caplog.text

    def test_get_csv_file_with_no_files(self, tmp_path, caplog):
        """Test get_csv_file when no CSV files exist."""
        manager = script.KaggleDataManager("test/slug", auto_download=False)
        manager.download_path = str(tmp_path)

        with caplog.at_level(logging.ERROR):
            result = manager.get_csv_file(index=0)

        assert result.empty
        assert "only 0 files exist" in caplog.text

    def test_get_csv_file_index_out_of_bounds(self, tmp_path, caplog):
        """Test get_csv_file with index out of bounds."""
        # Create a CSV file
        csv_file = tmp_path / "data.csv"
        df = pd.DataFrame({"col1": [1, 2, 3]})
        df.to_csv(csv_file, index=False)

        manager = script.KaggleDataManager("test/slug", auto_download=False)
        manager.download_path = str(tmp_path)

        with caplog.at_level(logging.ERROR):
            result = manager.get_csv_file(index=5)

        assert result.empty
        assert "only 1 files exist" in caplog.text

    def test_get_csv_file_success(self, tmp_path):
        """Test successful CSV file loading."""
        # Create a CSV file
        csv_file = tmp_path / "data.csv"
        expected_df = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})
        expected_df.to_csv(csv_file, index=False)

        manager = script.KaggleDataManager("test/slug", auto_download=False)
        manager.download_path = str(tmp_path)

        result = manager.get_csv_file(index=0)

        assert not result.empty
        pd.testing.assert_frame_equal(result, expected_df)

    def test_iter_csv_files(self, tmp_path):
        """Test iteration over multiple CSV files."""
        # Create multiple CSV files
        for i in range(3):
            csv_file = tmp_path / f"data{i}.csv"
            df = pd.DataFrame({"col": [i]})
            df.to_csv(csv_file, index=False)

        manager = script.KaggleDataManager("test/slug", auto_download=False)
        manager.download_path = str(tmp_path)

        results = list(manager.iter_csv_files())
        assert len(results) == 3

    def test_iter_protocol(self, tmp_path):
        """Test that KaggleDataManager works as an iterator."""
        # Create CSV files
        for i in range(2):
            csv_file = tmp_path / f"data{i}.csv"
            df = pd.DataFrame({"col": [i]})
            df.to_csv(csv_file, index=False)

        manager = script.KaggleDataManager("test/slug", auto_download=False)
        manager.download_path = str(tmp_path)

        results = list(manager)  # Using __iter__
        assert len(results) == 2

    def test_iter_csv_files_no_download_path(self, caplog):
        """Test iter_csv_files when download path is not set."""
        manager = script.KaggleDataManager("test/slug", auto_download=False)

        with caplog.at_level(logging.ERROR):
            results = list(manager.iter_csv_files())

        assert len(results) == 0
        assert "Download path not set" in caplog.text


class TestDataProfiler:
    """Test cases for the DataProfiler class."""

    def test_init(self):
        """Test DataProfiler initialization."""
        df = pd.DataFrame({"a": [1, 2, 3]})
        profiler = script.DataProfiler(df)
        assert profiler._index == 0
        pd.testing.assert_frame_equal(profiler.df, df)

    def test_str_empty_dataframe(self):
        """Test __str__ with empty DataFrame."""
        profiler = script.DataProfiler(pd.DataFrame())
        assert str(profiler) == "No Data to Profile"

    def test_str_non_empty_dataframe(self):
        """Test __str__ with non-empty DataFrame."""
        df = pd.DataFrame({"num": [1, 2, 3, 4, 5]})
        profiler = script.DataProfiler(df)
        result = str(profiler)
        assert "Extended Data Profile" in result

    def test_iteration(self):
        """Test row-by-row iteration."""
        df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
        profiler = script.DataProfiler(df)

        rows = list(profiler)
        assert len(rows) == 3
        assert rows[0] == {"a": 1, "b": "x"}
        assert rows[1] == {"a": 2, "b": "y"}
        assert rows[2] == {"a": 3, "b": "z"}

    def test_iteration_empty(self):
        """Test iteration with empty DataFrame."""
        profiler = script.DataProfiler(pd.DataFrame())
        rows = list(profiler)
        assert len(rows) == 0

    def test_iteration_reset(self):
        """Test that iteration resets properly."""
        df = pd.DataFrame({"a": [1, 2]})
        profiler = script.DataProfiler(df)

        # First iteration
        rows1 = list(profiler)
        assert len(rows1) == 2

        # Second iteration (should reset)
        rows2 = list(profiler)
        assert len(rows2) == 2

    def test_fav_stats_empty(self, caplog):
        """Test fav_stats with empty DataFrame."""
        profiler = script.DataProfiler(pd.DataFrame())

        with caplog.at_level(logging.WARNING):
            result = profiler.fav_stats()

        assert result.empty
        assert "DataFrame is empty" in caplog.text

    def test_fav_stats_no_numeric(self, caplog):
        """Test fav_stats with no numeric columns."""
        df = pd.DataFrame({"str_col": ["a", "b", "c"]})
        profiler = script.DataProfiler(df)

        with caplog.at_level(logging.WARNING):
            result = profiler.fav_stats()

        assert result.empty
        assert "No numeric columns found" in caplog.text

    def test_fav_stats_basic(self):
        """Test fav_stats with basic numeric data."""
        df = pd.DataFrame({"nums": [1, 2, 3, 4, 5]})
        profiler = script.DataProfiler(df)
        result = profiler.fav_stats()

        assert not result.empty
        assert "median" in result.index
        assert "mode" in result.index
        assert "range" in result.index
        assert result.loc["median", "nums"] == 3
        assert result.loc["range", "nums"] == 4

    def test_fav_stats_multiple_columns(self):
        """Test fav_stats with multiple numeric columns."""
        df = pd.DataFrame({"col1": [1, 2, 3, 4, 5], "col2": [10, 20, 30, 40, 50]})
        profiler = script.DataProfiler(df)
        result = profiler.fav_stats()

        assert not result.empty
        assert "col1" in result.columns
        assert "col2" in result.columns
        assert result.loc["median", "col1"] == 3
        assert result.loc["median", "col2"] == 30

    def test_fav_stats_mixed_types(self):
        """Test fav_stats with mixed column types."""
        df = pd.DataFrame({"numeric": [1, 2, 3], "string": ["a", "b", "c"]})
        profiler = script.DataProfiler(df)
        result = profiler.fav_stats()

        # Should only include numeric column
        assert "numeric" in result.columns
        assert "string" not in result.columns


class TestMain:
    """Test cases for the main function."""

    @patch("script.KaggleDataManager")
    @patch("script.setup_logging")
    @patch("script.parse_args")
    def test_main_successful_run(
        self, mock_parse_args, mock_setup_logging, mock_manager_class, caplog
    ):
        """Test main function with successful data processing."""
        # Setup mocks
        mock_args = Mock()
        mock_args.log_level = "INFO"
        mock_parse_args.return_value = mock_args

        # Mock the manager and DataFrame
        mock_df = pd.DataFrame({"col": [1, 2, 3]})
        mock_manager = Mock()
        mock_manager.get_csv_file.return_value = mock_df
        mock_manager_class.return_value = mock_manager

        with caplog.at_level(logging.INFO):
            script.main()

        # Verify calls
        mock_parse_args.assert_called_once()
        mock_setup_logging.assert_called_once_with("INFO")
        mock_manager_class.assert_called_once()
        mock_manager.get_csv_file.assert_called_once_with(index=0)
        assert "Data loaded successfully" in caplog.text

    @patch("script.KaggleDataManager")
    @patch("script.setup_logging")
    @patch("script.parse_args")
    def test_main_empty_dataframe(
        self, mock_parse_args, mock_setup_logging, mock_manager_class, caplog
    ):
        """Test main function with empty DataFrame."""
        mock_args = Mock()
        mock_args.log_level = "INFO"
        mock_parse_args.return_value = mock_args

        mock_manager = Mock()
        mock_manager.get_csv_file.return_value = pd.DataFrame()
        mock_manager_class.return_value = mock_manager

        with caplog.at_level(logging.WARNING):
            script.main()

        assert "No data available for profiling" in caplog.text


class TestIntegration:
    """Integration tests combining multiple components."""

    def test_full_pipeline(self, tmp_path):
        """Test the full pipeline with real file operations."""
        # Create test data
        data_dir = tmp_path / "dataset"
        data_dir.mkdir()
        csv_file = data_dir / "test_data.csv"

        df = pd.DataFrame(
            {"temperature": [20, 25, 30, 35, 40], "rainfall": [0, 5, 10, 15, 20]}
        )
        df.to_csv(csv_file, index=False)

        # Test KaggleDataManager
        manager = script.KaggleDataManager("test/slug", auto_download=False)
        manager.download_path = str(data_dir)

        loaded_df = manager.get_csv_file(index=0)
        assert not loaded_df.empty

        # Test DataProfiler
        profiler = script.DataProfiler(loaded_df)
        stats = profiler.fav_stats()

        assert not stats.empty
        assert "median" in stats.index
        assert "temperature" in stats.columns
        assert "rainfall" in stats.columns

    def test_multiple_csv_iteration(self, tmp_path):
        """Test iteration over multiple CSV files."""
        data_dir = tmp_path / "dataset"
        data_dir.mkdir()

        # Create multiple CSV files
        for i in range(3):
            csv_file = data_dir / f"data_{i}.csv"
            df = pd.DataFrame({"value": [i * 10, i * 10 + 1]})
            df.to_csv(csv_file, index=False)

        manager = script.KaggleDataManager("test/slug", auto_download=False)
        manager.download_path = str(data_dir)

        all_data = []
        for df in manager:
            all_data.append(df)

        assert len(all_data) == 3
        assert all_data[0]["value"].iloc[0] == 0
        assert all_data[1]["value"].iloc[0] == 10
        assert all_data[2]["value"].iloc[0] == 20


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
