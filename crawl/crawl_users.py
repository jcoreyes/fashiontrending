from instagram.client import InstagramAPI
from instagram.bind import InstagramAPIError
import sys
import pickle
import time

def get_recent_media(user_id):
	all_media = []
	recent_media = []
	max_id = None
	counter = 0
	while (recent_media is not None):
		try:
			if (max_id is not None):
				recent_media, next_ = api.user_recent_media(user_id=user_id, max_id=max_id)
			else:
				recent_media, next_ = api.user_recent_media(user_id=user_id)
			for media in recent_media:
				all_media.append(media)
			if len(recent_media) > 19:
				max_id = recent_media[-1].id.split('_')[0]
			else:
				print "Found %d" %len(all_media)
				break

		except InstagramAPIError as e:
			print e
			if (e.status_code == 429):
				print "Rate limit reached. Waiting 1min"
				recent_media = []
				time.wait(60)
			elif (e.status_code == 502):
				"Unable to parse response"
				break
			else:
				"Instagram Error"
				break
		except:
			"Error getting data for %d" %user_id
			break

	media_counts.append(len(all_media))
	pickle.dump(all_media, save_file)

if __name__ == '__main__':
	media_counts = []
	access_token = sys.argv[1]
	user_ids_file = sys.argv[2]
	output_file = sys.argv[3]
	api = InstagramAPI(access_token=access_token)
	save_file = open(output_file, 'ab')

	user_ids = []
	with open(user_ids_file, 'r') as id_file:
		for line in id_file.readlines():
			user_ids.append(line.rstrip('\n'))
	while user_ids[0] != '10051934':
		user_ids.pop(0)

	for user_id in user_ids:
		try:
			print "Crawling %s" %user_id
			get_recent_media(user_id)
			print "Rate limit %s" %api.x_ratelimit_remaining
			print media_counts
		except:
			"Error crawling"
			# [2952, 4333, 280, 1501, 1285, 765, 2446, 887, 1800, 171, 2059, 1169, 64, 2377, 1392, 852, 1143, 1039, 450, 771, 979, 2911, 446, 1230, 591, 4822, 4965, 14113, 4285]
			# Crawling 10051934
