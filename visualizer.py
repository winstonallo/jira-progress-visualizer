import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import os
import sys
import glob

STREAM_COLOR = '#5E1914'
AP_COLOR = '#C21807'

class GanttChart:

    def __init__(self, path : str, start : str, end : str) -> None:
        self.path = path
        self.start_date_field = start
        self.end_date_field = end
        self.df = None
    
    def set_color(self, i : int, row : pd.Series) -> str:
        if row['Summary'] == 'Testphase':
            return 'grey'
        elif row['Summary'] == 'Produktivsetzung':
            return 'yellow'
        elif row['Summary'] == 'Abnahme':
            return 'green'
        elif row['Issue Type'] == 'Stream' and self.path != 'streams.csv':
            return STREAM_COLOR
        elif row['Issue Type'] == 'Arbeitspaket':
            return AP_COLOR
        else:
            return self.colors[i]

    def load_data(self):
        self.df = pd.read_csv(self.path)
        self.df[self.start_date_field] = pd.to_datetime(self.df[self.start_date_field], errors='coerce').dt.date
        self.df[self.end_date_field] = pd.to_datetime(self.df[self.end_date_field], errors='coerce').dt.date
        self.df.dropna(subset=[self.end_date_field, self.start_date_field], inplace=True)
        self.df.sort_values(self.start_date_field, inplace=True, ascending=False)

    def generate_gantt_chart(self, output_path : str):
        fig, ax = plt.subplots(figsize=(10, 5))
        self.colors = plt.cm.viridis(np.linspace(0, 1, len(self.df)))
        bar_height = 0.9

        for i, (_, row) in enumerate(self.df.iterrows()):
            duration = (row[self.end_date_field] - row[self.start_date_field]).days
            color = self.set_color(i, row)
            ax.barh(i, duration, left=mdates.date2num(row[self.start_date_field]), height=bar_height, color=color)
        
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
            no_suffix = os.path.splitext(self.path)[0]
            trimmed_name = no_suffix.split("/", 1)[-1]
            self.generate_gantt_chart(f"diagrams/{trimmed_name}.png")
        else:
            print("data not loaded - call load_data() before saving plot")

if __name__ == "__main__":
    if len(sys.argv) == 3:
        if not os.path.exists('diagrams'):
            os.makedirs('diagrams')
        files = glob.glob('data/*.csv')
        for file in files:
            chart = GanttChart(file, sys.argv[1], sys.argv[2])
            chart.load_data()
            chart.save_plot()
    else:
        print("usage: python3 visualizer.py 'start date field' 'end date field'")
        sys.exit(1)

