import pickle
import sys


if __name__ == '__main__':
	user_posts_file = sys.argv[1]
	my_file = open(user_posts_file, 'rb')
	user_posts = pickle.load(my_file)
	while(user_posts is not None):
		try:
			print(len(user_posts))
			user_posts = pickle.load(my_file)
			for post in user_posts:
				print post
		except EOFError:
			break