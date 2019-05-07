import cv2
import numpy as np
cap = cv2.VideoCapture(0)
while(1):
    ret, frame = cap.read()

    # Convert BGR to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # define color in HSV
    lower_blue = np.array([101,157,0])
    upper_blue = np.array([111,255,255])

    lower_red = np.array([133,142,0])
    upper_red = np.array([180,255,255])

    lower_green = np.array([40,176,0])
    upper_green = np.array([80,255,255])

    # Threshold the HSV image to get only specific colors
    red = cv2.inRange(hsv, lower_red, upper_red)
    blue = cv2.inRange(hsv, lower_blue, upper_blue)
    green = cv2.inRange(hsv, lower_green, upper_green)

    # Bitwise-AND mask and original image
    kernal= np.ones((5 ,5), "uint8") #kernal is created of 5x5
    red=cv2.dilate(red, kernal)

    res=cv2.bitwise_and(frame, frame, mask = red)
    blue=cv2.dilate(blue,kernal)

    res1=cv2.bitwise_and(frame, frame, mask = blue)
    green=cv2.dilate(green,kernal)

    res2=cv2.bitwise_and(frame, frame, mask = green)

    contours,hierarchy = cv2.findContours(red,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    for pic, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        if(area>300): #for removing small noises
            x,y,w,h = cv2.boundingRect(contour)
            frame = cv2.rectangle(frame,(x,y),(x+w,y+h),(0,0,255),2)
            cv2.putText(frame,"RED color",(x,y),cv2.FONT_HERSHEY_SIMPLEX, 0.7,(0,0,255))

    contours,hierarchy = cv2.findContours(green,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    for pic, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        if(area>300): #for removing small noises
            x,y,w,h = cv2.boundingRect(contour)
            frame = cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
            cv2.putText(frame,"GREEN color",(x,y),cv2.FONT_HERSHEY_SIMPLEX, 0.7,(0,255,0))

    contours,hierarchy = cv2.findContours(blue,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    for pic, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        if(area>300): #for removing small noises
            x,y,w,h = cv2.boundingRect(contour)
            frame = cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)
            cv2.putText(frame,"BLUE color",(x,y),cv2.FONT_HERSHEY_SIMPLEX, 0.7,(255,0,0))

    cv2.imshow('res',res)
    cv2.imshow('res1',res1)
    cv2.imshow('res2',res2)
    cv2.imshow('frame',frame)
    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break
cv2.destroyAllWindows()