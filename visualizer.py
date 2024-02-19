import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

df = pd.read_csv('streams.csv')

df['Due Date'] = pd.to_datetime(df['Due Date'], errors='coerce').dt.date

# no jira field for start date, so using custom field
df['Custom field (Start)'] = pd.to_datetime(df['Custom field (Start)'], errors='coerce').dt.date

# remove rows with missing dates
df = df.dropna(subset=['Due Date', 'Custom field (Start)'])

# sort by start date
df = df.sort_values('Custom field (Start)')

# set up the plot
# adjust the figsize to make the chart longer and provide enough space for each bar
fig, ax = plt.subplots(figsize=(10, len(df)))

# generate a color array
colors = plt.cm.viridis(np.linspace(0, 1, len(df)))

# plot each task
bar_height = 0.9 # increase this to reduce the gap between bars
for i, (index, row) in enumerate(df.iterrows()):
    duration = (row['Due Date'] - row['Custom field (Start)']).days
    ax.barh(i, duration, left=mdates.date2num(row['Custom field (Start)']), height=bar_height, color=colors[i])

# set y-ticks to be the names of the tasks
ax.set_yticks(range(len(df)))
ax.set_yticklabels(df['Summary'], fontsize=8)
plt.yticks(rotation=0)

# improve readability by adding grid lines
ax.xaxis.grid(True, linestyle='--', which='major', color='grey', alpha=.25)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
ax.xaxis.set_major_locator(mdates.MonthLocator())

# rotate x-ticks(dates) for better visibility
plt.xticks(fontsize=8)
plt.xticks(rotation=70)

# adjust the padding between and around subplots
plt.tight_layout()

# save a high-resolution version of the plot
plt.savefig('diagram.png', dpi=300)
