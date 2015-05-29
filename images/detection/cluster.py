#!/usr/bin/env python
import cv2
import numpy as np
import os
import sys
from matplotlib import pyplot as plt
import imghdr

import pickle

from modshogun import *

from shogun.IO import SerializableAsciiFile

def get_imlist(path):
    return [[os.path.join(path,f) for f in os.listdir(path) if (f.endswith('.jpg') or f.endswith('.png'))]]

def get_stock():
    filenames=get_imlist('data_images/stock')
    filenames=np.array(filenames)

    # for keeping all the descriptors from the template images
    descriptor_mat=[]

    # initialise OpenCV's SIFT
    sift=cv2.SIFT()

    for image_no in xrange(len(filenames[0])):
        img=cv2.imread(filenames[0][image_no])
        img=cv2.resize(img, (500, 300), interpolation=cv2.INTER_AREA)
        gray=cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray=cv2.equalizeHist(gray)
        
        #detect the SIFT keypoints and the descriptors.
        kp, des=sift.detectAndCompute(gray,None)
        # store the descriptors.
        descriptor_mat.append(des)    
        return descriptor_mat


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



def get_similar_descriptors(k, descriptor_mat):

    descriptor_mat=np.double(np.vstack(descriptor_mat))
    descriptor_mat=descriptor_mat.T

    #initialize KMeans in Shogun 
    sg_descriptor_mat_features=RealFeatures(descriptor_mat)

    #EuclideanDistance is used for the distance measurement.
    distance=EuclideanDistance(sg_descriptor_mat_features, sg_descriptor_mat_features)

    #group the descriptors into k clusters.
    kmeans=KMeans(k, distance)
    kmeans.train()

    #get the cluster centers.
    cluster_centers=(kmeans.get_cluster_centers())
    
    return cluster_centers


def get_sift_training():
    folders=['selfie', 'single' ,'group', 'fashion_items', 'food', 'outdoors', 'pets', 'gadgets', 'captioned' ]
    sift = cv2.SIFT()

    
    folder_number=-1
    des_training=[]
      
    for folder in folders:
        folder_number+=1

        #get all the training images from a particular class 
        filenames=get_imlist('data_images/training/%s'%folder)
        filenames=np.array(filenames)
        
        des_per_folder=[]
        for image_name in filenames[0]:
            img=cv2.imread(image_name)

            # carry out normal preprocessing routines
            gray= cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
            gray=cv2.resize(gray, (500, 300), interpolation=cv2.INTER_AREA)
            gray=cv2.equalizeHist(gray)

            #get all the SIFT descriptors for an image
            _, des=sift.detectAndCompute(gray, None)
            des_per_folder.append(des)
    
        des_training.append(des_per_folder)
    return des_training
def compute_training_data(k, cluster_centers, descriptors):
    
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
    folders=['selfie', 'single', 'group', 'fashion_items', 'food', 'outdoors', 'pets', 'gadgets', 'captioned' ]
    folder_number=-1
    for folder in folders:
        folder_number+=1

        #get all the training images from a particular class 
        filenames=get_imlist('data_images/training/%s'%folder)

        for image_name in xrange(len(filenames[0])):
            des=descriptors[folder_number][image_name]
            
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


def get_sift_testing(folder):

    testing_sample = []
    filenames=get_imlist(folder)
    for i in xrange(len(filenames[0])):
        temp=cv2.imread(filenames[0][i])
        testing_sample.append(temp)

    filenames=np.array(filenames)
    des_testing=[]
    for image_name in filenames[0]:
        result=[]
        #read the test image
        img=cv2.imread(image_name)

        #follow the normal preprocessing routines 
        gray= cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        gray=cv2.resize(gray, (500, 300), interpolation=cv2.INTER_AREA)
        gray=cv2.equalizeHist(gray)

        sift = cv2.SIFT()


        #compute all the descriptors of the test images
        _, des=sift.detectAndCompute(gray, None)
        des_testing.append(des)
    return testing_sample, des_testing

def get_sift_file(filename):
    
    
    testing_sample = []
    # testing_sample.append(cv2.imread(filename))
    temp = cv2.imread(filename)
    testing_sample.append(temp)
    arr = np.array(filename)
    des_testing = []
    img = cv2.imread(filename)
    gray= cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    gray=cv2.resize(gray, (500, 300), interpolation=cv2.INTER_AREA)
    gray=cv2.equalizeHist(gray)
    sift = cv2.SIFT()

        #compute all the descriptors of the test images
    _, des=sift.detectAndCompute(gray, None)
    des_testing.append(des)
    return testing_sample, des_testing

def classify_image(k, knn, des_testing, filename, gsvm):
    all_histograms=[]
    image_name = filename
    # des = des_testing[0]
    des = des_testing[0]
    # print des_testing
    des=(np.float64(des)).T
    #cluster all the above found descriptors into the vocabulary
    sg_des=RealFeatures((des))
    # print sg_des
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



def classify_svm(k, knn, des_testing, folder, gsvm):
    
    # a list to hold histograms of all the test images
    all_histograms=[]
    filenames=get_imlist('data_images/testing')    
    for image_name in xrange(len(filenames[0])):
        
        result=[]
        des=des_testing[image_name]
        
        #Shogun works in a way in which columns are samples and rows are features.
        #Hence we need to transpose the observation matrix
        des=(np.float64(des)).T
        #cluster all the above found descriptors into the vocabulary
        sg_des=RealFeatures(np.array(des))
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


def create_conf_matrix(expected, predicted, n_classes):
    m = [[0] * n_classes for i in range(n_classes)]
    for pred, exp in zip(predicted, expected):
        m[exp][int(pred)] += 1
    return np.array(m)

def create_expected():
    filenames=get_imlist('data_images/testing')
    # get the formation of the files, later to be used for calculating the confusion matrix
    formation=([int(''.join(x for x in filename if x.isdigit())) for filename in filenames[0]])
        
    # associate them with the correct labels by making a dictionary
    keys=range(len(filenames[0]))

    values=[0, 2, 0, 2, 2, 2, 2, 2, 1, 0, 2, 2, 2, 2, 2, 1, 2, 2, 2, 0, 2, 2, 2, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 1, 0, 2, 2, 2, 2, 2, 0, 0, 2, 2, 2, 0, 2, 5, 0, 2, 0, 0, 2, 1, 2, 2, 0, 2, 2, 1, 2, 0, 2, 2, 2, 2, 2, 2, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 6, 0, 3, 0, 0, 5, 0, 0, 0, 4, 6, 6, 0, 0, 0, 0, 0, 6, 0, 1, 0, 0, 1, 4, 4, 4, 2, 0, 2, 6, 0, 2, 6, 1, 0, 0, 0, 3, 0, 6, 5, 6, 1, 6, 4, 6, 1, 0, 0, 0, 1, 6, 2, 2, 6, 4, 4, 2, 1, 2, 4, 2, 0]
    label_dict=dict(zip(keys, values))

    # the following list holds the actual labels
    expected=[]
    for i in formation:
        expected.append(label_dict[i-1])
    return expected

def showfig(image, ucmap):


    #There is a difference in pixel ordering in OpenCV and Matplotlib.
    #OpenCV follows BGR order, while matplotlib follows RGB order.
    if len(image.shape)==3 :
        b,g,r = cv2.split(image)       # get b,g,r
        image = cv2.merge([r,g,b])     # switch it to rgb
    imgplot=plt.imshow(image, ucmap)
    imgplot.axes.get_xaxis().set_visible(False)
    imgplot.axes.get_yaxis().set_visible(False)

def plotting(best_prediction, testing_sample):
    filenames=get_imlist('data_images/testing')    
    plt.rcParams['figure.figsize']=50, 10
    fig=plt.figure()
    folders=['selfie', 'single' ,'group', 'fashion_items', 'food', 'outdoors', 'pets', 'gadgets', 'captioned' ]
    for image_no in xrange(40):
        print image_no
        fig.add_subplot(4,10, image_no+1)
        image_no = image_no + 45
        plt.title(folders[int(best_prediction[image_no])])
        showfig(testing_sample[image_no], None)
    plt.show()


def main():
    descriptors = get_stock()
    k = 200
    center = get_similar_descriptors(k, descriptors)
    img_mat = get_sift_training()
    all_histograms, final_labels, knn = compute_training_data(k, center, img_mat)
    gsvm = train_svm(all_histograms, final_labels)
    testing_sample, test_set = get_sift_testing('data_images/testing')
    predicted = classify_svm(k , knn, test_set, 'data_images/testing', gsvm)

def train():
    descriptors = get_stock()
    k = 200
    center = get_similar_descriptors(k, descriptors)
    img_mat = get_sift_training()
    all_histograms, final_labels, knn = compute_training_data(k, center, img_mat)
    gsvm = train_svm(all_histograms, final_labels)
    fstream = SerializableAsciiFile("svm", "w")
    status = gsvm.save_serializable(fstream)
    assert(status)

    fstream2 = SerializableAsciiFile("knn", 'w')
    status2 = knn.save_serializable(fstream2)
    assert(status2)
    return knn, gsvm


if __name__== '__main__':
    main()
	# expected = create_expected()
	# accuracy=sum(predicted==expected)*100/float(len(expected))
	# print "for a k=%d, accuracy is %d%%"%(k, accuracy)
