import os
import hashlib
from itertools import combinations
from .data_loaders import CSVLoader, JSONLoader, ParquetLoader

class DatasetManager:
    def __init__(self, data_dir, cache_dir):
        self.data_dir = data_dir
        self.cache_dir = cache_dir
        self.datasets = {}
        self.dataset_cache = {}
        self.loaders = {
            '.csv': CSVLoader(),
            '.json': JSONLoader(),
            '.parquet': ParquetLoader()
        }

    def add_dataset(self, file_path, date_column, value_column):
        dataset_hash = self.compute_hash(file_path)
        file_timestamp = os.path.getmtime(file_path)
        self.datasets[dataset_hash] = {
            'name': os.path.basename(file_path),
            'path': file_path,
            'date_column': date_column,
            'value_column': value_column,
            'timestamp': file_timestamp
        }

    def compute_hash(self, file_path):
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()

    def load_dataset(self, dataset_hash):
        if dataset_hash not in self.dataset_cache:
            config = self.datasets[dataset_hash]
            file_extension = os.path.splitext(config['path'])[1].lower()
            loader = self.loaders.get(file_extension)
            if loader:
                self.dataset_cache[dataset_hash] = loader.load(
                    config['path'], config['date_column'], config['value_column']
                )
            else:
                raise ValueError(f"Unsupported file format: {config['path']}")
        return self.dataset_cache[dataset_hash]

    def clean_cache(self):
        current_datasets = set(self.datasets.keys())
        cached_datasets = set(self.dataset_cache.keys())
        for hash in cached_datasets - current_datasets:
            del self.dataset_cache[hash]

    def get_dataset_pairs(self):
        return list(combinations(self.datasets.keys(), 2))
