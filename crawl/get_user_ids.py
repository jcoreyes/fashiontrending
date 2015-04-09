from instagram.client import InstagramAPI
import sys

def get_user_id(username):
	user_info = api.user_search(q=username, count=1)
	for user in user_info:
		return user.id

if __name__ == '__main__':

	access_token = sys.argv[1]
	usernames_file = sys.argv[2]
	user_ids_file = sys.argv[3]
	api = InstagramAPI(access_token=access_token)
	in_file = open(usernames_file, 'r')
	out_file = open(user_ids_file, 'w')

	for line in in_file.readlines():
		try:
			user_id = get_user_id(line.rstrip('\n'))
			out_file.write("%s\n" %user_id)
		except:
			print "Error"
			continue

	in_file.close()
	out_file.close()
