import sys
import cPickle as pickle
import os
def most_popular_posts(posts_lst):
	popular_posts = []
	for posts in posts_lst:
		for post in posts:
			if post.likes > 1000:
				popular_posts.append(post)
	sorted(popular_posts, key=lambda x: x.likes, reverse=True)
	with open('popular_posts.txt', 'w') as my_file:
		for i in range(100):
			my_file.write("%s\n" %popular_posts[i].images['standard_resolution'].url)

def read_posts(filename):
	my_file = open(filename, 'rb')
	posts_lst = []
	while True:
		try:
			posts = pickle.load(my_file)
			posts_lst.append(posts)
			break
		except EOFError:
			break
	my_file.close()
	return posts_lst

if __name__ == '__main__':
	data_folder = sys.argv[1]
	all_posts_lst = []
	i = 0
	for filename in os.listdir(data_folder):
		if filename == "user_posts":
			continue
		posts_lst = read_posts(data_folder+"/"+filename)
		for posts in posts_lst:
			all_posts_lst.append(posts)
	most_popular_posts(all_posts_lst)
