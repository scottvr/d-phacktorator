import os
import hashlib
import json
import pandas as pd
import numpy as np
from scipy import stats
from itertools import combinations
from concurrent.futures import ProcessPoolExecutor
import argparse
import logging
import matplotlib.pyplot as plt
from functools import partial

logging.basicConfig(level=logging.INFO)

class FlexibleDatasetManager:
    def __init__(self, data_dir, cache_dir, output_dir):
        self.data_dir = data_dir
        self.cache_dir = cache_dir
        self.output_dir = output_dir
        self.dataset_metadata = {}
        self.dataset_configs = {}
        self.correlation_cache = {}
        self.load_metadata()
        self.load_cache()

    def load_metadata(self):
        for filename in os.listdir(self.data_dir):
            if filename.endswith(('.csv', '.json', '.parquet')):
                path = os.path.join(self.data_dir, filename)
                dataset_hash = self.compute_hash(path)
                file_timestamp = os.path.getmtime(path)
                self.dataset_metadata[dataset_hash] = {
                    'name': filename,
                    'path': path,
                    'timestamp': file_timestamp
                }

    def compute_hash(self, file_path):
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()

    def load_cache(self):
        cache_file = os.path.join(self.cache_dir, 'correlation_cache.json')
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                self.correlation_cache = json.load(f)

    def save_cache(self):
        cache_file = os.path.join(self.cache_dir, 'correlation_cache.json')
        with open(cache_file, 'w') as f:
            json.dump(self.correlation_cache, f)

    def load_dataset(self, file_path, date_column, value_column):
        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path, parse_dates=[date_column])
            elif file_path.endswith('.json'):
                df = pd.read_json(file_path)
            elif file_path.endswith('.parquet'):
                df = pd.read_parquet(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_path}")
            df.set_index(date_column, inplace=True)
            return df[[value_column]]
        except Exception as e:
            logging.error(f"Failed to load dataset {file_path}: {e}")
            return pd.DataFrame()

    def add_dataset(self, file_path, date_column, value_column):
        dataset_hash = self.compute_hash(file_path)
        file_timestamp = os.path.getmtime(file_path)
        self.dataset_configs[dataset_hash] = {
            'path': file_path,
            'date_column': date_column,
            'value_column': value_column,
            'timestamp': file_timestamp
        }
        # Update metadata
        self.dataset_metadata[dataset_hash].update({
            'date_column': date_column,
            'value_column': value_column,
            'timestamp': file_timestamp
        })

    def compute_correlation(self, hash1, hash2, window_size=30):
        config1, config2 = self.dataset_configs[hash1], self.dataset_configs[hash2]
        df1 = self.load_dataset(config1['path'], config1['date_column'], config1['value_column'])
        df2 = self.load_dataset(config2['path'], config2['date_column'], config2['value_column'])
        
        aligned_data = pd.concat([df1, df2], axis=1, join='inner')
        if len(aligned_data) < window_size:
            return None
        
        rolling_corr = aligned_data.rolling(window=window_size).corr().iloc[window_size-1::2]
        max_corr = rolling_corr.max().iloc[0]
        return max_corr

    def plot_correlation(self, hash1, hash2, result):
        config1, config2 = self.dataset_configs[hash1], self.dataset_configs[hash2]
        df1 = self.load_dataset(config1['path'], config1['date_column'], config1['value_column'])
        df2 = self.load_dataset(config2['path'], config2['date_column'], config2['value_column'])
        
        aligned_data = pd.concat([df1, df2], axis=1, join='inner')
        
        plt.figure(figsize=(10, 5))
        plt.plot(aligned_data.index, aligned_data.iloc[:, 0], label=config1['path'], color='blue')
        plt.plot(aligned_data.index, aligned_data.iloc[:, 1], label=config2['path'], color='red')
        plt.title(f"Correlation: {result['correlation']:.2f}")
        plt.xlabel('Date')
        plt.ylabel('Values')
        plt.legend()
        plt.grid(True)
        
        output_file = os.path.join(self.output_dir, f"{result['dataset1']}_vs_{result['dataset2']}.png")
        plt.savefig(output_file)
        plt.close()
        logging.info(f"Saved plot to {output_file}")

    def update_datasets(self, date_column_map):
        for hash, metadata in self.dataset_metadata.items():
            if hash not in self.dataset_configs or self.dataset_configs[hash]['timestamp'] != metadata['timestamp']:
                # Get date_column and value_column from the map
                date_column, value_column = date_column_map.get(metadata['name'], (None, None))
                if date_column and value_column:
                    self.add_dataset(metadata['path'], date_column, value_column)

def process_pair(pair, manager, threshold, window_size, plot):
    h1, h2 = pair
    cache_key = f"{h1}_{h2}"
    if cache_key in manager.correlation_cache:
        return manager.correlation_cache[cache_key]
    
    corr = manager.compute_correlation(h1, h2, window_size=window_size)
    if corr is not None and abs(corr) >= threshold:
        result = {
            'dataset1': manager.dataset_metadata[h1]['name'],
            'dataset2': manager.dataset_metadata[h2]['name'],
            'correlation': corr
        }
        manager.correlation_cache[cache_key] = result
        if plot:
            manager.plot_correlation(h1, h2, result)
        return result
    return None


def main():
    parser = argparse.ArgumentParser(description='Flexible Dataset Manager for P-hacking demonstration')
    parser.add_argument('--data_dir', type=str, required=True, help='Directory containing the datasets')
    parser.add_argument('--cache_dir', type=str, required=True, help='Directory to store the cache')
    parser.add_argument('--output_dir', type=str, required=True, help='Directory to store the output plots')
    parser.add_argument('--window_size', type=int, default=30, help='Window size for rolling correlation')
    parser.add_argument('--threshold', type=float, default=0.7, help='Correlation threshold')
    parser.add_argument('--date_column_map', type=str, required=True, help='JSON file mapping filenames to date and value columns')
    parser.add_argument('--plot', action='store_true', help='Generate and save plots of the correlated datasets')
    args = parser.parse_args()

    with open(args.date_column_map, 'r') as f:
        date_column_map = json.load(f)

    manager = FlexibleDatasetManager(args.data_dir, args.cache_dir, args.output_dir)
    manager.update_datasets(date_column_map)
    
    dataset_pairs = list(combinations(manager.dataset_configs.keys(), 2))
    
    # Use partial to pass fixed arguments to process_pair
    process_pair_with_args = partial(process_pair, manager=manager, threshold=args.threshold, window_size=args.window_size, plot=args.plot)
    
    with ProcessPoolExecutor() as executor:
        results = list(executor.map(process_pair_with_args, dataset_pairs))
    
    correlations = [result for result in results if result]
    
    manager.save_cache()
    
    print("Spurious correlations found:")
    for corr in correlations:
        print(f"High correlation found between {corr['dataset1']} and {corr['dataset2']}: {corr['correlation']:.2f}")

if __name__ == "__main__":
    main()