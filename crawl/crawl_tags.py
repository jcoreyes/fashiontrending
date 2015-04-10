from instagram.client import InstagramAPI
from instagram.bind import InstagramAPIError
import sys
import cPickle as pickle
import time

def get_recent_media(tag):
	all_media = []
	recent_media = []
	min_id = None
	while (recent_media is not None):
		try:
			if (min_id is not None):
				recent_media, next_ = api.tag_recent_media(tag=tag, min_id=min_id)
			else:
				recent_media, next_ = api.tag_recent_media(tag=tag)
			for media in recent_media:
				all_media.append(media)
				if len(media) % 200 == 0:
					print("At %d" %len(media))
			if len(recent_media) > 19:
				min_id = recent_media[-1].id.split('_')[0]
			else:
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
		except:
			"Error getting data for %d" %tag
			break
	print min_id
	print "Found %d" %len(all_media)
	media_counts.append(len(all_media))
	pickle.dump(all_media, save_file)

if __name__ == '__main__':
	media_counts = []
	access_token = sys.argv[1]
	tags_file = sys.argv[2]
	output_file = sys.argv[3]
	api = InstagramAPI(access_token=access_token)
	save_file = open(output_file, 'ab')

	get_recent_media('fashion')

