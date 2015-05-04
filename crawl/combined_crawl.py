from instagram.client import InstagramAPI
from instagram.bind import InstagramAPIError
import sys
import cPickle as pickle
import time
import datetime
import numpy as np
import pandas as pd
import traceback
import os
MAX_MEDIA = 1e2
MAX_TIME_PER_CRAWL = 3600 # max time in seconds to spend on single tag
def get_popular_recent_media(tag):
    """ 
    Get recent media for a given tag. Return list of 100 tags sorted by likes
    """
    tag_media = []
    media_count = 0
    max_id = None

    start = time.time()
    while (time.time() - start) < MAX_TIME_PER_CRAWL:
        try:
            # Media is return 20 per request. We can paginate through the media by
            # specifying the max id of the previous request
            if (max_id is not None):
                recent_media, next_ = api.tag_recent_media(tag_name=tag, max_id=max_id)
            else:
                recent_media, next_ = api.tag_recent_media(tag_name=tag)

            for media in recent_media:
                tag_media.append(media)
                if media_count % 200 == 0:
                    print("At %d with rate limit %s and time %s for %s" 
                        %(media_count, api.x_ratelimit_remaining, recent_media[-1].created_time, tag))
                media_count += 1

            # If 20 media obs returned then continue paginating
            if len(recent_media) == 20:
                max_id = recent_media[-1].id.split('_')[0]

            # If no more tags or reached media limit, then save and break
            if len(recent_media) < 20 or media_count >= MAX_MEDIA:
                break

            time.sleep(1) # Time requests once per second

        except InstagramAPIError as e:
            print traceback.format_exc() 
            break
                
    # Sort by likes
    tag_media.sort(key=lambda x: x.likes, reverse=True)
    # Return top 100
    return tag_media[:min(len(tag_media), 100)]

def crawl_tag_counts(tags):
    tag_counts = {}
    start = time.time()
    while (time.time() - start) < MAX_TIME_PER_CRAWL:
        try:
            for tag in tags:
                print tag
                result = api.tag_search(tag)[0]
                for tag_object in result:
                    tag_counts[tag_object.name] = tag_object.media_count
                time.sleep(1)
            break
        except InstagramAPIError as e:
            print traceback.format_exc() 
            if (e.status_code == 429):
                print "Rate limit reached"
                time.sleep(60)
                continue
        except Exception as e:
            print traceback.format_exc() 
            "Error getting data for %s" %tag
            time.sleep(60)
            continue

    return tag_counts

def save_media(day_media, output_file):
    print "Saving %d media objects" %len(day_media)
    with open(output_file, 'ab') as f:
        pickle.dump(day_media, f)

def save_topmedia(top_media, output_file):
    with open(output_file, 'w') as f:
        index = 1
        f.write("{\n")
        for tag, items in top_media.items():
            f.write("\"popularitem_title%d\": \"%s\",\n" %(index, tag))
            for media_index, media in enumerate(items):
                f.write("\"popularitem%d_image%d\": \"%s\"" %(index, media_index+1, media.images['standard_resolution'].url))
                if index != 3 or media_index != len(items)-1:
                    f.write(",")
                f.write("\n")
            index += 1
        f.write("}")



def save_tag_counts(tag_counts, output_file):
    print "Saving %d tag counts" % len(tag_counts)
    tag_counts_lst = ["%s:%d" %(x[0], x[1]) for x in tag_counts.items()]
    date_str = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    with open(output_file, 'a') as f:
        f.write(date_str +" " + " ".join(tag_counts_lst).encode('utf-8') + "\n")

def save_tag_counts_df(tag_counts, df):
    last_col = df.shape[1]
    df[last_col] = np.nan
    for tag, count in tag_counts.items():
        df[last_col][tag] = count

def load_tag_counts(data_file):
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

def get_top_tags(df):
    last_col = df.shape[1] - 1
    top_tags = df.loc[df[last_col]>10000].pct_change(axis=1, periods=min(24, last_col))
    top_tags.drop(['tagsforlikesapp'], inplace=True)
    # Return top 10 based on pct change
    top_tags = top_tags.sort([df.shape[1]-1], ascending = False).ix[0:10, df.shape[1]-1]
    return top_tags

def crawl(df, all_tags):
    t1 = time.time()
    t2 = time.time()
    top_tags = get_top_tags(df)
    f1 = False
    f2 = True
    while (True):
        try:
            if f1 or (time.time() - t1) > 3600:
                t1 = time.time()
                f1 = False
                print "Crawling counts at %s" %datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
                tag_counts = crawl_tag_counts(all_tags)
                save_tag_counts(tag_counts, '/home/jcoreyes/Dropbox/fp_website_dump/time_tag_counts.txt')
                # Also save tag counts to data frame
                save_tag_counts_df(tag_counts, df)
                top_tags = get_top_tags(df)
                print top_tags

            if f2 or (time.time() - t2) > 3600*24:
                t2 = time.time()
                f2 = False
                directory = "/home/jcoreyes/Dropbox/fp_website_dump/recentMedia_" + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
                if not os.path.exists(directory):
                    os.makedirs(directory)
                print "Crawling tags at %s" %datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
                top30_media = {}
                for index, tag in enumerate(top_tags.index):
                    tag_recent_media = get_popular_recent_media(tag)
                    save_media(tag_recent_media, '%s/%s' %(directory,tag))
                    if index < 3:
                        top30_media[tag] = tag_recent_media[0:10]
                save_topmedia(top30_media, "/home/jcoreyes/Dropbox/fp_website_dump/fp_website/top30.json")

        except:
            print traceback.format_exc() 
            time.sleep(60)
            continue

if __name__ == '__main__':
    try:
        id_no = int(sys.argv[1]) # Which access token to use from file
    except:
        print "Usage: crawl_tags.py <id_no>"
        exit(0)
        
    with open('../analyze/tag_counts.txt', 'r') as f:
        all_tags = [x.split()[0] for x in f.read().splitlines()]
    print all_tags

    with open('access_tokens.txt', 'r') as f:
        access_token = f.read().splitlines()[id_no]

    api = InstagramAPI(access_token=access_token)

    prev_times, prev_tag_counts = load_tag_counts('/home/jcoreyes/Dropbox/fp_website_dump/time_tag_counts.txt')

    df = pd.DataFrame.from_dict(prev_tag_counts, orient='index')

    all_tags = all_tags
    crawl(df, all_tags)