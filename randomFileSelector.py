# USAGE
# python hash_and_search.py --rawdataset rawdataset --cleandataset cleandataset

# import the necessary packages
from imutils import paths
import argparse
import sys
import os
import random
import cv2
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--inputdataset", required=True,
	help="dataset of images to copy over for the model")
ap.add_argument("-c", "--copytodir", required=True,
	help="where we are compying the images to")
ap.add_argument("-n", "--numberoffiles", required=True,
	help="number of files to copy")
args = vars(ap.parse_args())

#for now we are not going to check for dups or clean the input data..
# .just a random selection of the images put into the director
inputdataset = args["inputdataset"]
copytodir = args["copytodir"] 
numberoffiles = int(args["numberoffiles"])
inputdatasetPaths = list(paths.list_images(inputdataset))
print("[INFO] Trying to copy " + str(numberoffiles) + " of files from " + inputdataset + " to " + copytodir)
filesCopied =0

 
for x in range(0, numberoffiles):
    #randomly select  x number of image
    filetocopy = random.choice(inputdatasetPaths)
    
    image = cv2.imread(filetocopy) 

    if image is None:
        continue 
 
    copyfilepath = filetocopy.replace(inputdataset,copytodir)
    print("[INFO] Selected file " + copyfilepath + " to copy to  " + copytodir)

    cv2.imwrite(copyfilepath,image)  
    filesCopied+=1;
 
print("[INFO] Randomly Copied " + str(filesCopied) + " files to " + copytodir)
 