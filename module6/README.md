# Kaggle Dataset Profiler

A Python application for downloading, loading, and analyzing Kaggle datasets with comprehensive logging and iterator support. This project includes a full test suite using pytest.

## Overview

This application consists of two main classes:

- **KaggleDataManager**: Handles downloading and loading of Kaggle datasets
- **DataProfiler**: Provides statistical analysis of DataFrames with row-by-row iteration

## Features

### 1. Data Management
- **Automatic Dataset Downloading**: Uses kagglehub to download datasets
- **CSV File Discovery**: Recursively finds CSV files in dataset directories
- **Lazy Loading**: Generator-based iteration over multiple CSV files
- **Caching**: Prevents redundant downloads

### 2. Data Profiling
- **Statistical Analysis**: Calculates count, mean, std, min, max, median, mode, and range
- **Row Iteration**: Implements Python iterator protocol for row-by-row access
- **Type Safety**: Automatically filters to numeric columns for statistics
- **Error Handling**: Graceful handling of empty DataFrames and missing files

### 3. Logging Infrastructure
- **Configurable Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Dual Output**: Logs to both console and file (`script.log`)
- **Timestamped Entries**: All log entries include timestamps
- **Command-line Control**: Set log level via `-l` or `--log-level` flag

### 4. Iterator Protocols
- **KaggleDataManager**: Implements `__iter__` to yield DataFrames from CSV files
- **DataProfiler**: Implements `__iter__` and `__next__` for row-by-row iteration

## Installation

```bash
# Install dependencies
pip install pandas numpy kagglehub

# Or if using the provided virtual environment
source .venv/bin/activate
```

## Usage

### Basic Usage

```bash
# Run with default INFO logging
python script.py

# Run with DEBUG logging for detailed output
python script.py -l DEBUG

# Other log levels
python script.py --log-level WARNING
```

### As a Module

```python
from script import KaggleDataManager, DataProfiler

# Initialize data manager
dataset = "sandhyapalaniappan/rainfall-prediction-dataset-cleaned-weatheraus"
manager = KaggleDataManager(dataset)

# Load a CSV file
df = manager.get_csv_file(index=0)

# Analyze the data
profiler = DataProfiler(df)
print(profiler.fav_stats())

# Iterate through rows
for row in profiler:
    print(row)

# Iterate through all CSV files in dataset
for df in manager:
    print(f"Processing {df.shape[0]} rows")
```

## Testing

The project includes comprehensive testing with both pytest and doctest:

- **32 pytest tests** covering all functionality
- **52 doctests** embedded in docstrings

### Running Pytest Tests

```bash
# Run all tests
pytest test_script.py test_doctests.py

# Run with verbose output
pytest test_script.py test_doctests.py -v

# Run specific test class
pytest test_script.py::TestKaggleDataManager -v

# Run with coverage report
pytest test_script.py --cov=script --cov-report=term-missing
```

### Test Coverage

The test suite includes:

- **TestParseArgs**: Command-line argument parsing (3 tests)
- **TestSetupLogging**: Logging configuration (2 tests)
- **TestKaggleDataManager**: Data downloading and loading (9 tests)
- **TestDataProfiler**: Statistical analysis and iteration (11 tests)
- **TestMain**: Main function integration (2 tests)
- **TestIntegration**: End-to-end workflows (2 tests)

### Running Doctests

Doctests are embedded in the module docstrings and provide both documentation and testing:

```bash
# Run doctests directly from the script
python script.py --doctest

# Run doctests with verbose output
python script.py --doctest -v

# Run doctests via pytest
pytest test_doctests.py
```

### Test Features

- **Mocking**: External dependencies (kagglehub) are mocked for isolation
- **Temporary Files**: Tests use pytest's `tmp_path` fixture for file operations
- **Log Capture**: Tests verify log messages using `caplog` fixture
- **Edge Cases**: Empty DataFrames, missing files, and error conditions are tested
- **Doctests**: Executable documentation examples in docstrings

## Architecture

### KaggleDataManager

```python
class KaggleDataManager:
    def __init__(self, dataset_slug: str, auto_download: bool = True, download_func = None)
    def download(self) -> str
    def get_csv_file(self, index: int = 0) -> pd.DataFrame
    def __iter__(self) -> Generator[pd.DataFrame, None, None]
    def iter_csv_files(self) -> Generator[pd.DataFrame, None, None]
```

**Key Design Decisions:**
- Dependency injection for `download_func` enables testing without kagglehub
- `auto_download` parameter allows lazy initialization
- Generator methods provide memory-efficient iteration over large datasets
- Error handling for missing download paths and out-of-bounds indices

### DataProfiler

```python
class DataProfiler:
    def __init__(self, df: pd.DataFrame)
    def __str__(self) -> str
    def __iter__(self) -> 'DataProfiler'
    def __next__(self) -> dict
    def fav_stats(self) -> pd.DataFrame
```

**Key Design Decisions:**
- Iterator protocol allows `for row in profiler:` syntax
- Statistics filtered to numeric columns to avoid type errors
- Mode calculation handles multiple values by taking the first
- Empty DataFrame checks with appropriate warnings

## Code Structure

```
.
├── script.py          # Main application code with embedded doctests
├── test_script.py     # Comprehensive pytest test suite
├── test_doctests.py   # Doctest runner for pytest
├── script.log         # Log file (generated)
└── README.md          # This file
```

## Error Handling

The application handles various error conditions:

- **No CSV Files**: Returns empty DataFrame with error log
- **Index Out of Bounds**: Returns empty DataFrame with descriptive error
- **Empty DataFrame**: Returns appropriate message for statistics
- **No Numeric Columns**: Returns empty DataFrame with warning
- **Download Path Not Set**: Returns empty DataFrame with error log

## Logging

All operations are logged at appropriate levels:

- **DEBUG**: Detailed information for troubleshooting
- **INFO**: General operation progress (downloads, file loading)
- **WARNING**: Non-fatal issues (empty data, missing numeric columns)
- **ERROR**: Operation failures (missing files, invalid indices)

Log format: `%(asctime)s - %(levelname)s - %(message)s`

## Development

### Adding New Tests

Tests are organized by class and follow pytest conventions:

```python
class TestNewFeature:
    def test_specific_behavior(self):
        # Arrange
        input_data = ...
        
        # Act
        result = function_under_test(input_data)
        
        # Assert
        assert result == expected_value
    
    def test_edge_case(self, tmp_path):
        # Use fixtures like tmp_path for file operations
        ...
```

### Extending Functionality

To add new statistical measures to DataProfiler:

1. Add calculation to `fav_stats()` method
2. Add corresponding test in `TestDataProfiler`
3. Update documentation in this README

## Dependencies

- **pandas**: Data manipulation and analysis
- **numpy**: Numerical operations (via pandas)
- **kagglehub**: Dataset downloading
- **pytest**: Testing framework (development)

## Notes

- The script is designed to work with the Kaggle API via kagglehub
- Large datasets are handled efficiently through generators
- All file operations use pathlib for cross-platform compatibility
- The test suite mocks external dependencies for reliability

## License

This project was developed with educational purposes in mind.
