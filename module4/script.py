"""
Kaggle Dataset Profiler

This script was developed with the assistance of AI (opencode/kimi-k2.5-free).
An AI assistant helped implement features including:
- Logging infrastructure with configurable levels
- Command-line argument parsing
- Iterator and generator patterns for CSV file processing
- Iterator protocol for row-wise data analysis
"""

import pandas as pd
import pathlib
import kagglehub
import logging
import argparse
import sys


def parse_args():
    parser = argparse.ArgumentParser(description="Kaggle Dataset Profiler")
    parser.add_argument(
        "-l",
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level (default: INFO)",
    )
    return parser.parse_args()


logger = logging.getLogger(__name__)  # Create logger at module level


def setup_logging(level_name: str):
    """Configure root logger with the specified level."""
    level = getattr(logging, level_name)
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler("script.log"), logging.StreamHandler()],
    )


class KaggleDataManager:
    """
    Handles downloading and loading of Kaggle datasets
    """

    def __init__(self, dataset_slug: str):
        self.dataset_slug = dataset_slug
        self.download_path: str = ""
        self.df: pd.DataFrame = pd.DataFrame()
        # We can trigger download immediately on init
        self.download()

    def download(self) -> str:
        """
        Downloads the dataset using kagglehub, returns path
        """
        # Checks if already downloaded to avoid spamming the console
        if not self.download_path:
            logger.info(f"Downloading dataset: {self.dataset_slug}")
            self.download_path = kagglehub.dataset_download(self.dataset_slug)
            logger.info(f"Dataset downloaded to: {self.download_path}")
        else:
            logger.debug("Dataset already downloaded, using cached path")
        return self.download_path

    def get_csv_file(self, index=0) -> pd.DataFrame:
        """
        Helper to find .csv in dir.
        Defaults to index=0 (The FIRST file found).
        """
        search_path = pathlib.Path(self.download_path)

        # Use rglob instead of glob to find CSVs even inside subfolders
        csv_files = list(search_path.rglob("*.csv"))
        csv_files.sort()

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

    def iter_csv_files(self):
        """Generator that yields DataFrames from all CSV files lazily."""
        search_path = pathlib.Path(self.download_path)
        csv_files = sorted(search_path.rglob("*.csv"))

        logger.info(f"Starting iteration over {len(csv_files)} CSV files")

        for i, csv_file in enumerate(csv_files):
            logger.debug(f"Yielding CSV file {i + 1}/{len(csv_files)}: {csv_file.name}")
            yield pd.read_csv(csv_file)


class DataProfiler:
    """
    Handles the data and analysis
    """

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self._index = 0

    def __str__(self) -> str:
        """returns an extended stats version of self"""
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
        Calculates my favorite stats
        """
        if self.df.empty:
            logger.warning("DataFrame is empty, cannot calculate statistics")
            return pd.DataFrame()

        logger.debug(f"Calculating statistics for {len(self.df)} rows")

        # Only run stats on numeric columns to avoid errors
        numeric_df = self.df.select_dtypes(include=["number"])

        desc = numeric_df.describe()

        median = numeric_df.median()
        # Mode can return multiple rows, take the first
        mode = numeric_df.mode().iloc[0]
        range_val = numeric_df.max() - numeric_df.min()

        extra_stats = pd.DataFrame(
            {"median": median, "mode": mode, "range": range_val}
        ).T

        full_stats = pd.concat([desc, extra_stats])
        return full_stats


def main():
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
    # We use index=0 because this dataset only has 1 file.
    # If you used index=1, it would look for a 2nd file that doesn't exist.
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
