import pandas as pd
import pathlib
import kagglehub


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
            self.download_path = kagglehub.dataset_download(self.dataset_slug)
            print(f"Dataset downloaded to: {self.download_path}")
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

        # Debugging: Print what we found
        print(f"Found {len(csv_files)} CSV files: {[f.name for f in csv_files]}")

        if len(csv_files) <= index:
            print(
                f"Error: You asked for file index {index} (file #{index + 1}), but only {len(csv_files)} files exist."
            )
            return pd.DataFrame()

        target_file = csv_files[index]
        print(f"Loading: {target_file.name}")
        return pd.read_csv(target_file)


class DataProfiler:
    """
    Handles the data and analysis
    """

    def __init__(self, df: pd.DataFrame):
        self.df = df

    def __str__(self) -> str:
        """returns an extended stats version of self"""
        if self.df.empty:
            return "No Data to Profile"

        stats = self.fav_stats()
        return f"\n--- Extended Data Profile ---\n{stats}"

    def fav_stats(self) -> pd.DataFrame:
        """
        Calculates my favorite stats
        """
        if self.df.empty:
            return pd.DataFrame()

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
    # Configuration
    dataset_name = "sandhyapalaniappan/rainfall-prediction-dataset-cleaned-weatheraus"

    # 1. Initialize the Data Manager (automatically downloads)
    manager = KaggleDataManager(dataset_name)

    # 2. Get the CSV
    # We use index=0 because this dataset only has 1 file.
    # If you used index=1, it would look for a 2nd file that doesn't exist.
    df = manager.get_csv_file(index=0)

    # 3. Analyze Data
    if not df.empty:
        profiler = DataProfiler(df)
        print(profiler)


if __name__ == "__main__":
    main()
