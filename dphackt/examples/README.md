# d-phacktorator 
the dataset p-hacking fact-creator and phony correlation generator (and choose-your-own-letter-arrangement acronym) project.

### Examples
This subdirectory contains example config and datasets for use with the dphackt-cli command

### Example Usage
dphackt-cli \
          --data_dir data \
          --cache_dir cache \
          --output_dir out \
          --window_size 30 \
          --threshold 0.7 \
          --date_column_map date_column_map.json \
          [--plot]
```