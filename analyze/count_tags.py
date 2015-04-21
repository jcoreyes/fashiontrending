import cPickle as pickle
import sys
import os

def count_all_tags(posts_lst):
	for posts in posts_lst:
		for post in posts:
			count_post_tags(post)
	#print tags
	filtered_tags = {i:tags[i] for i in tags if tags[i]>100}
	my_file = open("tag_counts.txt", 'a')
	i = 0
	for w in sorted(filtered_tags, key=filtered_tags.get,reverse=True):
		print w, filtered_tags[w]
		try:
			my_file.write("%s %d\n" %(w, filtered_tags[w]))
		except UnicodeError as e:
			print "Error writing tag"
			continue
		i += 1
		if i > 500:
			break

def count_post_tags(post):
	if not hasattr(post, 'tags'):
		return
	for tag in post.tags:
		tag_name = tag.name
		#tag_name = tag.name.encode('ascii', 'ignore')
		if tag_name not in tags:
			tags[tag_name] = 1
		else:
			tags[tag_name] += 1
			
def read_posts(filename):
	my_file = open(filename, 'rb')
	posts_lst = []
	while True:
		try:
			posts = pickle.load(my_file)
			posts_lst.append(posts)
		except EOFError:
			break
	return posts_lst

if __name__ == '__main__':
	data_folder = sys.argv[1]
	tags = {}
	all_posts_lst = []
	i = 0
	for filename in os.listdir(data_folder):
		posts_lst = read_posts(data_folder+"/"+filename)
		for posts in posts_lst:
			all_posts_lst.append(posts)
	count_all_tags(all_posts_lst)