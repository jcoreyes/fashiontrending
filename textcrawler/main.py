import re, urllib

textfile = file('Apr_8_1.txt','wt')
access_token = "245374485.9d8f80b.c15ebf31857942ef8dd8fb67c4f3445d"
tag_url = "https://api.instagram.com/v1/tags/fashion/media/recent?access_token=" + access_token

handle = urllib.urlopen(tag_url)
media_info = handle.read()

for tag in re.findall(r"\b#[\w]*", media_info, re.I):
	textfile.write(tag + "\n")
textfile.close()