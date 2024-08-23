import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

class WaterQualityAnalyzer:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = None
        self.ic_series = None

    def read_spr_opt(self):
        try:
            # Read the spr.opt file, assuming space-separated values and no header
            self.data = pd.read_csv(self.file_path, delim_whitespace=True, header=None)
            
            # Assign column names based on the structure we observed
            column_names = ['Julian_day', 'Depth', 'Elevation', 'Temperature', 'DO']
            self.data.columns = column_names + [f'Column_{i}' for i in range(len(self.data.columns) - len(column_names))]
            
            print("File read successfully. Columns found:", self.data.columns.tolist())
        except Exception as e:
            print(f"Error reading file: {e}")
            return False
        return True

    def clean_data(self):
        # Replace -99.00 with NaN (assuming -99.00 represents missing data)
        self.data = self.data.replace(-99.00, np.nan)
        
        # Remove rows with NaN values in critical columns
        self.data = self.data.dropna(subset=['Temperature', 'DO'])

    def sort_data(self):
        # Sort data by Julian day, Depth
        self.data = self.data.sort_values(['Julian_day', 'Depth'])

    def calculate_tsi(self):
        # Calculate Trophic State Index (TSI) based on DO
        # Note: This is a simplified version. You might need to adjust based on your specific requirements
        self.data['TSI'] = 60 - 14.41 * np.log(self.data['DO'])

    def identify_layers(self):
        # Identify hypolimnion, thermocline, and epilimnion layers
        self.data['LAYER_TYPE'] = pd.cut(
            self.data['Temperature'],
            bins=[-np.inf, 27, 28.5, np.inf],
            labels=['HYPOLIMNION', 'THERMOCLINE', 'EPILIMNION']
        )

    def calculate_oxygen_content(self):
        # Calculate average oxygen content for hypolimnion and epilimnion
        oxygen_content = self.data.groupby(['Julian_day', 'LAYER_TYPE'])['DO'].mean().unstack()
        self.data = self.data.merge(oxygen_content, on='Julian_day', suffixes=('', '_AVG'))

    def calculate_ic(self):
        # Calculate Chemical Stratification Index (IC)
        self.ic_series = self.data.groupby('Julian_day').apply(
            lambda x: x['DO'].max() - x['DO'].min()
        )

    def plot_ic(self):
        # Plot time series of IC
        plt.figure(figsize=(12, 6))
        plt.plot(self.ic_series.index, self.ic_series.values)
        plt.title('Chemical Stratification Index (IC) Time Series')
        plt.xlabel('Julian Day')
        plt.ylabel('IC')
        plt.grid(True)
        plt.savefig('IC_time_series.png')
        plt.close()

    def run_analysis(self):
        if not self.read_spr_opt():
            return

        self.clean_data()
        self.sort_data()
        self.calculate_tsi()
        self.identify_layers()
        self.calculate_oxygen_content()
        self.calculate_ic()
        self.plot_ic()

        # Save results
        self.ic_series.to_csv('IC_time_series.csv')
        print("Analysis complete. Results saved to IC_time_series.csv and IC_time_series.png")
        
        # Print some summary statistics
        print("\nSummary Statistics:")
        print(self.data.describe())
        print("\nIC Series Statistics:")
        print(self.ic_series.describe())

# Add this block to make the script executable
if __name__ == "__main__":
    file_path = input("Enter the path to your spr.opt file: ")
    analyzer = WaterQualityAnalyzer(file_path)
    analyzer.run_analysis()
