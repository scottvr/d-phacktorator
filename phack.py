import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

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


import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy import stats

def plot_data(data, value_col1, value_col2, significant_corrs=None):
    """Plot two columns of data against each other with annotations for significant correlations."""
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Plot the first dataset
    ax1.set_xlabel('Date')
    ax1.set_ylabel(value_col1, color='tab:blue')
    ax1.plot(data.index, data[value_col1], color='tab:blue', label=value_col1)
    ax1.tick_params(axis='y', labelcolor='tab:blue')

    # Create a second y-axis to plot the second dataset
    ax2 = ax1.twinx()
    ax2.set_ylabel(value_col2, color='tab:red')
    ax2.plot(data.index, data[value_col2], color='tab:red', label=value_col2)
    ax2.tick_params(axis='y', labelcolor='tab:red')

    # Title and layout
    plt.title(f'{value_col1} vs {value_col2}')
    fig.tight_layout()
    
    # Create a legend
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, loc='upper left')

    # Add significant correlations if provided
    if significant_corrs is not None:
        for _, row in significant_corrs.iterrows():
            window = row['Window']
            shift = row['Shift']
            correlation = row['Correlation']
            p_value = row['P-value']

            # Calculate the start and end indices of the correlation window
            start_idx = data.index.min() + pd.DateOffset(months=shift)
            end_idx = start_idx + pd.DateOffset(months=window)
            
            if start_idx < data.index.max() and end_idx <= data.index.max():
                # Use a marker for the start of the window
                ax1.axvline(start_idx, color='orange', linestyle='--', label=f'Corr Start: {correlation:.2f}' if not plt.gca().get_legend_handles_labels()[1] else "")
                
                # Add a shaded region for the window
                ax1.axvspan(start_idx, end_idx, color='yellow', alpha=0.3, label=f'Window: {window}, Shift: {shift}' if not plt.gca().get_legend_handles_labels()[1] else "")
                
                # Add text annotation
                ax1.text(start_idx, data[value_col1].max(), f'Corr: {correlation:.2f}\nP: {p_value:.3f}', 
                         color='black', fontsize=8, ha='left', va='top')

    plt.show()

def main():
    # Example data loading and processing
    sst_data = load_sst_data()
    aligned_data = sst_data.to_frame().rename(columns={'SST': 'Temperature'})
    processed_data = calculate_changes(aligned_data, 'Temperature')
    
    correlations = find_correlations(processed_data, 'Temperature', 'Change')
    
    print("Top 5 'most significant' correlations:")
    top_correlations = correlations.sort_values('P-value').head()
    print(top_correlations)
    
    plot_data(aligned_data, 'Temperature', 'Change', significant_corrs=top_correlations)

if __name__ == "__main__":
    main()
