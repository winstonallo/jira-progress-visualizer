import os
import glob
import sys
from visualizer.gantt_chart import GanttChart
from visualizer.config import Config
from visualizer.error import Error

if __name__ == "__main__":
    if len(sys.argv) == 2:
        src_dir = sys.argv[1]
    else:
        Error("error: please provide a source directory in the command line - aborting")
    config = Config()
    if not os.path.exists('diagrams'):
        os.makedirs('diagrams')
    if not os.path.exists(src_dir):
        Error(f"error: directory {src_dir} does not exist; please ensure the path is valid - aborting")
    files = glob.glob(f"data/*.csv")
    for file in files:
        print(file)
        if file[:7] == 'data/0_':
            chart = GanttChart(file, config.get('0'))
        elif file[:7] == 'data/1_':
            chart = GanttChart(file, config.get('1'))
        elif file[:9] == 'data/1.1_':
            chart = GanttChart(file, config.get('1.1'))
        elif file[:7] == 'data/2_':
            chart = GanttChart(file, config.get('2'))
        chart.load_data()
        chart.save_plot()
        