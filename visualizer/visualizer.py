import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import os
import sys

plt.rcParams['font.family'] = 'DejaVu Serif'
plt.rcParams['font.weight'] = 'bold'

class GanttChart:

    def __init__(self, path : str, config : dict[str, str]) -> None:
        self.path = path
        self.load_config(config)
        self.df = None

    def load_config(self, config):
        try:
            self.start_date_field = config['start_date_field']
            self.end_date_field = config['end_date_field']
            self.target_dir = config['target_dir']
            self.csv_dir = config['csv_dir']
            self.stream_color = config['stream_color']
            self.ap_color = config['ap_color']
            self.label = config['label']
            self.deadline = config['deadline']
            self.filters = config['filters?']
        except KeyError:
            print(f'error: data missing in {self.path}')
            sys.exit(1)
    
    def set_color(self, i : int, row : pd.Series) -> str:
        if row[self.label] == 'Testphase':
            return 'grey'
        elif row[self.label] == 'Produktivsetzung':
            return 'yellow'
        elif row[self.label] == 'Abnahme':
            return 'green'
        elif row['Issue Type'] == 'Stream' and self.path != 'streams.csv':
            return self.stream_color
        elif row['Issue Type'] == 'Arbeitspaket':
            if self.ap_color == 'random':
                return self.colors[i]
            else:
                return self.ap_color
        else:
            return self.colors[i]

    def apply_filters_to_dataframe(self):
        for filter in self.filters:
            try:
                self.df = self.df[self.df[filter[0]] != filter[1]]
            except IndexError:
                print(f'error: invalid filter: {filter}')
                sys.exit(1)

    def load_data(self):
        self.df = pd.read_csv(self.path)
        self.df[self.start_date_field] = pd.to_datetime(self.df[self.start_date_field], format='%d/%b/%y %I:%M %p', errors='coerce').dt.date
        self.df[self.end_date_field] = pd.to_datetime(self.df[self.end_date_field], format='%d/%b/%y %I:%M %p', errors='coerce').dt.date
        self.df.dropna(subset=[self.end_date_field, self.start_date_field], inplace=True)
        self.df['is_stream'] = self.df['Issue Type'].apply(lambda x: 1 if x == 'Stream' else 0)
        self.df.sort_values(by=['is_stream', self.start_date_field], inplace=True, ascending=False)
        self.df.drop('is_stream', axis=1, inplace=True)
        self.apply_filters_to_dataframe()

    def generate_gantt_chart(self, output_path : str):
        fig, ax = plt.subplots(figsize=(20, 10))
        self.colors = plt.cm.viridis(np.linspace(0, 1, len(self.df)))
        bar_height = 0.9

        for i, (_, row) in enumerate(self.df.iterrows()):
            duration = (row[self.end_date_field] - row[self.start_date_field]).days
            color = self.set_color(i, row)
            ax.barh(i, duration, left=mdates.date2num(row[self.start_date_field]), height=bar_height, color=color)
        
        ax.set_yticks(range(len(self.df)))
        ax.set_yticklabels(self.df[self.label], fontsize=12)
        plt.yticks(rotation=0)

        self.format_axes(ax)

        deadline = pd.to_datetime(self.deadline)
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
            self.generate_gantt_chart(f"{self.target_dir}/{trimmed_name}.png")
        else:
            print("data not loaded - call load_data() before saving plot")



