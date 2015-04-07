from instagram.client import InstagramAPI
import sys

def get_recent_media(user_id):
	recent_media, next_ = api.user_recent_media(user_id=user_id, count=10)
	for media in recent_media:
		print media.caption.text

if __name__ == '__main__':
	access_token = sys.argv[1]
	user_ids_file = sys.argv[2]
	api = InstagramAPI(access_token=access_token)

	user_ids = []
	with open(user_ids_file, 'r') as id_file:
		for line in id_file.readlines():
			user_ids.append(line.rstrip('\n'))
	print user_ids
	user_ids_file.close()

	

	#get_user_id("arizona_muse")
	#get_recent_media(221174293)
