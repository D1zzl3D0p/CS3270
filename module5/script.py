"""
Kaggle Dataset Profiler

This script was developed with the assistance of AI (opencode/kimi-k2.5-free).
An AI assistant helped implement features including:
- Logging infrastructure with configurable levels
- Command-line argument parsing
- Iterator and generator patterns for CSV file processing
- Iterator protocol for row-wise data analysis
- Comprehensive test suite using pytest
- Doctest examples for documentation and testing

Examples:
    >>> # Test parse_args with empty list returns INFO level
    >>> args = parse_args([])
    >>> args.log_level
    'INFO'

    >>> # Test parse_args with DEBUG flag
    >>> args = parse_args(['-l', 'DEBUG'])
    >>> args.log_level
    'DEBUG'
"""

import pandas as pd
import pathlib
import logging
import argparse
import sys
from typing import Optional, Generator


logger = logging.getLogger(__name__)


def parse_args(args: Optional[list] = None):
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Kaggle Dataset Profiler")
    parser.add_argument(
        "-l",
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level (default: INFO)",
    )
    return parser.parse_args(args)


def setup_logging(level_name: str, log_file: str = "script.log"):
    """Configure root logger with the specified level.

    Args:
        level_name: Logging level as string (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (default: "script.log")

    Examples:
        >>> import logging
        >>> import tempfile
        >>> import os
        >>> # Setup logging with DEBUG level
        >>> with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
        ...     log_path = f.name
        >>> setup_logging("DEBUG", log_path)
        >>> logger = logging.getLogger()
        >>> logger.level == logging.DEBUG
        True
        >>> # Cleanup
        >>> import os
        >>> os.remove(log_path)
    """
    level = getattr(logging, level_name)
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
        force=True,
    )


class KaggleDataManager:
    """
    Handles downloading and loading of Kaggle datasets.

    This class can work with or without actual Kaggle downloads.
    For testing, you can set download_path directly to bypass kagglehub.

    Examples:
        >>> # Create a manager without auto-download
        >>> manager = KaggleDataManager("test/slug", auto_download=False)
        >>> manager.dataset_slug
        'test/slug'
        >>> manager.download_path
        ''

        >>> # Test with mocked download function
        >>> mock_download = lambda x: "/fake/path"
        >>> manager = KaggleDataManager("test/slug", auto_download=True, download_func=mock_download)
        >>> manager.download_path
        '/fake/path'
    """

    def __init__(
        self, dataset_slug: str, auto_download: bool = True, download_func=None
    ):
        self.dataset_slug = dataset_slug
        self.download_path: str = ""
        self._download_func = download_func
        if auto_download:
            self.download()

    def download(self) -> str:
        """
        Downloads the dataset using kagglehub, returns path.
        Can be bypassed by setting download_path directly for testing.
        """
        if not self.download_path:
            if self._download_func:
                # Use injected function (for testing)
                self.download_path = self._download_func(self.dataset_slug)
            else:
                # Import here to allow testing without kagglehub installed
                import kagglehub

                logger.info(f"Downloading dataset: {self.dataset_slug}")
                self.download_path = kagglehub.dataset_download(self.dataset_slug)
                logger.info(f"Dataset downloaded to: {self.download_path}")
        else:
            logger.debug("Dataset already downloaded, using cached path")
        return self.download_path

    def get_csv_file(self, index: int = 0) -> pd.DataFrame:
        """
        Helper to find .csv in dir.
        Defaults to index=0 (The FIRST file found).

        Args:
            index: Index of CSV file to load (default: 0)

        Returns:
            DataFrame containing the CSV data, or empty DataFrame if not found

        Examples:
            >>> import tempfile
            >>> import pandas as pd
            >>> from pathlib import Path
            >>> # Create test CSV file
            >>> with tempfile.TemporaryDirectory() as tmpdir:
            ...     csv_path = Path(tmpdir) / "data.csv"
            ...     df = pd.DataFrame({"col": [1, 2, 3]})
            ...     df.to_csv(csv_path, index=False)
            ...     manager = KaggleDataManager("test", auto_download=False)
            ...     manager.download_path = tmpdir
            ...     result = manager.get_csv_file(0)
            ...     len(result)
            3
            >>> # Verify column data
            >>> with tempfile.TemporaryDirectory() as tmpdir:
            ...     csv_path = Path(tmpdir) / "data.csv"
            ...     df = pd.DataFrame({"col": [1, 2, 3]})
            ...     df.to_csv(csv_path, index=False)
            ...     manager = KaggleDataManager("test", auto_download=False)
            ...     manager.download_path = tmpdir
            ...     result = manager.get_csv_file(0)
            ...     list(result['col'])
            [1, 2, 3]
        """
        if not self.download_path:
            logger.error("Download path not set. Call download() first.")
            return pd.DataFrame()

        search_path = pathlib.Path(self.download_path)
        csv_files = sorted(search_path.rglob("*.csv"))

        logger.debug(f"Found {len(csv_files)} CSV files: {[f.name for f in csv_files]}")

        if len(csv_files) <= index:
            logger.error(
                f"Requested file index {index} (file #{index + 1}), but only {len(csv_files)} files exist."
            )
            return pd.DataFrame()

        target_file = csv_files[index]
        logger.info(f"Loading CSV file: {target_file.name}")
        return pd.read_csv(target_file)

    def __iter__(self):
        """Iterator protocol: yields each CSV file in the dataset."""
        return self.iter_csv_files()

    def iter_csv_files(self) -> Generator[pd.DataFrame, None, None]:
        """Generator that yields DataFrames from all CSV files lazily."""
        if not self.download_path:
            logger.error("Download path not set. Call download() first.")
            return

        search_path = pathlib.Path(self.download_path)
        csv_files = sorted(search_path.rglob("*.csv"))

        logger.info(f"Starting iteration over {len(csv_files)} CSV files")

        for i, csv_file in enumerate(csv_files):
            logger.debug(f"Yielding CSV file {i + 1}/{len(csv_files)}: {csv_file.name}")
            yield pd.read_csv(csv_file)


class DataProfiler:
    """
    Handles data analysis and profiling.

    Examples:
        >>> import pandas as pd
        >>> # Create profiler with sample data
        >>> df = pd.DataFrame({"nums": [1, 2, 3, 4, 5]})
        >>> profiler = DataProfiler(df)
        >>> # Test string representation
        >>> "Extended Data Profile" in str(profiler)
        True
        >>> # Test row iteration
        >>> rows = list(profiler)
        >>> len(rows)
        5
        >>> rows[0]
        {'nums': 1}
    """

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self._index = 0

    def __str__(self) -> str:
        """Returns an extended stats version of self.

        Returns:
            String representation of the data profile

        Examples:
            >>> import pandas as pd
            >>> # Test with data
            >>> df = pd.DataFrame({"nums": [1, 2, 3, 4, 5]})
            >>> profiler = DataProfiler(df)
            >>> text = str(profiler)
            >>> "Extended Data Profile" in text
            True
            >>> # Test with empty DataFrame
            >>> empty = DataProfiler(pd.DataFrame())
            >>> str(empty)
            'No Data to Profile'
        """
        if self.df.empty:
            return "No Data to Profile"

        stats = self.fav_stats()
        return f"\n--- Extended Data Profile ---\n{stats}"

    def __iter__(self):
        """Make DataProfiler iterable - returns self as iterator."""
        self._index = 0
        return self

    def __next__(self):
        """Return the next row as a dictionary."""
        if self.df.empty or self._index >= len(self.df):
            raise StopIteration

        row = self.df.iloc[self._index].to_dict()
        self._index += 1
        return row

    def fav_stats(self) -> pd.DataFrame:
        """
        Calculates favorite statistics including median, mode, and range.

        Returns:
            DataFrame with statistics (count, mean, std, min, 25%, 50%, 75%, max,
            plus custom stats: median, mode, range)

        Examples:
            >>> import pandas as pd
            >>> import numpy as np
            >>> # Test with simple numeric data
            >>> df = pd.DataFrame({"nums": [1, 2, 3, 4, 5]})
            >>> profiler = DataProfiler(df)
            >>> stats = profiler.fav_stats()
            >>> "median" in stats.index
            True
            >>> "mode" in stats.index
            True
            >>> "range" in stats.index
            True
            >>> float(stats.loc["median", "nums"])
            3.0
            >>> float(stats.loc["range", "nums"])
            4.0
            >>> # Test empty DataFrame
            >>> empty_profiler = DataProfiler(pd.DataFrame())
            >>> empty_profiler.fav_stats().empty
            True
            >>> # Test with no numeric columns
            >>> str_profiler = DataProfiler(pd.DataFrame({"text": ["a", "b", "c"]}))
            >>> str_profiler.fav_stats().empty
            True
        """
        if self.df.empty:
            logger.warning("DataFrame is empty, cannot calculate statistics")
            return pd.DataFrame()

        logger.debug(f"Calculating statistics for {len(self.df)} rows")

        # Only run stats on numeric columns to avoid errors
        numeric_df = self.df.select_dtypes(include=["number"])

        if numeric_df.empty:
            logger.warning("No numeric columns found for statistics")
            return pd.DataFrame()

        desc = numeric_df.describe()

        median = numeric_df.median()
        # Mode can return multiple rows, take the first
        mode = numeric_df.mode()
        if not mode.empty:
            mode = mode.iloc[0]
        range_val = numeric_df.max() - numeric_df.min()

        extra_stats = pd.DataFrame(
            {"median": median, "mode": mode, "range": range_val}
        ).T

        full_stats = pd.concat([desc, extra_stats])
        return full_stats


def run_doctests(verbose: bool = False) -> int:
    """Run doctests for the module.

    Args:
        verbose: If True, print detailed test output

    Returns:
        Number of test failures
    """
    import doctest
    import sys

    # Suppress logging during doctests
    logging.disable(logging.CRITICAL)

    # Run doctests
    result = doctest.testmod(
        verbose=verbose, optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE
    )

    # Re-enable logging
    logging.disable(logging.NOTSET)

    if result.failed == 0:
        print(f"All {result.attempted} doctests passed!")
    else:
        print(f"{result.failed} of {result.attempted} doctests failed.")

    return result.failed


def main():
    """Main entry point for the script."""
    # Check for doctest mode
    if len(sys.argv) > 1 and sys.argv[1] == "--doctest":
        verbose = "-v" in sys.argv or "--verbose" in sys.argv
        failures = run_doctests(verbose=verbose)
        sys.exit(0 if failures == 0 else 1)

    # Parse command-line arguments first
    args = parse_args()
    setup_logging(args.log_level)

    # Configuration
    dataset_name = "sandhyapalaniappan/rainfall-prediction-dataset-cleaned-weatheraus"

    logger.info("Starting data processing pipeline")

    # 1. Initialize the Data Manager (automatically downloads)
    logger.debug("Initializing KaggleDataManager")
    manager = KaggleDataManager(dataset_name)

    # 2. Get the CSV
    df = manager.get_csv_file(index=0)

    # 3. Analyze Data
    if not df.empty:
        logger.info(
            f"Data loaded successfully: {df.shape[0]} rows, {df.shape[1]} columns"
        )
        profiler = DataProfiler(df)
        print(profiler)
        logger.info("Data profiling completed successfully")
    else:
        logger.warning("No data available for profiling")


if __name__ == "__main__":
    main()
