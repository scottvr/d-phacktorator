import os
import json
import argparse
import logging
from concurrent.futures import ProcessPoolExecutor
import matplotlib.pyplot as plt
from dphackt.dataset_manager import DatasetManager
from dphackt.analysis_tasks import CorrelationAnalysis

logging.basicConfig(level=logging.INFO)

def plot_correlation(dataset_manager, result, output_dir):
    hash1 = next(hash for hash, config in dataset_manager.datasets.items() if config['name'] == result['dataset1'])
    hash2 = next(hash for hash, config in dataset_manager.datasets.items() if config['name'] == result['dataset2'])
    
    df1 = dataset_manager.load_dataset(hash1)
    df2 = dataset_manager.load_dataset(hash2)
    
    aligned_data = pd.concat([df1, df2], axis=1, join='inner')
    
    plt.figure(figsize=(10, 5))
    plt.plot(aligned_data.index, aligned_data.iloc[:, 0], label=result['dataset1'], color='blue')
    plt.plot(aligned_data.index, aligned_data.iloc[:, 1], label=result['dataset2'], color='red')
    plt.title(f"Correlation: {result['correlation']:.2f}")
    plt.xlabel('Date')
    plt.ylabel('Values')
    plt.legend()
    plt.grid(True)
    
    output_file = os.path.join(output_dir, f"{result['dataset1']}_vs_{result['dataset2']}.png")
    plt.savefig(output_file)
    plt.close()
    logging.info(f"Saved plot to {output_file}")

def process_dataset_pair(args):
    dataset_manager, correlation_analysis, pair = args
    return correlation_analysis.process(dataset_manager, pair)

def main():
    parser = argparse.ArgumentParser(description='Spurious Correlation Demonstration')
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

    manager = DatasetManager(args.data_dir, args.cache_dir)
    
    # Add datasets
    for filename, (date_column, value_column) in date_column_map.items():
        file_path = os.path.join(args.data_dir, filename)
        if os.path.exists(file_path):
            manager.add_dataset(file_path, date_column, value_column)
    
    correlation_analysis = CorrelationAnalysis(window_size=args.window_size, threshold=args.threshold)
    
    # Process dataset pairs
    with ProcessPoolExecutor() as executor:
        results = list(executor.map(
            lambda pair: correlation_analysis.process(manager, pair),
            manager.get_dataset_pairs()
        ))
    
    correlations = [result for result in results if result]
    
    print("Spurious correlations found:")
    for corr in correlations:
        print(f"High correlation found between {corr['dataset1']} and {corr['dataset2']}: {corr['correlation']:.2f}")
        if args.plot:
            plot_correlation(manager, corr, args.output_dir)
    
    manager.clean_cache()

if __name__ == "__main__":
    main()
