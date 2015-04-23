from instagram.client import InstagramAPI
import pickle
import urllib

'''Loading fashion data'''
lst = pickle.load(open('/home/aditya/SchoolWork/cs145/fashiontrending/data/fashion', 'rb'))
for i in range(0, 5):
	url = lst[i].images['standard_resolution']
	urllib.urlretrieve(url, 'data_images/0000%d.jpg' %i)
