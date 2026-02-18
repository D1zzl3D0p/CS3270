# Overview

In this assignment, we were asked to create two classes to help implement an OOP
workflow. I implemented them as a KaggleDataManager, an object that abstracts
away the downloading and reading/loading of the data, and DataProfiler, an
object that really only exists for the purpose of this assignment, maybe a
better use of the object would be to extend the pd.DataFrame class, but I
figured I'd implement that later

## Week 4 Changes

This week, the following features were added to the script:

### 1. Generators and Iterators
- **KaggleDataManager** now implements the iterator protocol (`__iter__`) and provides a `iter_csv_files()` generator for lazy loading of multiple CSV files
- **DataProfiler** implements the iterator protocol (`__iter__` and `__next__`) allowing row-by-row iteration over the DataFrame

### 2. Error Handling
- Added robust error handling for file index out-of-bounds in `get_csv_file()`
- Added checks for empty DataFrames with appropriate warning messages
- Command-line argument validation for log levels

### 3. Logging
- Added comprehensive logging throughout the script using Python's `logging` module
- Configurable log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL) via command-line flag (`-l` or `--log-level`)
- Logs are written to both console and `script.log` file
- All print statements converted to appropriate log levels

### Usage
```bash
# Run with default INFO logging
python script.py

# Run with DEBUG logging for detailed output
python script.py -l DEBUG

# Iterate through all CSV files
for df in manager:
    print(f"Processing {df.shape}")

# Iterate through DataFrame rows
for row in profiler:
    print(row)
```
