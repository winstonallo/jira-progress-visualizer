import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import os
import sys

class GanttChart:

    def __init__(self, path : str) -> None:
        self.path = path
        self.df = None
    
    def load_data(self):
        self.df = pd.read_csv(self.path)
        self.df['Custom field (Start)'] = pd.to_datetime(self.df['Custom field (Start)'], errors='coerce').dt.date
        self.df['Due Date'] = pd.to_datetime(self.df['Due Date'], errors='coerce').dt.date
        self.df.dropna(subset=['Due Date', 'Custom field (Start)'], inplace=True)
        self.df.sort_values('Custom field (Start)', inplace=True)

    def generate_gantt_chart(self, output_path : str):
        fig, ax = plt.subplots(figsize=(10, 5))
        colors = plt.cm.viridis(np.linspace(0, 1, len(self.df)))
        bar_height = 0.9

        for i, (_, row) in enumerate(self.df.iterrows()):
            duration = (row['Due Date'] - row['Custom field (Start)']).days
            ax.barh(i, duration, left=mdates.date2num(row['Custom field (Start)']), height=bar_height, color=colors[i])
        
        ax.set_yticks(range(len(self.df)))
        ax.set_yticklabels(self.df['Summary'], fontsize=8)
        plt.yticks(rotation=0)

        self.format_axes(ax)

        deadline = pd.to_datetime('2025-01-01')
        plt.axvline(x=mdates.date2num(deadline), color='red', linestyle='-')
        plt.savefig(output_path, dpi=300)

    def format_axes(self, ax):
        ax.xaxis.grid(True, linestyle='--', which='major', color='grey', alpha=.25)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        plt.xticks(fontsize=8, rotation=70)
        plt.tight_layout()

    def save_plot(self):
        if self.df is not None:
            trimmed_name = os.path.splitext(self.path)[0]
            self.generate_gantt_chart(f"{trimmed_name}.png")
        else:
            print("data not loaded - call load_data() before saving plot")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        chart = GanttChart(sys.argv[1])
        chart.load_data()
        chart.save_plot()
    else:
        print("please provide a csv file")
        sys.exit(1)

