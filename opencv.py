import cv2
import numpy as np
cap = cv2.VideoCapture(0)
while True:
    ret, frame = cap.read()
    # blurred the image with gaussian blur
    blurred_frame = cv2.GaussianBlur(frame, (5, 5), 0)
    # Convert BGR to HSV
    hsv = cv2.cvtColor(blurred_frame, cv2.COLOR_BGR2HSV)

    colors = {'Red color':(0,0,255), 'Green color':(0,179,0), 'Blue color':(255,0,0)}
    lower = {'Red color':(166, 84, 141), 'Green color':(65,60,60), 'Blue color':(97, 100, 117)}
    upper = {'Red color':(186,255,255), 'Green color':(80,255,255), 'Blue color':(111,255,255)}
    
    for key, value in upper.items():
        kernel = np.ones((7,7),np.uint8)
        PrimaryMask = cv2.inRange(hsv, lower[key], upper[key])
        mask = cv2.morphologyEx(PrimaryMask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(PrimaryMask, cv2.MORPH_CLOSE, kernel)
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
                    center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                    cv2.drawContours(frame, [approx], -1, colors[key], 2)
                    cv2.circle(frame, center, 3, (0, 0, 0), 2) 
                    print center
                    cv2.putText(frame,key,(int(x), int(y)),cv2.FONT_HERSHEY_SIMPLEX, 0.7,colors[key])
                    if len(approx) == 3:
                        cv2.putText(frame,"            TRIANGLE", (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 0.7,colors[key])
                    elif len(approx) == 4:
                        cv2.putText(frame,"            RECTANGLE", (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 0.7,colors[key])
                    elif 10 < len(approx) < 20:
                        cv2.putText(frame,"            CIRCLE", (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 0.7,colors[key])

    cv2.imshow('warna',mask)
    cv2.imshow('frame',frame)
    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break
cv2.destroyAllWindows()