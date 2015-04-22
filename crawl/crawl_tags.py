from instagram.client import InstagramAPI
import sys
#from urlparse import urlparse
import codecs
import pickle
import pprint
#Access Token:1811685103.7c9b708.bb2a3b18ffbf4adda8774e4c113d38b5


''' Looks through all of the tags and retrives media objects that have at least three 
tags in the list. '''
def get_media(tags, api):
	media_lst = []
	for tag in tags:
		val = api.tag_recent_media(count=10, tag_name=tag)[0]
		for item in val:
			count = 0
			for aux_tag in item.__dict__['tags']:
				tag_val = aux_tag.name
				''' Loooks through all aux tags and checking to make sure that the have the right tag'''
				if tag_val in tags:
					count += 1
					if count > 2:
						# print item
						# print tags
						# print item.__dict__['tags']
						if item not in media_lst:
							media_lst.append(item)
						# break
	output = open('data.pk1', 'wb')
	pickle.dump(media_lst, output)
	pprint.pprint(media_lst)
	output.close()




if __name__ == '__main__':
	access_token = sys.argv[1]
	tags_file = sys.argv[2]
	api = InstagramAPI(access_token=access_token)
	tags = []
	f = codecs.open(tags_file, encoding='utf-8')
	tags = [str(line.strip()).translate(None, '#') for line in f]
	tags = tags[:5]
	get_media(tags, api)
	# with open(tags_file, 'r') as t_file:
	# 	tags = [line.strip() for line in t_file]
	# 	# for line in lines:
		# 	line = line.translate(None, '#').rstrip('\n')
		# 	print line
		# 	#tags.append(str(line))
		# 	print type(line)
		# 	tags.append(str(line))
		# tags.append("hiwerw")
	f.close()
	get_media(tags, api)
