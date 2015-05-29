import sys
import json
import pprint
import operator
from cluster import *


def sort(filename, tag_info, num):
	# Going through the files and finding out what tags and images one should have. 
	data = {}

	temp = {}
	lst = []
	''' Load all of the data '''
	with open (filename, 'rb') as fp:
		data = json.load(fp)

	'''' Create a dictionary with the tags being the key. '''
	for key, value in data.iteritems():
		if 'title' in key:
			name = key.replace('_title', '')
			temp[name] = []
	''' Populate the dictionary ''' 
	for key, value in data.iteritems():
		if 'title' not in key:
			name =  key.split('_', 1)[0]
			temp[name].append(value)
	top = []
	''' Sort the tags into the top list. '''
	top = sort_tags(tag_info)

	count = 1
	final_dict = {}

	for k in top:
		temp_key = {}
		key = k[0: 11] + '_title' + k[11:]
		temp_key = k[0:11] + '_title' + str(count)

		new_key = temp_key.replace('_title', '')
		final_dict[temp_key] = data[key]
		num = 1
		images = temp[k]
		# if(len(images) >= 10):
			# count += 1

		temp_dict = {}
		if(len(images) > 5):
			for img in images:
				mod_key = '%s_image%d' % (new_key, num)
				temp_dict[mod_key] = img
				# final_dict[mod_key] = img
				num += 1
				if(num == 6):
					final_dict.update(temp_dict)
					break
			count += 1
		if(count > 32):
			break
	with open('top32_sort.json', 'wb') as fp:
		json.dump(final_dict, fp, indent = 2)




def sort_tags(tag_info):
	# Sorts the tags
	percents = {}
	# sorted_x = sorted(x.items(), key=operator.itemgetter(0))

	with open (tag_info, 'rb') as fp:
		percents = json.load(fp)
	sorted_percents = sorted(percents.items(), key=operator.itemgetter(1), reverse=True)
	results = []
	for i in range(0, len(sorted_percents)):
		results.append(sorted_percents[i][0])
	return results



if __name__ == '__main__':
	filename = sys.argv[1]
	tag_info = sys.argv[2]
	sort(filename, tag_info, 32)