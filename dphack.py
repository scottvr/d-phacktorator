import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
import yfinance as yf
from io import StringIO
import requests

def load_sp500_data(start_date='1950-01-01', end_date='2023-12-31'):
    """Load S&P 500 data using yfinance."""
    sp500 = yf.download('^GSPC', start=start_date, end=end_date)
    return sp500['Close'].resample('M').last()

def load_sst_data():
    """Load sea surface temperature data."""
    url = "https://www.esrl.noaa.gov/psd/data/correlation/amon.us.long.data"
    sst_data = pd.read_csv(url, delim_whitespace=True, skiprows=1, na_values='-99.99')
    
    # Process the data
    sst_data['Date'] = pd.to_datetime(sst_data['YR'].astype(str) + '-' + sst_data['MON'].astype(str), format='%Y-%m')
    sst_data.set_index('Date', inplace=True)
    
    return sst_data['ANOM']

def load_climate_data():
    """Load global temperature anomalies data."""
    url = "https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv"
    response = requests.get(url)
    data = pd.read_csv(StringIO(response.text), skiprows=1, na_values='***')

    # Reshape the data so that each row represents a single month
    data = data.melt(id_vars=['Year'], var_name='Month', value_name='Temperature')
    data = data[~data['Month'].isin(['J-D', 'D-N', 'DJF', 'MAM', 'JJA', 'SON'])]  # Remove seasonal and annual means
    data['Month'] = pd.to_datetime(data['Month'], format='%b').dt.month
    data['Date'] = pd.to_datetime(data[['Year', 'Month']].assign(DAY=1))

    data.set_index('Date', inplace=True)
    data = data.sort_index()  # Ensure data is sorted by date

    return data['Temperature']


def align_and_prepare_data(sp500_data, climate_data):
    """Align the datasets and prepare for analysis."""
    common_start = max(sp500_data.index.min(), climate_data.index.min())
    common_end = min(sp500_data.index.max(), climate_data.index.max())
    
    aligned_data = pd.DataFrame({
        'SP500': sp500_data.loc[common_start:common_end],
        'Temperature': climate_data.loc[common_start:common_end]
    })
    aligned_data.dropna(inplace=True)
    return aligned_data

def calculate_returns_and_changes(data):
    """Calculate returns for S&P 500 and changes for temperature."""
    data['SP500_Return'] = data['SP500'].pct_change()
    data['Temp_Change'] = data['Temperature'].diff()
    return data.dropna()

def find_correlations(data, window_sizes=[12, 24, 36, 48, 60]):
    """Find correlations between S&P 500 returns and temperature changes."""
    correlations = []
    for window in window_sizes:
        for shift in range(-12, 13):  # Shift up to 1 year in either direction
            sp500_data = data['SP500_Return'].shift(shift)
            temp_data = data['Temp_Change'].rolling(window=window).mean()
            
            valid_data = pd.DataFrame({'SP500': sp500_data, 'Temp': temp_data}).dropna()
            if len(valid_data) > window:
                r, p = stats.pearsonr(valid_data['SP500'], valid_data['Temp'])
                correlations.append((window, shift, r, p))
    
    return pd.DataFrame(correlations, columns=['Window', 'Shift', 'Correlation', 'P-value'])

def plot_data(data):
    """Plot the S&P 500 prices and temperature anomalies."""
    fig, ax1 = plt.subplots(figsize=(12, 6))

    ax1.set_xlabel('Year')
    ax1.set_ylabel('S&P 500 Price', color='tab:blue')
    ax1.plot(data.index, data['SP500'], color='tab:blue', label='S&P 500')
    ax1.tick_params(axis='y', labelcolor='tab:blue')

    ax2 = ax1.twinx()
    ax2.set_ylabel('Temperature Anomaly (°C)', color='tab:red')
    ax2.plot(data.index, data['Temperature'], color='tab:red', label='Temperature Anomaly')
    ax2.tick_params(axis='y', labelcolor='tab:red')

    plt.title('S&P 500 vs Global Temperature Anomalies')
    fig.tight_layout()
    plt.legend(loc='upper left')
    plt.show()

def main():
#    sp500_data = load_sp500_data()
    sst_data = load_sst_data()
    climate_data = load_climate_data()
    
    aligned_data = align_and_prepare_data(sst_data, climate_data)
    processed_data = calculate_returns_and_changes(aligned_data)
    
    correlations = find_correlations(processed_data)
    
    print("Top 5 'most significant' correlations:")
    print(correlations.sort_values('P-value').head())
    
    plot_data(aligned_data)

if __name__ == "__main__":
    main()
