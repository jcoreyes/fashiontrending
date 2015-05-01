from instagram.client import InstagramAPI
from instagram.bind import InstagramAPIError
import sys
import cPickle as pickle
import time
import datetime

MAX_MEDIA = 1e3

def get_recent_media(tag):
	""" 
	Get recent media for a given tag and save all tags by
	day. Dumps media as python objects formatted as 
	day_media = [media1_obj, media2_obj, ...]
	Dumps day_media for each consecutive day to the same file
	"""

	output_file = "recent_media/%s" %tag
	day_media = []
	media_count = 0
	max_id = None

	prev_day = None

	while True:
		try:
			# Media is return 20 per request. We can paginate through the media by
			# specifying the max id of the previous request
			if (max_id is not None):
				recent_media, next_ = api.tag_recent_media(tag_name=tag, max_id=max_id)
			else:
				recent_media, next_ = api.tag_recent_media(tag_name=tag)

			for media in recent_media:
				day_media.append(media)
				if media_count % 40 == 0:
					print("At %d with rate limit %s and time %s" 
						%(media_count, api.x_ratelimit_remaining, recent_media[-1].created_time))

				media_count += 1

			# If 20 media obs returned then continue paginating
			if len(recent_media) == 20:
				max_id = recent_media[-1].id.split('_')[0]

			# If no more tags or reached media limit, then save and break
			if len(recent_media) < 20 or media_count >= MAX_MEDIA:
				save_media(day_media, output_file)
				break
			
			# If done crawling for this day, then save and continue
			curr_day = int(recent_media[-1].created_time.day)
			if prev_day is not None and curr_day != prev_day:
				save_media(day_media, output_file)
				prev_day = curr_day
				day_media = []

			time.sleep(1) # Time requests once per second

		except InstagramAPIError as e:
			print sys.exc_info()
			if (e.status_code == 429):
				print "Reached rate limit. Waiting 60sec"
				time.sleep(60)
				continue
			

def save_media(day_media, output_file):
	print "Saving %d media objects" %len(day_media)
	with open(output_file, 'ab') as f:
		pickle.dump(day_media, f)

if __name__ == '__main__':
	try:
		id_no = int(sys.argv[1]) # Which access token to use from file
	except:
		print "Usage: crawl_tags.py <id_no>"
		exit(0)
		
	with open('tags_to_crawl.txt', 'r') as f:
		tags_to_crawl = f.read().splitlines()
	print tags_to_crawl

	with open('access_tokens.txt', 'r') as f:
		access_token = f.read().splitlines()[id_no]

	api = InstagramAPI(access_token=access_token)

	for tag in tags_to_crawl:
		print "Crawling tag: " + tag
		get_recent_media(tag)