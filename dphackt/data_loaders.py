import pandas as pd
from abc import ABC, abstractmethod

class DataLoader(ABC):
    @abstractmethod
    def load(self, file_path, date_column, value_column):
        pass

class CSVLoader(DataLoader):
    def load(self, file_path, date_column, value_column):
        df = pd.read_csv(file_path, parse_dates=[date_column])
        df.set_index(date_column, inplace=True)
        return df[[value_column]]

class JSONLoader(DataLoader):
    def load(self, file_path, date_column, value_column):
        df = pd.read_json(file_path)
        df.set_index(date_column, inplace=True)
        return df[[value_column]]

class ParquetLoader(DataLoader):
    def load(self, file_path, date_column, value_column):
        df = pd.read_parquet(file_path)
        df.set_index(date_column, inplace=True)
        return df[[value_column]]

