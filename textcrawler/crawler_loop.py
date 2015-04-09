import re, urllib

def get_info():
	""" 
	Uses Instagram to find recent media that uses the "fashion" tag
	"""
	# this is graces access token. may replace
	access_token = "245374485.9d8f80b.c15ebf31857942ef8dd8fb67c4f3445d"
	# retrieves recent posts that are tagged with the word "fashion"
	tag_url = "https://api.instagram.com/v1/tags/fashion/media/recent?access_token=" + access_token
	# get instagram information
	handle = urllib.urlopen(tag_url)
	media_info = handle.read()
	return media_info

def get_tags(media_info, tag_dict):
	"""
	Parses the information from the GET request and retrieves other tags
	and puts them in a dictionary and counts the occurences

	:param str media_info: string of media post information
	:param dict tag_dict: dictionary holding the tags and occurences
	"""
	# for tags (starts with "#") found in the info
	for tag in re.findall(r"\b#[\w]*", media_info):
		# add to dictionary if not already there
		if tag not in tag_dict.keys():
			tag_dict[tag] = 1
		# increment the count if already there
		else:
			tag_dict[tag] += 1