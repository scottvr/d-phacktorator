# d-phacktorator (and the dphackt lib)
the dataset p-hacking fact-creator and phony correlation generator (and choose-your-own-letter-arrangement acronym) project.

I will properly write up the motivation, purpose, and functionality of the tool eventually. 

Until such time as I do, maybe see [this guy's site](https://www.tylervigen.com/spurious-correlations) for inspiration. 

# dphackt
I've tried to abstract and genericize the support methods into their own library, after considering that they might be of value to someone doing something else. It's possible this is an inadvertent incremental reinvinting of the wheel of course, since it isn't the product of a well-planned utility, rather it came about when I wanted to generate my own spurious correlations using arbitrary datasets.

```python
from data_analysis_library import DatasetManager, CorrelationAnalysis

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

For more detailed see the D-phacktorator demo in its subdirectory.
