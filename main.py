import os
import glob
import sys
from visualizer.visualizer import GanttChart
from visualizer.config import Config

if __name__ == "__main__":
    if len(sys.argv) == 3:
        if not os.path.exists(sys.argv[2]):
            os.makedirs(sys.argv[2])
        files = glob.glob(f'{sys.argv[1]}/*.csv')
        for file in files:
            chart = GanttChart(file, sys.argv[2])
            chart.load_data()
            chart.save_plot()
    else:
        print("usage: python3 visualizer.py csv_dir target_dir")
        sys.exit(1)