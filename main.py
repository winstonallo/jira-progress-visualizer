import os
import glob
import sys
from visualizer.visualizer import GanttChart
from visualizer.config import Config

if __name__ == "__main__":
    if len(sys.argv) == 2:
        config_path = sys.argv[1]
    else:
        config_path = None
    config = Config().config
    if not os.path.exists(config['target_dir']):
        os.makedirs(config['target_dir'])
    files = glob.glob(f"{config['csv_dir']}/*.csv")
    for file in files:
        chart = GanttChart(file, config)
        chart.load_data()
        chart.save_plot()
        