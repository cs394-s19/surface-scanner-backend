from __future__ import print_function
import os, sys, math, glob
import cv2
import numpy as np
from utilities import ProgressBar
import utilities

ImgPattern = "*.png"
cropRect = [50, 50, -50, -50]

class Image:
    def __init__(self, imgFolder, sessionName):

        self.imgFolder = imgFolder
        self.sessionName = sessionName
        self.PRECISION_IMG = np.dtype(np.float64)
        #self.imgFileList = os.listdir(self.imgFolder)
        self.readFileList()

        self.NumCam = len(self.imgFileList)
        lastImg = self.readKthImg(0)
        [self.height, self.width, self.nColor] = lastImg.shape


        # Img sequences[9]: {v1, v2, v3, v4, h1, h2, h3, h4, full}
        self.imgSet = np.zeros((self.NumCam, self.height, self.width, self.nColor), dtype=np.float32)
        self.imgVSet = np.zeros((4, self.height, self.width), dtype=self.PRECISION_IMG)
        self.imgHSet = np.zeros((4, self.height, self.width), dtype=self.PRECISION_IMG)
        self.imgOnOffSet = np.zeros((2, self.height, self.width), dtype=self.PRECISION_IMG)
        self.setImgSet()
        self.setDirectionalImgSet()
        self.setAlbedo()
        self.setValidRegion()

    def readFileList(self):

        self.imgFileList = glob.glob(os.path.join(self.imgFolder, ImgPattern))
        # self.imgFileList = os.listdir(self.imgFolder)
        #self.imgFileList.remove('.DS_Store') # remove system database log
        self.imgFileList.sort()


    # Read the kth image of the capture set
    def readKthImg(self, k):
        assert (k <= len(self.imgFileList)), (
            'Out of range: cannot get %d in image out of total %d images.', k, len(self.imgFileList))
        # img = cv2.imread(os.path.join(self.imgFolder, self.imgFileList[k]), cv2.IMREAD_COLOR)
        # Because some header issue from Vikas's app, the input image will flip
        img = cv2.flip(cv2.imread(os.path.join(self.imgFolder, self.imgFileList[k]), cv2.IMREAD_COLOR), 1)
        #cv2.imwrite(os.path.join(self.imgFolder, 'test.png'), img)
        # TODO: White balancing the captured image set

        return img

    def setImgSet(self):
        #progress = ProgressBar(self.NumCam, fmt=ProgressBar.FULL)
        print('Loading ImgSet %d Images...' %(self.NumCam))
        # img = self.readKthImg(1)

        for k in range(self.NumCam):
            #progress.current += 1
            #progress()

            img = self.readKthImg(k)
            img.astype(np.float32) # turn image to floating point

            self.imgSet[k, ...] = img #/ 255.0 # normalize the image intensity

        self.imgSet /= np.max(self.imgSet)
        #progress.done()

    def setDirectionalImgSet(self):
        #progress = ProgressBar(self.NumCam, fmt=ProgressBar.FULL)
        #print('Loading ImgSetGray...')
        for n in range(self.NumCam):
            #progress.current += 1
            #progress()
            if n < 4:
                img = cv2.cvtColor(self.imgSet[n, :, :, :], cv2.COLOR_BGR2GRAY)
                self.imgVSet[n, ...] = img.astype(self.PRECISION_IMG)
            elif (n >= 4 and n < 8):
                img = cv2.cvtColor(self.imgSet[n, :, :, :], cv2.COLOR_BGR2GRAY)
                self.imgHSet[(n - 4), ...] = img.astype(self.PRECISION_IMG)
            elif n >= 8:
                # use illumination on and off images to determine valid region
                self.imgOnOffSet[(n - 8), ...] = cv2.cvtColor(self.imgSet[n, :, :, :], cv2.COLOR_BGR2GRAY)

        #progress.done()

    def setValidRegion(self):
        # On Off illumination
        # img = np.abs(self.imgOnOffSet[1, ...] - self.imgOnOffSet[0, ...])

        # compute variance across the phase shift pattern
        # psSet = np.zeros((8, self.height, self.width), dtype=self.PRECISION_IMG)
        # psSet[0:4, ...] = self.imgVSet
        # psSet[4:, ...] = self.imgHSet
        # img = np.var(psSet, axis=0)
        #
        # img[img < maskThreshold] = 0
        #
        # # Mask of non-black pixels (assuming image has a single channel).
        # mask = img > 0
        #
        # # Coordinates of non-black pixels.
        # coords = np.argwhere(mask)
        #
        # # Bounding box of non-black pixels.
        # x0, y0 = coords.min(axis=0)
        # x1, y1 = coords.max(axis=0) + 1  # slices are exclusive at the top

        self.mask = np.array(cropRect)

    def setAlbedo(self):
        self.A = np.mean(self.imgSet, axis=0)

    def exportTexture(self):
        fname = os.path.join(self.imgFolder, self.sessionName + '.jpg')
        img = cv2.flip(self.A, -1)
        cv2.imwrite(fname, (img * 255).astype(np.uint8))