import cv2
import numpy as np
cap = cv2.VideoCapture(0)
while True:
    ret, frame = cap.read()

    # blurred the image with gaussian blur
    blurred_frame = cv2.GaussianBlur(frame, (5, 5), 0)

    # define color in HSV
    lower_blue = np.array([101,157,0])
    upper_blue = np.array([111,255,255])

    lower_red = np.array([166, 84, 141])
    upper_red = np.array([186,255,255])

    lower_green = np.array([40,176,0])
    upper_green = np.array([80,255,255])

    # Convert BGR to HSV
    hsv = cv2.cvtColor(blurred_frame, cv2.COLOR_BGR2HSV)

    # Threshold the HSV image to get only specific colors
    red = cv2.inRange(hsv, lower_red, upper_red)
    blue = cv2.inRange(hsv, lower_blue, upper_blue)
    green = cv2.inRange(hsv, lower_green, upper_green)

    _,redThreshold = cv2.threshold(red, 240, 255, cv2.THRESH_BINARY)
        
    _,blueThreshold = cv2.threshold(blue, 240, 255, cv2.THRESH_BINARY)

    _,greenThreshold = cv2.threshold(green, 240, 255, cv2.THRESH_BINARY)

    contours,_ = cv2.findContours(redThreshold,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    for pic, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        approx = cv2.approxPolyDP(contour, 0.02*cv2.arcLength(contour, True), True)
        x = approx.ravel()[0]
        y = approx.ravel()[1]
        if(area>300): #for removing small noises
            cv2.drawContours(frame, [approx], 0, (0,0,255), 3)
            cv2.putText(frame,"RED color",(x,y),cv2.FONT_HERSHEY_SIMPLEX, 0.7,(0,0,255))
            if len(approx) == 3:
                cv2.putText(frame, "          TRIANGLE", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7,(0,0,255))
            elif len(approx) == 4:
                cv2.putText(frame, "          RECTANGLE", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7,(0,0,255))
            elif 10 < len(approx) < 20:
                cv2.putText(frame, "          CIRCLE", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7,(0,0,255))      

    contours,_ = cv2.findContours(greenThreshold,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    for pic, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        approx = cv2.approxPolyDP(contour, 0.02*cv2.arcLength(contour, True), True)
        x = approx.ravel()[0]
        y = approx.ravel()[1]
        if(area>400): #for removing small noises
            cv2.drawContours(frame, [approx], 0, (0,255,0), 3)
            cv2.putText(frame,"GREEN color",(x,y),cv2.FONT_HERSHEY_SIMPLEX, 0.7,(0,255,0))
            if len(approx) == 3:
                cv2.putText(frame, "            TRIANGLE", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7,(0,255,0))
            elif len(approx) == 4:
                cv2.putText(frame, "            RECTANGLE", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7,(0,255,0))
            elif 10 < len(approx) < 20:
                cv2.putText(frame, "            CIRCLE", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7,(0,255,0))


    contours,_ = cv2.findContours(blueThreshold,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    for pic, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        approx = cv2.approxPolyDP(contour, 0.02*cv2.arcLength(contour, True), True)
        x = approx.ravel()[0]
        y = approx.ravel()[1]
        if(area>500):
            cv2.drawContours(frame, [approx], 0, (255,0,0), 3)
            cv2.putText(frame,"BLUE color",(x,y),cv2.FONT_HERSHEY_SIMPLEX, 0.7,(255,0,0))
            if len(approx) == 3:
                cv2.putText(frame, "            TRIANGLE", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7,(255,0,0))
            elif len(approx) == 4:
                cv2.putText(frame, "            RECTANGLE", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7,(255,0,0))
            elif 10 < len(approx) < 20:
                cv2.putText(frame, "            CIRCLE", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7,(255,0,0))
            

    cv2.imshow('red',redThreshold)
    cv2.imshow('green',greenThreshold)
    cv2.imshow('blue',blueThreshold)
    cv2.imshow('frame',frame)
    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break
cv2.destroyAllWindows()