import cv2
import numpy as np

cap = cv2.VideoCapture(1)

while True:
    _, frame = cap.read()
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
     
    lower = np.array([1, 165, 215])
    high = np.array([21, 185, 295])

    mask = cv2.inRange(hsv_frame, lower, high)
    color = cv2.bitwise_and(frame, frame, mask=mask)
    contours,_  = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    for pic, contour in enumerate(contours):
        approx = cv2.approxPolyDP(contour, 0.03*cv2.arcLength(contour, True), True)
        x = approx.ravel()[0]
        y = approx.ravel()[1]
        if len(contours) > 2:
            cv2.putText(frame,"DROP ZONE", (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 0.7,(0,0,255))

    cv2.imshow("Frame", frame)
    cv2.imshow("Color", color)
    key = cv2.waitKey(1)
    if key == 27:
        break