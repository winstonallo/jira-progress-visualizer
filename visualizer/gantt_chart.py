import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.colors as mcolors
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
        self.df = None
        self.colors = None
        self.load_config(config)
        self.operation_mapping = {
            "equals": operator.eq,
            "not_equals": operator.ne,
            "lower_than": operator.lt,
            "lower_equals": operator.le,
            "greater_than": operator.gt,
            "greater_equals": operator.ge
		}        
        
    def load_config(self, config : dict) -> None:
        self.config = config
        if not os.path.exists(self.config.get('directories', {}).get('target')):
            os.makedirs(self.config.get('directories', {}).get('target'))
        self.target_dir = self.config.get('directories', {}).get('target', 'diagrams')
        self.csv_dir = self.config.get('directories', {}).get('csv')
        self.start_date_field = self.config.get('fields', {}).get('start_date')
        self.end_date_field = self.config.get('fields', {}).get('end_date')
        self.label = self.config.get('fields', {}).get('label') 
        self.filters = self.config.get('filters', [])
        self.positioning_specs = self.config.get('visualization', {}).get('positioning_specs')
        self.bar_height = float(self.config.get('visualization', {}).get('bar_height', 0.9))
        self.milestones = self.config.get('milestones', [])
        self.color_map = self.config.get('visualization', {}).get('colors', {})
        self.fonts = self.config.get('visualization', {}).get('fonts', {})
        self.chart_line_style = self.config.get('visualization', {}).get('chart_line_style', '--')
        self.sort_by = self.config.get('sort_by', 'start_date')
        self.date_input_format = self.config.get('date_format', '%d/%b/%y %I:%M %p')
        self.date_display_format = self.config.get('date_display_format', '%Y-%m-%d')

    def validate_config(self) -> None:
        required_fields = [
            'directories.csv',
            'fields.start_date',
            'fields.end_date']
        if missing := [field for field in required_fields if self.config.get(field) is None] is not None:
            raise Error(f'error: missing required fields: {",".join(missing)}; please check your config file - aborting', exit=True)
    
    def set_color(self, i : int, row : pd.Series) -> str:  
        if color := self.color_map.get(row[self.label]) is not None:
            return color
        return self.colors[i]

    def wrap_lines(self, series : pd.Series, width : int) -> pd.Series:
        wrapped_series = series.apply(lambda x: textwrap.fill(x, width) if isinstance(x, str) else x)
        return wrapped_series

    def apply_filters_to_dataframe(self) -> None:
        for filter in self.filters:
            try:
                self.df = self.df[self.operation_mapping[filter['operator']](self.df[filter['field']], filter['condition'])]
            except IndexError:
                raise ValueError(f'error: invalid filter: {filter} - ignoring')

    def sort_dataframe(self) -> None:
        self.df['date_diff'] = (self.df[self.end_date_field] - self.df[self.start_date_field])
        if self.sort_by == 'start_date':
            self.df = self.df.sort_values(by=[self.start_date_field, 'date_diff'], ascending=[False, True])
        elif self.sort_by == 'structure_pos':
            self.df['structure_pos'] = self.df['Description'].str.extract(r'(\d+)$').astype(int)
            self.df = self.df.sort_values(by=['structure_pos', 'date_diff'], ascending=[False, True])
        self.df.drop(columns=['date_diff'], inplace=True)

    def load_data(self) -> None:
        self.df = pd.read_csv(self.path)
        self.df[self.start_date_field] = pd.to_datetime(self.df[self.start_date_field], format=self.date_input_format, errors='coerce').dt.date
        self.df[self.end_date_field] = pd.to_datetime(self.df[self.end_date_field], format=self.date_input_format, errors='coerce').dt.date
        self.df.dropna(subset=[self.end_date_field, self.start_date_field], inplace=True)
        if self.filters != 'None':
            self.apply_filters_to_dataframe()
        self.sort_dataframe()
        self.df[self.label] = self.wrap_lines(self.df[self.label], 40)

    def init_ylabels(self, ax):
        ax.set_yticks(range(len(self.df)))
        ax.set_yticklabels(self.df[self.label])

        for label, value in zip(ax.get_yticklabels(), self.df['Issue Type']):
            fontsize = self.fonts['y_label'][value]['font_size']
            if len(self.df) > 14:
                fontsize -= 4
            label.set_color(self.fonts['y_label'][value]['font_color'])
            label.set_fontsize(fontsize)
        return ax

    def generate_gantt_chart(self, output_path : str) -> None:
        fig, ax = plt.subplots(figsize=(19.2, 10.8))
        self.colors = plt.cm.Greys(np.linspace(0.3, 0.9, len(self.df)))
        for i, (_, row) in enumerate(self.df.iterrows()):
            duration = (row[self.end_date_field] - row[self.start_date_field]).days
            color = self.set_color(i, row)
            ax.barh(i, duration, left=mdates.date2num(row[self.start_date_field]), height=self.bar_height, color=color)
        ax = self.init_ylabels(ax)
        plt.yticks(rotation=0) 
        self.format_axes(ax)
        self.set_milestones()
        plt.savefig(output_path, dpi=300)
        print(f"info: gantt chart saved to {output_path}")

    def set_milestones(self) -> None:
        for milestone in self.milestones:
            date = pd.to_datetime(milestone['date'])
            if milestone['name'] != 'None':
                plt.text(mdates.date2num(date), milestone['pos'], milestone['name'], rotation=90, verticalalignment='center', horizontalalignment='right', fontsize=18, color=milestone['color'])
            plt.axvline(x=mdates.date2num(date), color=milestone['color'], linestyle=milestone['line_style'], linewidth=4)

    def format_axes(self, ax) -> None:
        ax.xaxis.grid(True, linestyle=self.chart_line_style, which='major', color=self.color_map['chart_lines'], alpha=.25)
        ax.xaxis.set_major_formatter(mdates.DateFormatter(self.date_display_format))
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        plt.xticks(fontsize=12, rotation=60, color=self.color_map['x_label'])
        plt.tight_layout()

    def save_plot(self):
        if self.df is not None:
            no_suffix = os.path.splitext(self.path)[0]
            trimmed_name = no_suffix.split("/", 1)[-1]
            self.generate_gantt_chart(f"{self.target_dir}/{trimmed_name}.png")
        else:
            raise Error("data not loaded - call load_data() before saving plot")