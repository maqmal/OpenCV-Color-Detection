import cv2
import numpy as np
cap = cv2.VideoCapture(0)
while True:

    ret, img = cap.read()
    img_hsv=cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # colors = { 'red0 color':(0,0,255), 'red1 color':(0,0,255)}
    # lower = {'red0 color':(0,50,50), 'red1 color':(170,50,50)}
    upper = {'red0 color':(10,255,255), 'red1 color':(180,255,255)}
    # lower mask (0-10)
    lower_red = np.array([0,50,50])
    upper_red = np.array([10,255,255])
    mask0 = cv2.inRange(img_hsv, lower_red, upper_red)
    # upper mask (170-180)
    lower_red = np.array([170,50,50])
    upper_red = np.array([180,255,255])
    mask1 = cv2.inRange(img_hsv, lower_red, upper_red)
    
    for key, value in upper.items():
        kernel = np.ones((7,7),np.uint8)
        mask = mask0+mask1
        center = None
        contours,_  = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        for pic, contour in enumerate(contours):
            approx = cv2.approxPolyDP(contour, 0.02*cv2.arcLength(contour, True), True)
            x = approx.ravel()[0]
            y = approx.ravel()[1]
            if len(contours) > 0:
                area = cv2.contourArea(contour)
                c = max(contours, key=cv2.contourArea)
                ((x, y), radius) = cv2.minEnclosingCircle(c)
                if(area>300): #for removing small noises
                    M = cv2.moments(c)
                    if len(approx) == 4:
                        cv2.putText(img,"            RECTANGLE", (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 0.7,(0,0,255))
                        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                        cv2.drawContours(img, [approx], -1, upper[key], 2)
                        cv2.circle(img, center, 3, (0, 0, 0), 2) 
    cv2.imshow('warna',mask)
    cv2.imshow('frame',img)
    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break
cv2.destroyAllWindows()