import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import os
import textwrap
import operator
from visualizer.error import Error

plt.rcParams['font.family'] = 'DejaVu Serif'
plt.rcParams['font.weight'] = 'bold'

class GanttChart:

    def __init__(self, path : str, config : dict[str, str]) -> None:
        self.path = path
        self.load_config(config)
        self.df = None
        self.operation_mapping = {
            "equals": operator.eq,
            "not_equals": operator.ne,
            "lower_than": operator.lt,
            "lower_equals": operator.le,
            "greater_than": operator.gt,
            "greater_equals": operator.ge
		}

    def load_config(self, config : dict) -> None:
        try:
            self.start_date_field = config['fields']['start_date']
            self.end_date_field = config['fields']['end_date']
            self.target_dir = config['directories']['target']
            self.csv_dir = config['directories']['csv']
            self.label = config['fields']['label']
            self.filters = config['filters']
            self.positioning_specs = config['visualization']['positioning_specs']
            self.bar_height = float(config['visualization']['bar_height'])
            self.milestones = config['milestones']
            self.color_map = dict(config['visualization']['colors'])
            self.y_label_fontsize = int(config['visualization']['y_label_fontsize'])
        except KeyError as e:
            Error(f'error: data {e} missing in {self.path}')
    
    def set_color(self, i : int, row : pd.Series) -> str:
        color = self.color_map.get(row[self.label])
        if color is not None:
            return color
        return self.colors[i]

    def wrap_lines(self, series : pd.Series, width : int) -> pd.Series:
        wrapped_series = series.apply(lambda x: textwrap.fill(x, width) if isinstance(x, str) else x)
        return wrapped_series

    def apply_filters_to_dataframe(self):
        for filter in self.filters:
            try:
                self.df = self.df[self.operation_mapping[filter['operator']](self.df[filter['field']], filter['condition'])]
            except IndexError:
                Error(f'error: invalid filter: {filter}')

    def set_positioning_specs(self) -> None:
        for key, value in self.positioning_specs.items():
            if value['ascending'] == "True":
                ascending = True
            else:
                ascending = False
            self.df['condition'] = self.df[value['field']].apply(lambda x: 1 if x == value['value'] else 0)
            self.df.sort_values(by=[value['field']], inplace=True, ascending=ascending)
        self.df.drop('condition', axis=1, inplace=True)

    # loads data from csv file and applies filters
    def load_data(self) -> None:
        self.df = pd.read_csv(self.path)
        self.df[self.start_date_field] = pd.to_datetime(self.df[self.start_date_field], format='%d/%b/%y %I:%M %p', errors='coerce').dt.date
        self.df[self.end_date_field] = pd.to_datetime(self.df[self.end_date_field], format='%d/%b/%y %I:%M %p', errors='coerce').dt.date
        self.df.dropna(subset=[self.end_date_field, self.start_date_field], inplace=True)
        if self.positioning_specs != "None":
            self.set_positioning_specs()
        if self.filters != "None":
            self.apply_filters_to_dataframe()
        self.df[self.label] = self.wrap_lines(self.df[self.label], 40)

    def generate_gantt_chart(self, output_path : str):
        fig, ax = plt.subplots(figsize=(19.2, 10.8))
        self.colors = plt.cm.viridis(np.linspace(0, 1, len(self.df))) # create color palette based on number of rows

        for i, (_, row) in enumerate(self.df.iterrows()): # iterate over rows and plot bars based on start and end date
            duration = (row[self.end_date_field] - row[self.start_date_field]).days
            color = self.set_color(i, row)
            ax.barh(i, duration, left=mdates.date2num(row[self.start_date_field]), height=self.bar_height, color=color)
        
        ax.set_yticks(range(len(self.df))) # set y-ticks to number of rows
        ax.set_yticklabels(self.df[self.label], fontsize=self.y_label_fontsize, color='grey') # set y-tick labels to configured label
        plt.yticks(rotation=0) 

        self.format_axes(ax)
        self.set_milestones()
        plt.savefig(output_path, dpi=300)
        print(f"info: gantt chart saved to {output_path}")

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