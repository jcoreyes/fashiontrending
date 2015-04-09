import time
from crawler_loop import * 

def main():
	"""
	Crawl the instagram posts and find popular tags related to fashion
	"""
	# holds all the tags and occurences
	tag_dict = {}
	textfile = file('tag_crawler_output.txt','wt')
	
	# retrieve data from instagram every 10 seconds
	for i in xrange(10):
		# every 10 seconds, gather information regarding fashion posts
		time.sleep(10)
		media_info = get_info()
		get_tags(media_info, tag_dict)
	for key in tag_dict.keys():
		strr = str(key) + " , " + str(tag_dict[key]) + "\n"
		textfile.write(strr)

	textfile.close()

if __name__ == "__main__":
    main()


