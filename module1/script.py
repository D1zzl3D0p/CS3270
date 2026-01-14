import pandas as pd
import os
import pathlib
import kagglehub
import pydoc


def download_csv(dataset: str) -> str:
    """Downlaods the given dataset from Kagglehub"""
    # Download latest version
    path = kagglehub.dataset_download(dataset)
    print("Path to dataset files:", path)

    return path


def read_csvs(path: str) -> dict:
    """Reads all the csv's of a given directory, and returns a list of dataframes"""
    res = {}
    print(os.listdir(path))
    for file in os.listdir(path):
        print(file)
        # print(path)
        # print(file)
        full_path = os.path.join(path, file)
        if pathlib.Path(full_path).suffix == ".csv":
            print("found csv file")
            res[file] = pd.read_csv(full_path)
    return res


if __name__ == "__main__":
    path = download_csv("thedevastator/weather-prediction")
    # print(os.listdir(path))
    data = read_csvs(path)
    print(data.keys())
    print(data)
    pydoc.writedoc("script")
