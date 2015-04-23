#!/usr/bin/env python
import cv2
import numpy as np
import os
import sys
from matplotlib import pyplot as plt

from modshogun import *


def get_stock(input_dir):
    # input_dir = '/home/aditya/SchoolWork/cs145/fashiontrending/images/detection/data_images/stock'
    img_mat = []
    sift = cv2.SIFT()
    for filename in os.listdir(input_dir):
        path = os.path.join(input_dir, filename)
        img = cv2.imread(path)
      #  print img
        img = cv2.resize(img, (500, 300), interpolation = cv2.INTER_AREA)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)

        kp, des = sift.detectAndCompute(gray, None)
        img_mat.append(des)
    return img_mat


def get_images(input_dir):
    # print input_dir
    img_mat = []
    sift = cv2.SIFT()
    # print os.listdir(input_dir)
    for filename in os.listdir(input_dir):
        # print filename
        path = os.path.join(input_dir, filename)
        img = cv2.imread(path)
      #  print img
        img = cv2.resize(img, (500, 300), interpolation = cv2.INTER_AREA)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)

        kp, des = sift.detectAndCompute(gray, None)
        img_mat.append(des)
    return img_mat



def get_similar(k, img_mat):
	img_mat = np.double(np.vstack(img_mat))
	img_mat = img_mat.T

	sg_img_mat_features = RealFeatures(img_mat)

	distance = EuclideanDistance(sg_img_mat_features, sg_img_mat_features)

	kmeans = KMeans(k, distance)
	kmeans.train()
	cluster_centers = (kmeans.get_cluster_centers())
	return cluster_centers 


def get_sift_training(input_dir):
	folders = ['fashion', 'not_fashion']

	des_training = []
	folder_number = -1
	print folders
	for folder in folders:
		folder_name = input_dir + "/%s" % folder
		#filenames = get_imlist()
        	print folder_name
		#filenames = np.array(filenames)
        #	 print 'Folder name is %s ' % folder_name
        	des_training.append(get_images(folder_name))
	return des_training


def compute_training_data(k, cluster_centers, descriptors, input_dir):
    
    # a list to hold histograms of all the training images
    all_histograms=[]
    # labels for all of the test images
    final_labels=[]
    # to hold the cluster number a descriptor belong to
    cluster_labels=[]

    #initialize a KNN in Shogun
    dist=EuclideanDistance()
    labels=MulticlassLabels(np.double(range(k)))
    knn=KNN(1, dist, labels)

    #Target descriptors are the cluster_centers that we got earlier. 
    #All the descriptors of an image are matched against these for 
    #calculating the histogram.
    sg_cluster_centers=RealFeatures(cluster_centers)
    knn.train(sg_cluster_centers)

    # name of all the folders together
    folders=['fashion', 'not_fashion']
    folder_number=-1

    for folder in folders:
        folder_number+=1

        #get all the training images from a particular class 
        directory = input_dir + "/%s " % folder
        im_list = -1
        for image_name in os.listdir(input_dir):
            im_list += 1
            
            des=descriptors[folder_number][im_list]
            
            #Shogun works in a way in which columns are samples and rows are features.
            #Hence we need to transpose the observation matrix
            des=(np.double(des)).T
            sg_des=RealFeatures(np.array(des))

            #find all the labels of cluster_centers that are nearest to the descriptors present in the current image. 
            cluster_labels=(knn.apply_multiclass(sg_des)).get_labels()

            histogram_per_image=[]
            for i in xrange(k):
                #find the histogram for the current image
                histogram_per_image.append(sum(cluster_labels==i))

            all_histograms.append(np.array(histogram_per_image))
            final_labels.append(folder_number)

    # we now have the training features(all_histograms) and labels(final_labels) 
    all_histograms=np.array(all_histograms)
    final_labels=np.array(final_labels)
    return all_histograms, final_labels, knn

def train_svm(all_histograms, final_labels):
    
    # we will use GMNPSVM class of Shogun for one vs rest multiclass classification
    obs_matrix=np.double(all_histograms.T)
    sg_features=RealFeatures(obs_matrix)
    sg_labels=MulticlassLabels(np.double(final_labels))
    kernel=LinearKernel(sg_features, sg_features)
    C=1
    gsvm=GMNPSVM(C, kernel, sg_labels)
    _=gsvm.train(sg_features)
    return gsvm

def classify_svm(k, knn, des_testing, input_dir):
    
    # a list to hold histograms of all the test images
    all_histograms=[]
    filenames=get_imlist(input_dir)
    
    for image_name in xrange(len(filenames[0])):
        
        result=[]
        des=des_testing[image_name]
        
        #Shogun works in a way in which columns are samples and rows are features.
        #Hence we need to transpose the observation matrix
        des=(np.double(des)).T
        sg_des=RealFeatures(np.array(des))

        #cluster all the above found descriptors into the vocabulary
        cluster_labels=(knn.apply_multiclass(sg_des)).get_labels()

        #get the histogram for the current test image
        histogram=[]
        for i in xrange(k):
            histogram.append(sum(cluster_labels==i))
        
        all_histograms.append(np.array(histogram))

    all_histograms=np.double(np.array(all_histograms))
    all_histograms=all_histograms.T
    sg_testfeatures=RealFeatures(all_histograms)
    return gsvm.apply(sg_testfeatures).get_labels()


if __name__== '__main__':
	input_dir = sys.argv[1]
	stock_dir = sys.argv[2]
	stand = get_stock(stock_dir)
	center = get_similar(2, stand)
	img_mat = get_sift_training(input_dir)
	k = 100
	all_histograms, final_labels, knn = compute_training_data(2, center, img_mat, input_dir)
	train_svm(all_histograms, final_labels)
