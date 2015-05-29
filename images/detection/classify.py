import json
from pprint import pprint
import imghdr
import sys
import urllib
import os
import pickle
from cluster import *
from six import string_types
from instagram.client import InstagramAPI
import filter32


from socket import error as SocketError

#Number of images per tag
NUM_IMAGES = 5

#Number of tags to select 
NUM_TAGS = 32

MOD_FILE = 'top32_mod.json'

TAG_FILE = 'tag_info'

# from urllib import FancyURLopener
class MyOpener(urllib.FancyURLopener):
	version = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11'


def classify(knn, gsvm, json_file, num_img):
	''' Goes through the json file and determiens whether the iamges are fashion related or not. '''
	k = 200
	good_list, bad_list = findAndclassifyTags(k, knn, gsvm, json_file, 0.6) 
	with open(json_file) as data_file:    
			data = json.load(data_file)
			count = 0
			curr = {}
			tags = []
			names = []
			compare_list = []
			for key, value in data.iteritems():
				test = key.replace('_title', '') + '_'
				if(value in bad_list):
					print "skipping. Not a good tag"
					compare_list.append(test)
			for key, value in data.iteritems():
				if(value in bad_list or key in compare_list):
					print "Not a good tag. Skipping"
				elif('title' in key):
					print "Tag"
					curr[key] = value
					count += 1
				elif(not isinstance(value, string_types)):
					print "skipping"
				elif(value in bad_list):
					print "skipipng. Not a good tag!"
				else:
					image_name = os.path.join('sample', str(count) + '.jpg')
					count += 1
					myopener = MyOpener()
					try:
						myopener.retrieve(value, image_name)
					except urllib.ContentTooShortError:
						print "Content %s too short. Skipping" % value
					except SocketError as e:
						if e.errno != errno.ECONNRESET:
							raise
						print "Reset at %s. Going on " % value
					except IOError:
						print "Cannot find %s. Going on" % value
					if(imghdr.what(image_name) != None):
						try:
							_, des_testing = get_sift_file(image_name)
							if(des_testing != [None]):
								predicted = classify_image(k, knn, des_testing, image_name, gsvm)
								if(predicted[0] < 4):
									curr[key] = value
						except cv2.error:
							print "Couldn't get, moving on."
			for i in range(0, len(tags)):
				curr[tags[i]] = names[i]
			with open(MOD_FILE, 'wb') as fp:
    				json.dump(curr, fp, indent = 2)


  	  		with open('bad_list.txt', 'wb') as f:
    				for elem in bad_list:
    					key = elem[0: 11] + '_title' + elem[11:]
    					string = "%s \n" % data[key]
    					f.write(string)



def loop_tagsGroup(json_file):
	''''Expects: Tag names to be in the format popularitem_title(num), and 
	image_urls to be in the format popularitem(num)_img(num2) '''
	with open(json_file) as data_file:    
			data = json.load(data_file)
			key_list = []
			num = 0

			tagDict = {}
			for key, value in data.iteritems():
				if('title' in key):
					key_list.append(key.replace('_title', ''))
			for key, value in data.iteritems():
				if('title' in key):
					continue
				else:
					possible_tag = key.split('_', 1)[0]
					if(possible_tag in key_list):
						image_name = os.path.join('tagDetec', str(num) + '.jpg')
						num += 1
						print value
						print image_name
						try:
							urllib.urlretrieve(value, image_name)
						except urllib.ContentTooShortError:
							print "Content %s too short. Skipping" % value
						except SocketError as e:
							if e.errno != errno.ECONNRESET:
								raise
							print "Reset at %s. Going on " % value
						except IOError:
							print "Cannot find %s. Going on" % value

						if(imghdr.what(image_name) != None and image_name!= None):
							print possible_tag
							print image_name
							pprint(tagDict)
							if possible_tag in tagDict:
								print "%s already in tagDict" % possible_tag
								tagDict[possible_tag].append(image_name)
							else:
								print "%s not in tagDict. Adding now" % possible_tag
								tagDict[possible_tag] = [image_name]
			data_file.close()
			return tagDict

def write_bad(input_name, output_name, threshold):
	data = {}
	with open(input_name, 'rb') as data_file:    
		data = json.load(data_file)
	bad_list = []
	for key, value in data.iteritems():
		if value < threshold:
			bad_list.append(key)
	with open(output_name, 'wb') as fp:
		for elem in bad_list:
			string = '%s \n' % elem
			fp.write(string)


def go_all(directory_name, threshold):
	lst = os.listdir(directory_name)
	for item in lst:
		if('recentMedia' in item):
			location = os.path.join(directory_name, item)
			files = os.listdir(location)
			if('tag_results' in files):
				name = os.path.join(location, 'tag_results')
				output = 'bad_list%f.txt' % threshold
				output = os.path.join(location, output)
				write_bad(name, output, threshold)


def classifySet(directory, k, knn, gsvm, threshold):
	lst = os.listdir(directory)
	for item in lst:
		if ('recentMedia' in item):
			location = os.path.join(directory, item)
			files = os.listdir(location)
			if('tag_results' not in files):
				# path = os.path.join(location, item)
				classifyTags(location, k, knn, gsvm, threshold)

def classifyTags(folder_name, k, knn, gsvm, threshold):
	lst = os.listdir(folder_name)
	home = os.path.join(os.getcwd(), 'tag_filter')
	# home = os.getcwd() + 'tag_'
	print lst
	bad_list = []
	tag_frac = {}
	count = 0 
	for item in lst:
		direc = item + 'dir'
		direc = os.path.join(home, direc)
		if not os.path.exists(direc):
			os.makedirs(direc)
		total = 0
		path = os.path.join(folder_name, item)
		media_list = pickle.load(open(path, 'rb'))
		success = 0
		for media in media_list:
			url = media.images['standard_resolution'].url
			# print url
			myopener = MyOpener()
			secondHalf = '%d.jpg' % count 
			image_name = os.path.join(direc, secondHalf)
			try:
				myopener.retrieve(url, image_name)
			except urllib.ContentTooShortError:
				print "Content %s too short. Skipping" % url
			except SocketError as e:
				if e.errno != errno.ECONNRESET:
					raise
				print "Reset at %s. Going on " % url
			except IOError:
				print "Cannot find %s. Going on" % url
			print image_name
			if(imghdr.what(image_name) != None):
				try:
					_, des_testing = get_sift_file(image_name)
					if(des_testing != [None]):
						predicted = classify_image(k, knn, des_testing, image_name, gsvm)
						if(predicted[0] < 4):
							success += 1
						total += 1
						print "Found"
				except cv2.error:
					print "Couldn't get, moving on."
			else:
				print "Hi , don't classify"
			count += 1
		compar = 0
		if(total != 0):
			compar = float(success) / float(total)
		print "compare is %f" % compar
		if(compar < threshold):
			bad_list.append(item)
		tag_frac[item] = compar
			# string = "%s \n" % item
			# f.write(string)
	location = os.path.join(folder_name, 'bad_list.txt')
	with open(location, 'wb') as f:
		for elem in bad_list:
			string = "%s \n" % elem
			f.write(string)
	results = os.path.join(folder_name, 'tag_results')
	with open(results, 'wb') as fp:
		json.dump(tag_frac, fp)




def findAndclassifyTags(k, knn, gsvm, json_file,  threshold):
	'''Given a tagList, json_file, finds the images and the attempts to label 
	good tags from bad tags'''
	tagDict = loop_tagsGroup(json_file)
	bad_list = []
	good_list = []
	export = {}
	for key, value in tagDict.iteritems():
		# test = classify_tag
		percent = classify_tag(k, knn, gsvm, key, value, threshold)
		if(percent < threshold ):
			good_list.append(key)
		else:
			bad_list.append(key)
		export[key] = percent
	with open(TAG_FILE, 'wb') as fp:
		json.dump(export, fp, indent=2)
	return good_list, bad_list

def do(json_file):

	knn, svm = train()
	k = 200
	good_list, bad_list = findAndclassifyTags(k, knn, svm, json_file, 0.5)
	print good_list
	print bad_list
	for elem in good_list:
		print "Good list: " + elem
	for thing in bad_list:
		print "Bad list: " + thing

def classify_tag(k, knn, gsvm, tag, img_lst, threshold):
	''' Goes through a tag and it's images, and determines whether a tag is fashion related or not.
	We see if half of the images have a classification label of less than 3 and '''
	total = len(img_lst)
	# success = 0
	success = 0
	# total = 0
	for image_name in img_lst:
		print image_name
		if(imghdr.what(image_name) != None):
			try:
				_, des_testing = get_sift_file(image_name)
				if(des_testing != [None]):
					predicted = classify_image(k, knn, des_testing, image_name, gsvm)
					if(predicted[0] < 4):
						success += 1
					# total += 1
					print "Found"
			except cv2.error:
				print "Couldn't get, moving on."
		else:
			print "Not a valid image, skipping"
	''' Now look as to how many of those iamges were actually fashion related. If the percent is less than the 
	threshold, write the tag to a shadow list '''
	ratio = 0
	if(total != 0):
		ratio = float(success) / float(total)
	return ratio
	# if(float(success)/ float(total) < threshold):
	# 	# with open('shadow_lst', 'a') as fp:
	# 	# 	fp.write(tag)
	# 	return False
	# else:
	# 	# with open('good_tags' as 'a') as fp:
	# 	# 	fp.write(tag)
	# 	return True

if __name__== '__main__':
	# json_knn = sys.argv[1]
	# json_gsvm = sys.argv[2]
	json_data = sys.argv[1]

	# # num_img = int(sys.argv[4])
	knn, svm = train()
	classify(knn, svm, json_data, 5)
	filter32.sort(MOD_FILE, TAG_FILE, 32)
	# classify2(json_data, num_img)


