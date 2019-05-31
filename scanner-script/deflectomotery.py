from __future__ import print_function
import os, sys
import cv2
import numpy as np
from Image import Image
from Mesh import Mesh
from utilities import ProgressBar

# Set Parameters
GradMap_filtersize = 49
freq = 1


def setGrad(imgSet, correctPhaseWrap=0.0):

    # Setup Phase Map
    PhaseMap = -1 * np.arctan2((imgSet[0, ...] - imgSet[2, ...]), (imgSet[1, ...] - imgSet[3, ...]))

    if not correctPhaseWrap==0.0:
        PhaseMap = np.angle(np.exp(1j * (PhaseMap - correctPhaseWrap)))

    # Remove offset
    Gradient_off = PhaseMap
    Gradient_off = cv2.GaussianBlur(Gradient_off, (GradMap_filtersize, GradMap_filtersize), ((GradMap_filtersize + 1) / 2))
    Gradient = PhaseMap - Gradient_off

    return Gradient


def deflectomotery(objectName, imgDir):

    Img = Image(imgDir, objectName)

    Gradient_V = setGrad(Img.imgVSet, 3.8)
    Gradient_H = setGrad(Img.imgHSet, 3.8)

    #cv2.imwrite(os.path.join(imgDir, 'GradV.png'), np.array(Gradient_V * 255, dtype=np.uint8))
    #cv2.imwrite(os.path.join(imgDir, 'GradH.png'), np.array(Gradient_H * 255, dtype=np.uint8))

    N = np.zeros((Img.height, Img.width, 3), dtype=Img.PRECISION_IMG)
    N[..., 0] = -Gradient_V / np.sqrt(np.square(Gradient_V) + np.square(Gradient_H) + 1)
    N[..., 1] = -Gradient_H / np.sqrt(np.square(Gradient_V) + np.square(Gradient_H) + 1)
    N[..., 2] = 1 / np.sqrt(np.square(Gradient_V) + np.square(Gradient_H) + 1)

    # crop valid region
    Ncrop = N[Img.mask[0]:Img.mask[2], Img.mask[1]:Img.mask[3]]
    A = Img.A[Img.mask[0]:Img.mask[2], Img.mask[1]:Img.mask[3]]

    [newHeight, newWidth, _] = A.shape

    Nfname = os.path.join(imgDir, 'normal.png')
    # xyz to zyx because of OPENCV BGR order
    cv2.imwrite(Nfname, cv2.cvtColor(np.array((Ncrop + 1) / 2.0 * 255, dtype=np.uint8), cv2.COLOR_RGB2BGR))

    mesh = Mesh(objectName, newHeight, newWidth, Img.mask)
    mesh.setNormal(N)
    mesh.setDepth()
    mesh.setTexture(A)
    mesh.exportOBJ(imgDir, True)


if __name__ == '__main__':

    # Input image order: v1, v2, v3, v4, h1, h2, h3, h4, (Full off, Full on)
    objectName = sys.argv[1]
    imgDir = os.path.normpath(sys.argv[2])
    # imgDir = "./image-scans/"

    deflectomotery(objectName, imgDir)