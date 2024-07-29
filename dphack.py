import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
import requests
from io import StringIO

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

def load_sst_data():
    """Load sea surface temperature data."""
    url = "https://psl.noaa.gov/data/correlation/amon.us.long.data"
    
    # Read the data, skip initial metadata row
    sst_data = pd.read_csv(url, delim_whitespace=True, skiprows=1, header=None, na_values='-99.99')
    
    # Assign proper column names
    col_names = ['Year'] + [f'Month_{i+1}' for i in range(12)]
    sst_data.columns = col_names
    
    # Filter out rows that are footnotes or contain metadata by keeping only numeric 'Year' rows
    sst_data = sst_data[pd.to_numeric(sst_data['Year'], errors='coerce').notnull()]
    
    # Convert all columns to numeric, forcing errors to NaN
    sst_data = sst_data.apply(pd.to_numeric, errors='coerce')
    
    # Drop rows with any NaN values
    sst_data.dropna(inplace=True)
    
    # Convert the data to a long format
    sst_data_long = sst_data.melt(id_vars=['Year'], var_name='Month', value_name='SST')
    sst_data_long['Month'] = sst_data_long['Month'].apply(lambda x: int(x.split('_')[1]))
    
    # Create a 'Date' column
    sst_data_long['Date'] = pd.to_datetime(sst_data_long[['Year', 'Month']].assign(DAY=1))
    
    # Set 'Date' as index and drop rows with NaN values
    sst_data_long.set_index('Date', inplace=True)
    sst_data_long.dropna(inplace=True)
    
    return sst_data_long['SST']

def calculate_changes(data, value_column):
    """Calculate changes for a given value column."""
    data['Change'] = data[value_column].diff()
    
    # Remove NaNs and Infs
    data.replace([np.inf, -np.inf], np.nan, inplace=True)
    data.dropna(subset=['Change'], inplace=True)
    
    return data

def find_correlations(data, value_col1, value_col2, window_sizes=[12, 24, 36, 48, 60]):
    """Find correlations between two columns of data."""
    correlations = []
    for window in window_sizes:
        for shift in range(-12, 13):  # Shift up to 1 year in either direction
            col1_data = data[value_col1].shift(shift)
            col2_data = data[value_col2].rolling(window=window).mean()
            
            valid_data = pd.DataFrame({value_col1: col1_data, value_col2: col2_data}).dropna()
            if len(valid_data) > window:
                try:
                    r, p = stats.pearsonr(valid_data[value_col1], valid_data[value_col2])
                    correlations.append((window, shift, r, p))
                except ValueError:
                    continue
    
    return pd.DataFrame(correlations, columns=['Window', 'Shift', 'Correlation', 'P-value'])

def align_and_prepare_data(sst_data, climate_data):
    """Align the datasets and prepare for analysis."""
    common_start = max(sst_data.index.min(), climate_data.index.min())
    common_end = min(sst_data.index.max(), climate_data.index.max())
    
    aligned_data = pd.DataFrame({
        'SST': sst_data.loc[common_start:common_end],
        'Temperature': climate_data.loc[common_start:common_end]
    })
    aligned_data.dropna(inplace=True)
    return aligned_data

def plot_data(data, value_col1, value_col2, significant_corrs=None):
    """Plot two columns of data against each other with annotations for significant correlations."""
    fig, ax1 = plt.subplots(figsize=(12, 6))

    ax1.set_xlabel('Date')
    ax1.set_ylabel(value_col1, color='tab:blue')
    ax1.plot(data.index, data[value_col1], color='tab:blue', label=value_col1)
    ax1.tick_params(axis='y', labelcolor='tab:blue')

    ax2 = ax1.twinx()
    ax2.set_ylabel(value_col2, color='tab:red')
    ax2.plot(data.index, data[value_col2], color='tab:red', label=value_col2)
    ax2.tick_params(axis='y', labelcolor='tab:red')

    plt.title(f'{value_col1} vs {value_col2}')
    fig.tight_layout()

    # Create a legend
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, loc='upper left')

    # Annotate significant correlations
    if significant_corrs is not None:
        for _, row in significant_corrs.iterrows():
            shift = row['Shift']
            # Calculate the index position for the x_loc, ensuring it is an integer
            idx_pos = int(len(data) / 2) + shift
            if 0 <= idx_pos < len(data):  # Check if the index position is valid
                x_loc = data.index[idx_pos]
                plt.axvline(x=x_loc, color='yellow', linestyle='--', label=f'Correlation: {row["Correlation"]:.2f}')
    
    # Display plot
    plt.show()


def main():
    sst_data = load_sst_data()
    climate_data = load_climate_data()
    
    aligned_data = align_and_prepare_data(sst_data, climate_data)
    processed_data = calculate_changes(aligned_data, 'SST')
    
    correlations = find_correlations(processed_data, 'SST', 'Temperature')
    
    print("Top 5 'most significant' correlations:")
    print(correlations.sort_values('P-value').head())
    
    plot_data(aligned_data, 'SST', 'Temperature', correlations.sort_values('P-value').head())

if __name__ == "__main__":
    main()
