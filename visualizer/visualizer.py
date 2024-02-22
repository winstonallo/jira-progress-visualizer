import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import os
import sys
import textwrap

plt.rcParams['font.family'] = 'DejaVu Serif'
plt.rcParams['font.weight'] = 'bold'

class GanttChart:

    def __init__(self, path : str, config : dict[str, str]) -> None:
        self.path = path
        self.load_config(config)
        self.df = None

    def load_config(self, config):
        try:
            self.start_date_field = config['fields']['start_date']
            self.end_date_field = config['fields']['end_date']
            self.target_dir = config['directories']['target']
            self.csv_dir = config['directories']['csv']
            self.label = config['fields']['label']
            self.filters = config['filters']
            self.bar_height = float(config['visualization']['bar_height'])
            self.milestones = config['milestones']
            self.color_map = dict(config['visualization']['colors'])
        except KeyError as e:
            print(f'error: data {e} missing in {self.path}')
            sys.exit(1)
    
    # sets color based on label
    def set_color(self, i : int, row : pd.Series) -> str:
        color = self.color_map.get(row[self.label])
        if color is not None:
            return color
        return self.colors[i]

    # wraps text in dataframe for better readability
    def wrap_line(self, series, width):
        wrapped_series = series.apply(lambda x: textwrap.fill(x, width) if isinstance(x, str) else x)
        return wrapped_series

    # applies filters to dataframe
    def apply_filters_to_dataframe(self):
        for filter in self.filters:
            try:
                self.df = self.df[self.df[filter['field']] != filter['condition']]
            except IndexError:
                print(f'error: invalid filter: {filter}')
                sys.exit(1)
        self.df[self.label] = self.wrap_line(self.df[self.label], 40)

    # loads data from csv file and applies filters
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
        fig, ax = plt.subplots(figsize=(19.2, 10.8))
        self.colors = plt.cm.viridis(np.linspace(0, 1, len(self.df))) # create color palette based on number of rows

        for i, (_, row) in enumerate(self.df.iterrows()): # iterate over rows and plot bars based on start and end date
            duration = (row[self.end_date_field] - row[self.start_date_field]).days
            color = self.set_color(i, row)
            ax.barh(i, duration, left=mdates.date2num(row[self.start_date_field]), height=self.bar_height, color=color)
        
        ax.set_yticks(range(len(self.df))) # set y-ticks to number of rows
        ax.set_yticklabels(self.df[self.label], fontsize=16, color='grey') # set y-tick labels to configured label
        plt.yticks(rotation=0) 

        self.format_axes(ax) # format x-axis and grid
        self.set_milestones() # set start and end date if configured
        plt.savefig(output_path, dpi=300) # save plot to configured target directory

    # sets start and end date (lines in chart) if configured
    def set_milestones(self):
        for milestone in self.milestones:
            date = pd.to_datetime(milestone['date'])
            if milestone['name'] != 'None':
                plt.text(mdates.date2num(date), milestone['pos'], milestone['name'], rotation=90, verticalalignment='center', horizontalalignment='right', fontsize=18, color=milestone['color'])
            plt.axvline(x=mdates.date2num(date), color=milestone['color'], linestyle='-', linewidth=4)

    def format_axes(self, ax):
        ax.xaxis.grid(True, linestyle='--', which='major', color='grey', alpha=.25)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        plt.xticks(fontsize=12, rotation=60, color='grey')
        plt.tight_layout()

    def save_plot(self):
        if self.df is not None:
            no_suffix = os.path.splitext(self.path)[0]
            trimmed_name = no_suffix.split("/", 1)[-1]
            self.generate_gantt_chart(f"{self.target_dir}/{trimmed_name}.png")
        else:
            print("error: data not loaded - call load_data() before saving plot")