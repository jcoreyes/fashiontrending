from instagram.client import InstagramAPI
from instagram.bind import InstagramAPIError
import sys
import cPickle as pickle
import time

max_media = 3e4
def get_recent_media(tag):
	all_media = []
	recent_media = []
	min_id = None
	prev_day = 12
	while (recent_media is not None):
		try:
			time.sleep(0.5)
			if (min_id is not None):
				recent_media, next_ = api.tag_recent_media(tag_name=tag, max_id=min_id)
			else:
				recent_media, next_ = api.tag_recent_media(tag_name=tag)
			for media in recent_media:
				all_media.append(media)
				if len(all_media) % 1000 == 0:
					print("At %d with rate limit %s and time %s" %(len(all_media), 
						api.x_ratelimit_remaining, recent_media[-1].created_time))
			if len(recent_media) > 19:
				min_id = recent_media[-1].id.split('_')[0]
				
			curr_day = int(recent_media[-1].created_time.day)
			if curr_day != prev_day:
				media_counts.append(len(all_media))
				pickle.dump(all_media, save_file)
				prev_day = curr_day
				print("Dumped data %d" %len(all_media))
				print("Stopped at %s" %min_id)
				all_media = []

			if len(all_media) > max_media or sum(media_counts) > max_media:
				pickle.dump(all_media, save_file)
				print("Reached max count. Stopped at %s" %min_id)
				break

		except InstagramAPIError as e:
			print e
			if (e.status_code == 429):
				print min_id
				break
			elif (e.status_code == 502):
				"Unable to parse response"
				break
			else:
				break
		except Exception as e:
			print e
			"Error getting data for %s" %tag
			break
			
	print("Stopped at %s" %min_id)

if __name__ == '__main__':
	media_counts = []
	access_token = sys.argv[1]
	tag = sys.argv[2]
	output_file = sys.argv[3]
	api = InstagramAPI(access_token=access_token)
	save_file = open(output_file, 'ab')

	get_recent_media(tag)