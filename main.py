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
    config_0 = Config('config_0.json').config
    config_1 = Config('config_1.json').config
    config_2 = Config('config_2.json').config
    if not os.path.exists(config_1['directories']['target']):
        os.makedirs(config_1['directories']['target'])
    files = glob.glob(f"{config_1['directories']['csv']}/*.csv")
    for file in files:
        print(file)
        if file[:7] == 'data/0_':
            chart = GanttChart(file, config_0)
        elif file[:7] == 'data/1_':
            chart = GanttChart(file, config_1)
        elif file[:7] == 'data/2_':
            chart = GanttChart(file, config_2)
        chart.load_data()
        chart.save_plot()
        