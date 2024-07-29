import os
import hashlib
import json
import pandas as pd
import numpy as np
from scipy import stats
from itertools import combinations
from concurrent.futures import ProcessPoolExecutor

class FlexibleDatasetManager:
    def __init__(self, data_dir, cache_dir):
        self.data_dir = data_dir
        self.cache_dir = cache_dir
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
                self.dataset_metadata[dataset_hash] = {
                    'name': filename,
                    'path': path,
                }

    def compute_hash(self, file_path):
        return hashlib.md5(open(file_path, 'rb').read()).hexdigest()

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

    def add_dataset(self, file_path, date_column, value_column):
        dataset_hash = self.compute_hash(file_path)
        self.dataset_configs[dataset_hash] = {
            'path': file_path,
            'date_column': date_column,
            'value_column': value_column
        }
        # Update metadata
        self.dataset_metadata[dataset_hash].update({
            'date_column': date_column,
            'value_column': value_column
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

    def find_correlations(self, threshold=0.7):
        results = []
        dataset_pairs = list(combinations(self.dataset_configs.keys(), 2))
        
        def process_pair(pair):
            h1, h2 = pair
            cache_key = f"{h1}_{h2}"
            if cache_key in self.correlation_cache:
                return self.correlation_cache[cache_key]
            
            corr = self.compute_correlation(h1, h2)
            if corr is not None and abs(corr) >= threshold:
                result = {
                    'dataset1': self.dataset_metadata[h1]['name'],
                    'dataset2': self.dataset_metadata[h2]['name'],
                    'correlation': corr
                }
                self.correlation_cache[cache_key] = result
                return result
            return None

        with ProcessPoolExecutor() as executor:
            for result in executor.map(process_pair, dataset_pairs):
                if result:
                    results.append(result)

        self.save_cache()
        return results

def main():
    data_dir = 'data_directory'  # Replace with actual data directory path
    cache_dir = 'cache_directory'  # Replace with actual cache directory path
    
    manager = FlexibleDatasetManager(data_dir, cache_dir)
    
    # Add datasets (replace with actual dataset file names and column names)
    manager.add_dataset('temperature.csv', 'date', 'temp_celsius')
    manager.add_dataset('stock_prices.csv', 'timestamp', 'closing_price')
    manager.add_dataset('social_media_trends.json', 'date', 'trend_score')
    # Add more datasets as needed...

    correlations = manager.find_correlations(threshold=0.7)
    
    print("Spurious correlations found:")
    for corr in correlations:
        print(f"High correlation found between {corr['dataset1']} and {corr['dataset2']}: {corr['correlation']:.2f}")

if __name__ == "__main__":
    main()
