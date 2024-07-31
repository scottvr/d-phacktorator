# d-phacktorator (and the dphackt lib)

## d-phacktorator 
the dataset p-hacking fact-creator and phony correlation generator (and choose-your-own-letter-arrangement acronym) project.

Disclaimer: I am not a data scientist or statistician or anything of the sort; I just find drawing correlations between ludicrous disparate things amusing. (Oh, and also there is that dangerous habit of some unscrupulous academics of "p-hacking" and the trend of papers using such data dredgery passing peer review without notice.) I will properly write up the motivation, purpose, and a more detailed explanation of the functionality eventually. The disclaimer is because I no nothing of properly selecting rolling window size or thresholds for any proper purpose other than the aforementioned amusement of seeing "proof" of relationships where none should probably be interpreted as such.

Until such time as I do, maybe see [Tyler Vigen's spurious correlation site](https://www.tylervigen.com/spurious-correlations) for inspiration. 

### Features

- Supports multiple data formats: `.csv`, `.json`, `.parquet`
- Caches computed correlations for faster repeated analysis
- Plots and saves visualizations of correlated datasets
- Utilizes multiprocessing for efficient computation

### Installation:
Clone this repo.
Install the dphackt lib as described in the next section.
(You could just move the dphackt/ subdirectory into the d-phacktorator/ subdirectory if you don't wish to install the lib to your Python environment.)

### Usage:
```
python ./d-phacktorator/dphackt.py \
          --data_dir /path/to/data \
          --cache_dir /path/to/cache \
          --output_dir /path/to/output \
          --window_size 30 \
          --threshold 0.7 \
          --date_column_map /path/to/date_column_map.json \
          [--plot]
```
Where in the above, ```data_dir``` is a directory with two or more CSV, JSON, or parquet files containing time series data, and you are wanting to find correlations with a window size of 30 days and a threshold of 0.7 between any (and all) of them.

### Arguments

- `--data_dir`: Directory containing the datasets.
- `--cache_dir`: Directory to store the cache.
- `--output_dir`: Directory to store the output plots.
- `--window_size`: Window size for rolling correlation (default: 30).
- `--threshold`: Correlation threshold for reporting (default: 0.7).
- `--date_column_map`: JSON file mapping filenames to date and value columns.
- `--plot`: Optional flag to generate and save plots of the correlated datasets.

### Date Column Map

The `date_column_map.json` should map filenames to their respective date and value columns. Example format:

```
{
  "dataset1.csv": ["date", "value"],
  "dataset2.json": ["timestamp", "value"]
}
```

### Output

The tool will output the list of detected correlations and save plots of these correlations (if the `--plot` option is used) in the specified `output_dir`.


## dphackt
I've tried to abstract and genericize the support methods into their own library, after considering that they might be of value to someone doing something else. It's possible this is an inadvertent incremental reinvinting of the wheel of course, since it isn't the product of a well-planned utility, rather it came about when I wanted to generate my own spurious correlations using arbitrary datasets.

### Usage:
```python
from dphackt import DatasetManager, CorrelationAnalysis

# Initialize DatasetManager
manager = DatasetManager("path/to/data", "path/to/cache")

# Add datasets
manager.add_dataset("dataset1.csv", "date_column", "value_column")
manager.add_dataset("dataset2.csv", "date_column", "value_column")

# Perform correlation analysis
analysis = CorrelationAnalysis(window_size=30, threshold=0.7)
results = analysis.process(manager, manager.get_dataset_pairs()[0])

print(results)
```

For more detailed usage, see the d-phacktorator demo in its subdirectory.
