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
            # Read the spr.opt file, assuming space-separated values
            self.data = pd.read_csv(self.file_path, delim_whitespace=True)
            print("File read successfully. Columns found:", self.data.columns.tolist())
        except Exception as e:
            print(f"Error reading file: {e}")
            return False
        return True

    def sort_data(self):
        # Sort data by day, segment, and layer
        self.data = self.data.sort_values(['JDAY', 'SEG', 'LAYER'])

    def calculate_tsi(self):
        # Calculate Trophic State Index (TSI) based on chlorophyll-a
        # Assuming 'CHLA' is the column for chlorophyll-a in μg/L
        if 'CHLA' in self.data.columns:
            self.data['TSI'] = 9.81 * np.log(self.data['CHLA']) + 30.6
        else:
            print("Warning: CHLA column not found. TSI calculation skipped.")

    def identify_layers(self):
        # Identify hypolimnion, thermocline, and epilimnion layers
        # This is a simplified version and may need adjustment
        self.data['LAYER_TYPE'] = pd.cut(
            self.data['TEMP'],
            bins=[-np.inf, 15, 20, np.inf],
            labels=['HYPOLIMNION', 'THERMOCLINE', 'EPILIMNION']
        )

    def calculate_oxygen_content(self):
        # Calculate average oxygen content for hypolimnion and epilimnion
        oxygen_content = self.data.groupby(['JDAY', 'LAYER_TYPE'])['DO'].mean().unstack()
        self.data = self.data.merge(oxygen_content, on='JDAY', suffixes=('', '_AVG'))

    def calculate_ic(self):
        # Calculate Chemical Stratification Index (IC)
        self.ic_series = self.data.groupby('JDAY').apply(
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

        self.sort_data()
        self.calculate_tsi()
        self.identify_layers()
        self.calculate_oxygen_content()
        self.calculate_ic()
        self.plot_ic()

        # Save results
        self.ic_series.to_csv('IC_time_series.csv')
        print("Analysis complete. Results saved to IC_time_series.csv and IC_time_series.png")

# Usage
file_path = 'path_to_your_spr_opt_file.opt'  # Replace with your actual file path
analyzer = WaterQualityAnalyzer(file_path)
analyzer.run_analysis()
