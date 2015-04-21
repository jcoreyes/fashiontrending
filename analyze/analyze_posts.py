import cPickle as pickle
import sys
import matplotlib.pyplot as plt
import numpy as np
import datetime
from instagram.client import InstagramAPI
import os


def detect_trends(post_lst):
	for posts in posts_lst:
		for post in posts:
			detect_trend(post)	

def detect_trend(post):
	share_dates = []
	comment_dates = []
	t = datetime.datetime(2015, 3, 21, 0, 0)
	print post.comment_count
	print post.like_count
	post_comments = api.media_comments(post.id)
	for comment in post_comments:
		comment_dates.append(comment.created_at)
		print vars(comment)
		if "@" in comment.text:
			share_dates.append(comment.created_at)
		#share_dates.append((comment.created_at-t).total_seconds())
	print share_dates
	plt.plot(np.asarray(share_dates), np.arange(1, len(share_dates)+1))
	plt.plot(np.asarray(comment_dates), np.arange(1, len(comment_dates)+1))
	title = "Comment and share count over time with %d comments and %d likes" %(post.comment_count, post.like_count)
	plt.title(title)
	plt.xlabel("Time")
	plt.ylabel("Total number of comments or shares")
	plt.legend("Comment count", "Share count")
	plt.show()

def filter_posts(user_posts):
	filtered_posts = []
	for post in user_posts:
		if post.comment_count > 50:
			filtered_posts.append(post)
	pickle.dump(filtered_posts, open('temp_shares', 'wb'))



if __name__ == '__main__':
	api = InstagramAPI(access_token=open('../crawl/access_tokens.txt', 'r').readline().rstrip('\n'))
	data_file_name = sys.argv[1]
	posts_lst = read_posts(data_file_name)

	#detect_trends(post_lst)
	count_all_tags(posts_lst)


