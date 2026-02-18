"""
Weather Data Analyzer

This script analyzes Australian weather data.

AI Assistance:
- Initial development: google/gemini-2.0-flash-exp (gemini-3-flash)
- Refactoring and enhancements: opencode (minimax-m2.5-free)
"""

import pandas as pd
import pathlib
import logging
import argparse
import sys
import seaborn as sns
import matplotlib.pyplot as plt
from typing import Optional, List, Dict, Any


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
    """Configure root logger with the specified level."""
    level = getattr(logging, level_name)
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
        force=True,
    )


def get_dataset_path(dataset_slug: str) -> str:
    """Download or retrieve the dataset path using kagglehub."""
    import kagglehub

    logger.info(f"Downloading dataset: {dataset_slug}")
    path = kagglehub.dataset_download(dataset_slug)
    logger.info(f"Dataset location: {path}")
    return path


def load_csv_data(base_path: str, index: int = 0) -> pd.DataFrame:
    """Find and load a CSV file from the given path."""
    search_path = pathlib.Path(base_path)
    csv_files = sorted(search_path.rglob("*.csv"))

    if not csv_files or len(csv_files) <= index:
        logger.error(f"CSV file at index {index} not found in {base_path}")
        return pd.DataFrame()

    target_file = csv_files[index]
    logger.info(f"Loading: {target_file.name}")
    return pd.read_csv(target_file)


def _is_interesting_record(record: Dict[str, Any], location: str) -> bool:
    """Check if a record is interesting based on location and weather conditions."""
    return str(record.get("Location")).lower() == location.lower() and (
        float(record.get("Rainfall", 0)) > 5.0
        or float(record.get("Humidity3pm", 0)) > 80.0
    )


def filter_interesting_data(
    data: List[Dict[str, Any]], location: str = "Cairns"
) -> List[Dict[str, Any]]:
    """
    Filter data to find 'interesting' observations.
    Criteria: Specific location AND significant rainfall or high humidity.
    """
    logger.info(f"Filtering data for location: {location}")
    return [r for r in data if _is_interesting_record(r, location)]


def _compute_comfort(record: Dict[str, Any]) -> Dict[str, Any]:
    """Compute derived fields for a weather record."""
    return {
        **record,
        "TempRange": float(record.get("MaxTemp", 0)) - float(record.get("MinTemp", 0)),
        "ComfortScore": 100
        - abs(float(record.get("Humidity3pm", 50)) - 50)
        - abs(float(record.get("Temp3pm", 22)) - 22),
    }


def transform_data(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Transform data by adding computed fields.
    Calculates temperature range and a simplified 'Comfort Score'.
    """
    logger.info("Transforming data records")
    return [_compute_comfort(r) for r in data]


def visualize_weather(df: pd.DataFrame, output_file: str = "weather_analysis.png"):
    """Visualize the analyzed weather data using Seaborn."""
    if df.empty:
        logger.warning("No data to visualize")
        return

    logger.info(f"Generating visualization: {output_file}")

    sns.set_theme(style="whitegrid")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    sns.scatterplot(
        data=df, x="Humidity3pm", y="Rainfall", hue="RainToday", alpha=0.6, ax=ax1
    )
    ax1.set_title("Humidity at 3pm vs Rainfall")

    sns.boxplot(
        data=df,
        x="RainTomorrow",
        y="TempRange",
        hue="RainTomorrow",
        palette="Set2",
        ax=ax2,
        legend=False,
    )
    ax2.set_title("Daily Temperature Range vs Rain Tomorrow")

    plt.tight_layout()
    plt.savefig(output_file)
    logger.info(f"Visualization saved to {output_file}")


def main():
    args = parse_args()
    setup_logging(args.log_level)

    dataset_name = "sandhyapalaniappan/rainfall-prediction-dataset-cleaned-weatheraus"

    try:
        path = get_dataset_path(dataset_name)
        df_raw = load_csv_data(path)

        if df_raw.empty:
            return

        records = df_raw.to_dict("records")
        logger.info(f"Processing {len(records)} initial records")

        filtered_records = filter_interesting_data(records, location="Cairns")
        logger.info(f"Filtered to {len(filtered_records)} interesting records")

        processed_records = transform_data(filtered_records)

        df_final = pd.DataFrame(processed_records)

        print("\n--- Weather Analysis Summary (Cairns) ---")
        print(f"Total interesting days found: {len(df_final)}")
        if not df_final.empty:
            avg_temp_range = sum(r["TempRange"] for r in processed_records) / len(
                processed_records
            )
            print(f"Average Temperature Range: {avg_temp_range:.2f}°C")
            print(
                df_final[
                    ["Date", "Location", "Rainfall", "TempRange", "ComfortScore"]
                ].head()
            )

            visualize_weather(df_final)

    except Exception as e:
        logger.exception(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
