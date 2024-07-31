from abc import ABC, abstractmethod
import pandas as pd

class AnalysisTask(ABC):
    @abstractmethod
    def process(self, dataset_manager, dataset_pair):
        pass

class CorrelationAnalysis(AnalysisTask):
    def __init__(self, window_size=30, threshold=0.7):
        self.window_size = window_size
        self.threshold = threshold

    def process(self, dataset_manager, dataset_pair):
        hash1, hash2 = dataset_pair
        df1 = dataset_manager.load_dataset(hash1)
        df2 = dataset_manager.load_dataset(hash2)

        aligned_data = pd.concat([df1, df2], axis=1, join='inner')
        if len(aligned_data) < self.window_size:
            return None

        rolling_corr = aligned_data.rolling(window=self.window_size).corr().iloc[self.window_size-1::2]
        max_corr = rolling_corr.max().iloc[0]

        if abs(max_corr) >= self.threshold:
            return {
                'dataset1': dataset_manager.datasets[hash1]['name'],
                'dataset2': dataset_manager.datasets[hash2]['name'],
                'correlation': max_corr
            }
        return None