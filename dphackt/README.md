# dphackt
a flexible dataset manager and correlation finder, developed in support of d-phacktorator, the p-hacking data dredger tool.

### Features

- Supports multiple data formats: `.csv`, `.json`, `.parquet`
- Caches computed correlations for faster repeated analysis
- Plots and saves visualizations of correlated datasets
- Utilizes multiprocessing for efficient computation

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
