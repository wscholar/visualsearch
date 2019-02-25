# USAGE
# python hash_and_search.py --rawdataset rawdataset --cleandataset cleandataset

# import the necessary packages
from imutils import paths
import argparse
import time
import sys
import cv2
import os
import pprint

def dhash(image, hashSize=8):
	# resize the input image, adding a single column (width) so we
	# can compute the horizontal gradient
	resized = cv2.resize(image, (hashSize + 1, hashSize))

	# compute the (relative) horizontal gradient between adjacent
	# column pixels
	diff = resized[:, 1:] > resized[:, :-1]

	# convert the difference image to a hash
	return sum([2 ** i for (i, v) in enumerate(diff.flatten()) if v])

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-a", "--rawdataset", required=True,
	help="dataset of images to search through (i.e., the haytack)")
ap.add_argument("-n", "--cleandataset", required=True,
	help="set of images we are searching for (i.e., cleandataset)")
args = vars(ap.parse_args())

rawpathBase = args["rawdataset"]
cleanpathBase = args["cleandataset"] 

# grab the paths to both the rawdataset and cleaned images 
print("[INFO] computing hashes for rawdataset...")
rawdatasetPaths = list(paths.list_images(args["rawdataset"]))
cleanPaths = list(paths.list_images(args["cleandataset"]))

# remove the `\` character from any filenames containing a space
# (assuming you're executing the code on a Unix machine)
if sys.platform != "win32":
	rawdatasetPaths = [p.replace("\\", "") for p in rawdatasetPaths]
	cleanPaths = [p.replace("\\", "") for p in cleanPaths]

rawdatasetPaths.sort()
cleanPaths.sort()
# initialize the dictionary that will map the image hash to corresponding image,
# hashes, then start the timer

rawdataset = {}
cleandataset = {}
pathsforcleanimage = {}
start = time.time()

totalRawFiles=0
totalCleanedFiles=0

# loop over the rawdataset paths
for p in rawdatasetPaths:
	# load the image from disk
	image = cv2.imread(p) 
	# if the image is None then we could not load it from disk (so
	# skip it...should have already been tested when we rean the download script)
	if image is None:
		continue

	# convert the image to grayscale and compute the hash
	image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	imageHash = dhash(image)

	# update the rawdataset dictionary
	l = rawdataset.get(imageHash, [])
	l.append(p)
	rawdataset[imageHash] = l
    
	#for writing the image to cleaned later
	pathsforcleanimage[imageHash] = p
	totalRawFiles +=1

# show timing for hashing rawdataset images, then start computing the
# hashes for cleaned images
print("[INFO] loaded {} images in {:.2f} seconds".format(
	len(rawdataset), time.time() - start))
print("[INFO] computing hashes for cleandataset...")
cleanSubDir="" 

#build hash of all cleanpath files
for x in cleanPaths:
	image = cv2.imread(x) 
	# if the image is None then we could not load it from disk (so
	# skip it)
	if image is None:
		continue

	# convert the image to grayscale and compute the hash
	image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	imageHash = dhash(image)  

	l = cleandataset.get(imageHash, [])
	l.append(x)
	cleandataset[imageHash] = l 



#  loop over rawdataset dic andcheck to see if we have an image in the cleandataset that is a duplicate
for rawImageHash in rawdataset:
	# check if the hash is matched in cleandataset if not added it.
	# loop over the cleaned paths ...should only compare to path of same sub dir
	rawpath = pathsforcleanimage.get(rawImageHash) 
	cleanpath = rawpath.replace(rawpathBase,cleanpathBase)
	cleanSubDir = cleanpathBase + "/" + cleanpath.split(os.path.sep)[-2]

	# Check if file is already in clean dir
	if os.path.exists(cleanpath): 
		print("[INFO] Skipping file already on cleanpath.." + cleanpath)
		continue 
	
	print("[INFO] checking   directory on cleanpath.." + cleanSubDir)
	if not os.path.exists(cleanSubDir): 
		os.makedirs(cleanSubDir)
		print("[INFO] Given we created this directory write these image on cleanpath we know it's not a dub.." + cleanpath)
		image = cv2.imread(rawpath)
		cv2.imwrite(cleanpath,image)  
		#add to the cleandataset hashmap
		l = cleandataset.get(rawImageHash, [])
		l.append(cleanpath)
		cleandataset[rawImageHash] = l   
		totalCleanedFiles +=1
		continue

	# see if image is a duplicate match in the rawdataset hash
	print("[INFO] checking to for match..." + cleanpath)
	matchedImage = cleandataset.get(rawImageHash, [])
	  
	if not matchedImage:
		#write the image to the cleandataset directory
		print("[INFO] Writing this image from raw directory..." + rawpath)
		image = cv2.imread(rawpath) 
		print("[INFO] Writing this image to cleanpath.." + cleanpath)
		cv2.imwrite(cleanpath,image)
		#add to the cleandataset hashmap
		l = cleandataset.get(rawImageHash, [])
		l.append(cleanpath)
		cleandataset[rawImageHash] = l  
		totalCleanedFiles +=1

 
# TODO check if hash is too different and don't insert those as they are outlyers...
 
print("[INFO] All Done in {:.2f} seconds".format(time.time() - start)) 
print("[INFO] Total Raw Files Looked at.." + str(totalRawFiles))
print("[INFO] Total Clean Files written (dedupped).." + str(totalCleanedFiles))