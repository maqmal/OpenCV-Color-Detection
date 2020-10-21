import cv2
import numpy as np

cap = cv2.VideoCapture(0)

kernelOpen=np.ones((5,5))
kernelClose=np.ones((20,20))

# 65,60,60
# 80,255,255

lower = np.array([65,60,60])
high = np.array([80,255,255])

color_threshold = 40

while True:
    _, frame = cap.read()
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
     
    mask = cv2.inRange(hsv_frame, lower, high)

    sum_of_color = np.sum(mask)
    exceed_threshold = sum_of_color > color_threshold

    color = cv2.bitwise_and(frame, frame, mask=mask)

    maskOpen=cv2.morphologyEx(mask,cv2.MORPH_OPEN,kernelOpen)
    maskClose=cv2.morphologyEx(maskOpen,cv2.MORPH_CLOSE,kernelClose)
    contours,_  = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    for pic, contour in enumerate(contours):
        if (len(contours)>0):
            maxContour = len(contours)
            maxIndex = 0
        for i in range (len(contours)):
            if (len(contours[i]) > maxContour):
                maxContour = len(contours[i])
                maxIndex = i
            M = cv2.moments(contours[maxIndex])
        if (M["m00"] != 0):
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
        cv2.circle(frame, (cX, cY), 2, (0, 0, 255), -1) #Draw center of object
        cv2.drawContours(frame,contours,-1,(0,255,0),1) #Draw contour of object
        color_area = max(contours, key=cv2.contourArea)
        (xg,yg,wg,hg) = cv2.boundingRect(color_area)
        cv2.rectangle(frame,(xg,yg),(xg+wg, yg+hg),(0,255,0),2)
        frame = cv2.putText(frame, 'Drop Zone Detected', (10,50), cv2.FONT_HERSHEY_SIMPLEX ,  1, (0, 0, 255), 1, cv2.LINE_AA)

    cv2.namedWindow("Frame", cv2.WND_PROP_FULLSCREEN)          
    cv2.setWindowProperty("Frame", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.imshow("Frame", frame)
    #cv2.imshow("Color", color)
    key = cv2.waitKey(1)
    if key == 27:
        break