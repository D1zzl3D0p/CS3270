# Weather Data Analyzer

A Python application for downloading, analyzing, and visualizing Australian weather data using functional programming principles.

## Overview

This application downloads a rainfall prediction dataset from Kaggle, filters it for interesting observations (tropical location with significant rainfall or humidity), transforms the data by computing derived fields, and generates visualizations using Seaborn.

## Features

### 1. Data Acquisition
- **Kaggle Integration**: Uses kagglehub to download datasets
- **CSV Discovery**: Recursively finds CSV files in dataset directories

### 2. Data Processing (Functional Approach)
- **Filtering**: Extracts records matching specific criteria (location + weather conditions)
- **Transformation**: Computes derived fields (temperature range, comfort score)
- **Pipeline**: Clean separation of data acquisition, filtering, transformation, and visualization

### 3. Visualization
- **Seaborn Integration**: Creates publication-quality plots
- **Dual Charts**: Scatter plot (humidity vs rainfall) and box plot (temperature range by rain prediction)

### 4. Logging
- **Configurable Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Dual Output**: Console and file (`script.log`)

## Installation

```bash
pip install pandas numpy kagglehub seaborn matplotlib
```

## Usage

```bash
# Run with default INFO logging
python script.py

# Run with DEBUG logging for detailed output
python script.py -l DEBUG
```

### Filtering Criteria

The script filters for:
- **Location**: Cairns (tropical Australia)
- **Conditions**: Rainfall > 5mm OR Humidity3pm > 80%

### Transformation Fields

- **TempRange**: MaxTemp - MinTemp (daily temperature swing)
- **ComfortScore**: 100 - |Humidity3pm - 50| - |Temp3pm - 22| (higher is more comfortable)

### Visualization

Two plots are generated in `weather_analysis.png`:
1. Scatter plot: Humidity at 3pm vs Rainfall (colored by RainToday)
2. Box plot: Temperature Range by Rain Tomorrow prediction

## Architecture

```
script.py
├── parse_args()           # Command-line argument parsing
├── setup_logging()        # Logging configuration
├── get_dataset_path()     # Download/retrieve dataset
├── load_csv_data()        # Load CSV file into DataFrame
├── _is_interesting_record()   # Filter predicate
├── filter_interesting_data()   # Filter records
├── _compute_comfort()     # Transform single record
├── transform_data()       # Transform all records
├── visualize_weather()    # Generate Seaborn plots
└── main()                 # Pipeline orchestration
```

## Dependencies

- **pandas**: Data manipulation
- **numpy**: Numerical operations
- **kagglehub**: Dataset downloading
- **seaborn**: Statistical visualization
- **matplotlib**: Plotting backend

## Development

### AI Assistance

This project was developed with the assistance of AI:
- Initial development: google/gemini-2.0-flash-exp (gemini-3-flash)
- Refactoring and enhancements: opencode (minimax-m2.5-free)

## Notes

- The script uses pure functions with no side effects for filtering and transformation
- Data is converted to list of dictionaries for functional processing, then back to DataFrame for visualization
- The dataset contains Australian weather observations with rainfall predictions
