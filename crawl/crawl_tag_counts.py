from instagram.client import InstagramAPI
from instagram.bind import InstagramAPIError
import sys
import cPickle as pickle
import time
import datetime

def crawl_tag_counts(tags):
    
    while (True):
        tag_counts = {}
        try:
            for tag in tags:
                result = api.tag_search(tag)[0]
                for tag_object in result:
                    tag_counts[tag_object.name] = tag_object.media_count
                print tag_counts
                time.sleep(1)
            tag_counts_lst = ["%s:%d" %(x[0], x[1]) for x in tag_counts.items()]
            date_str = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
            open(save_file, "a").write(date_str +" " + " ".join(tag_counts_lst) + "\n")

        except InstagramAPIError as e:
            print e
            if (e.status_code == 429):
                print "Rate limit reached"
                time.sleep(60)
                continue
        except Exception as e:
            print e
            "Error getting data for %s" %tag
            time.sleep(60)
            continue
            

if __name__ == '__main__':
    api = InstagramAPI(access_token=open('access_tokens.txt', 'r').readline().rstrip('\n'))
    tags = [x.split()[0] for x in open("../analyze/tag_counts.txt", 'r').readlines()]
    save_file = "time_tag_counts.txt"
    crawl_tag_counts(tags)