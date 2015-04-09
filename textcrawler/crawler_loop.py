import re, urllib

def get_info():
	access_token = "245374485.9d8f80b.c15ebf31857942ef8dd8fb67c4f3445d"
	tag_url = "https://api.instagram.com/v1/tags/fashion/media/recent?access_token=" + access_token

	handle = urllib.urlopen(tag_url)
	media_info = handle.read()
	return media_info

def get_tags(media_info, tag_dict):
	for tag in re.findall(r"\b#[\w]*", media_info):
		if tag not in tag_dict.keys():
			tag_dict[tag] = 1
		else:
			tag_dict[tag] += 1