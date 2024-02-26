import os
import glob
import sys
from visualizer.gantt_chart import GanttChart
from visualizer.config import Config
from visualizer.pdf import PDF

if __name__ == "__main__":
    if len(sys.argv) == 2:
        config_path = sys.argv[1]
    else:
        config_path = None
    config = Config()
    if not os.path.exists('diagrams'):
        os.makedirs('diagrams')
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
        elif file[:7] == 'data/3_':
            chart = GanttChart(file, config.get('3'))
        chart.load_data()
        chart.save_plot()
        