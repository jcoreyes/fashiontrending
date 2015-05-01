""" Analyze time series of tag counts"""
import cPickle as pickle
import sys
import pandas as pd
import matplotlib.pyplot as plt
import time
import datetime
import numpy as np

def load_tag_counts(datafile):
    with open(data_file, 'r') as f:
        data = f.read().splitlines()
    tag_counts = {}
    times = []
    for line in data:
        line_data = line.split(" ")
        times.append(line_data[0])
        for tagc in line_data[1:]:
            tagc =  tagc.split(":")
            if len(tagc) == 2:
                tag, count = tagc
                count = int(count)
            else:
                tag = tagc[0]
                count = np.nan
            if tag not in tag_counts:
                tag_counts[tag] = [count]
            else:
                tag_counts[tag].append(count)
    times = [datetime.datetime(*time.strptime(x, '%Y-%m-%d-%H-%M-%S')[:6]) for x in reversed(times)]
    for tag, counts in tag_counts.items():
        tag_counts[tag] = counts[0:len(times)]
    return times, tag_counts

if __name__=='__main__':
    data_file = "../crawl/time_tag_counts.txt"
    times, tag_counts = load_tag_counts(data_file)
    df = pd.DataFrame.from_dict(tag_counts, orient='index')
    df = df[df[len(times)-1]>10000]
    df.sort(columns=len(times)-1, ascending=False, inplace=True, na_position='last')
    top_tags = df.pct_change(axis=1, periods=24).sort(ascending=False, columns=len(times)-1).ix[0:100, len(times)-1]

    # with open("top_popular_tags.txt", "w") as f:
    #     for tag in top_tags.index.tolist():
    #         f.write("%s\n" %tag)

    # plt.plot(times, tag_counts['fashion'])
    # plt.show()
