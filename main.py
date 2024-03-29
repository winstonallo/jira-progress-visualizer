import os
import glob
import sys
from visualizer.gantt_chart import GanttChart
from visualizer.config import Config
from visualizer.error import Error

if __name__ == "__main__":
    source_file = None
    if len(sys.argv) >= 2:
        src_dir = sys.argv[1]
        if len(sys.argv) >= 3:
            source_file = sys.argv[2]
    else:
        Error("please provide a source directory in the command line - aborting")
    config = Config()
    if not os.path.exists(src_dir):
        Error(f"directory {src_dir} does not exist; please ensure the path is valid - aborting")
    if source_file is not None:
        if not os.path.exists(source_file):
            Error(f"file {source_file} does not exist; please ensure the path is valid - aborting")
        chart = GanttChart(source_file, config.get_config('1'))
        chart.load_data()
        chart.save_plot()
        sys.exit(0)    
    files = glob.glob(f"{src_dir}/*.csv")
    for file in files:
        if file[:7] == 'data/0_':
            chart = GanttChart(file, config.get_config('0'))
        elif file[:7] == 'data/1_':
            chart = GanttChart(file, config.get_config('1'))
        elif file[:9] == 'data/1.1_':
            chart = GanttChart(file, config.get_config('1.1'))
        elif file[:7] == 'data/2_':
            chart = GanttChart(file, config.get_config('2'))
        chart.load_data()
        chart.save_plot()
        