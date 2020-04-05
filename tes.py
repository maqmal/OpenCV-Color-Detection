from collections import deque 
import io
import time

#import picamera
import cv2 
import numpy as np

cap = cv2.VideoCapture(0)

while(1):
    # Take each frame%
    _, frame = cap.read() 

    # Convert BGR to HSV


    #defined blue

    lower_blue = np.array([110, 50, 60], dtype=np.uint8)
    upper_blue = np.array([130,255,255], dtype=np.uint8)
    blue = [lower_blue, upper_blue, 'blue']

    #defined red
    lower_red = np.array([160, 90, 50], dtype=np.uint8)
    upper_red = np.array([179,255,255], dtype=np.uint8)
    red = [lower_red, upper_red, 'red']


    #defined green
    lower_green = np.array([60, 110, 60], dtype=np.uint8)
    upper_green = np.array([160,255,255], dtype=np.uint8)
    green = [lower_green, upper_green, 'green']


    #defined yellow
    lower_yellow = np.array([5, 110, 100], dtype=np.uint8)
    upper_yellow = np.array([50, 255, 255], dtype=np.uint8)
    yellow = [lower_yellow, upper_yellow, 'yellow']





    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)




    if  blue:
        print ("blue")
    # Threshold the HSV image to get only blue colors mask = cv2.inRange(hsv, lower_blue, upper_blue)

    # Bitwise-AND mask and original image
        res = c v2.bitwise_and(frame,frame, mask= mask)
        #------------------------------------------------------------------------------#
        # define range of red color in HSV

    elif red:
        print ("red")
        # Threshold the HSV image to get only red colors
        mask = cv2.inRange(hsv, lower_red, upper_red)

        # Bitwise-AND mask and original image
        res = cv2.bitwise_and(frame,frame, mask= mask)
#        -------------------------------------------------------------------------------
        # define range of green color in HSV

    elif green:
        print ("green")
        # Threshold the HSV image to get only green colors
        mask = cv2.inRange(hsv, lower_green, upper_green)

        # Bitwise-AND mask and original image
        res = cv2.bitwise_and(frame,frame, mask= mask)
#        -------------------------------------------------------------------------------------
    elif yellow:
            print ("yellow")
    # Threshold the HSV image to get only green colors
            mask = cv2.inRange(hsv,lower_yellow, upper_yellow )

    # Bitwise-AND mask and original image
            res = cv2.bitwise_and(frame,frame, mask= mask)



    cv2.imshow('frame',frame)
    cv2.imshow('mask',mask)
    cv2.imshow('res',res)
    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break
    cv2.destroyAllWindows()