import pandas as pd
import os
import pathlib
import kagglehub
# import pydoc


def download_csv(dataset: str) -> str:
    """Downloads the given dataset from Kagglehub"""
    # Download latest version
    path = kagglehub.dataset_download(dataset)
    print("Path to dataset files:", path)

    return path


def read_csv(path: str) -> pd.DataFrame:
    """Reads all the csv's of a given directory, and returns a list of dataframes"""
    # print(os.listdir(path))
    for file in os.listdir(path):
        # print(file)
        # print(path)
        # print(file)
        full_path = os.path.join(path, file)
        if pathlib.Path(full_path).suffix == ".csv":
            # gets first csv
            # print("found csv file")
            return pd.read_csv(full_path)
    print("csv not found")
    return pd.DataFrame()


def fav_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Prints out a bunch of important stats for a df (extends pandas.describe()"""
    desc = df.describe()

    stats_data = df[desc.columns]
    median = stats_data.median()
    mode = stats_data.mode().loc[0]
    range_val = stats_data.max() - stats_data.min()

    extra_stats = pd.DataFrame({"median": median, "mode": mode, "range": range_val}).T

    full_stats = pd.concat([desc, extra_stats])

    print(full_stats)
    return full_stats


def test_functions() -> None:
    path = download_csv(
        "sandhyapalaniappan/rainfall-prediction-dataset-cleaned-weatheraus"
    )
    df = read_csv(path)
    fav_stats(df)


if __name__ == "__main__":
    # print("attempting to download")
    path = download_csv(
        "sandhyapalaniappan/rainfall-prediction-dataset-cleaned-weatheraus"
    )
    # print(os.listdir(path))
    # print("attempting to read")
    df = read_csv(path)
    # print(data.keys())
    # print(data)
    # pydoc.writedoc("script")
    fav_stats(df)
