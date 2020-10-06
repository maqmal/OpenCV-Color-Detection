# Note: Before running this code, run "taskset 0x1 sudo pigpiod" 
# in the command prompt to enable hardwarePWM

# Import libaries
from multiprocessing import Process, Queue, Value, Lock, Array
import RPi.GPIO as GPIO # Import GPIO library
import time   # Import time library for time control
import sys
import numpy as np
import pigpio
import cv2
from datetime import datetime

# Set GPIO Pins to be referred in Broadcom SOC channel
GPIO.setmode(GPIO.BCM)
motorPinR = 13
pi_hw = pigpio.pi() #connect to pi gpio Daemon
pi_hw.hardware_PWM(motorPinR, 50, 80000)
print "CALIBRATING..."
time.sleep(3)
currentDirectionR = 80000

def rotate5 (direction, strength): #1 is turn cloclwise, strength from 1 to 5 
    global currentDirectionR
    fullRight = 35000.0
    fullLeft = 130000.0
    increment = (fullLeft - fullRight) / 150.0
    if direction == 1:
        currentDirectionR = currentDirectionR - strength*increment
        if currentDirectionR < fullRight:
            currentDirectionR = fullRight
    elif direction ==0:
        pi_hw.hardware_PWM(motorPinR, 50, 0) #50 Hz Freq. 0% duty cycle
        pi_hw.hardware_PWM(motorPinT, 50, 0) #50 Hz Freq. 0% duty cycle
    else:
        currentDirectionR = currentDirectionR + strength*increment
        if currentDirectionR > fullLeft:
            currentDirectionR = fullLeft
    pi_hw.hardware_PWM(motorPinR, 50, currentDirectionR)
    #current_direction (in percent DD) /100 * 1000000
    #print ("Rotation Direction ", currentDirectionR)
    
# Function for the Master Process
def grab_frame_display(run_flag, send_frame_queue, receive_contour_queue, p_start_turn, p_end_turn, p_start_lock, p_end_lock):
    local = True
    last_contour_receive_time = 0
    startTime_ms = 0
    contourRead = False
    x_diff = 0
    y_diff = 0
    prevX_diff = 0 
    prevY_diff = 0
    start_time = 0
    start_datetime = datetime.now()
    laserCond = False
    calibrationNow = False
    while (run_flag.value):
        returnBoolean, frame = videoCap.read()
        frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(frame_hsv, lowerC, upperC)
        # 4. Check the sum of blue pixels, only try to send over for processing if greater than threshold
        sum_of_blue = np.sum(mask)
        exceed_threshold = sum_of_blue > blue_threshold
        # 5. Check if time since last send to queue exceeds 30ms
        current_time = datetime.now()
        delta_time = current_time-start_datetime
        delta_time_ms = delta_time.total_seconds()*1000
        # Check if at Calibration Mode
        if (calibrationNow):
            pi_hw.hardware_PWM(motorPinR, 50, 80000) #50 Hz Freq.
            pi_hw.hardware_PWM(motorPinT, 50, 75000) #50 Hz Freq.
        else: 
            # Only put frame in queue if it has past 30ms and exceeds blue threshold and there are fewer than 4 frames in queue
            if ((delta_time_ms > 30) and exceed_threshold and (send_frame_queue.qsize() < 4)):
                start_datetime = current_time # Update last send to queue time
                send_frame_queue.put(mask) # Put mask in queue
            #Check if receive_contour_queue is not empty
            if ((not receive_contour_queue.empty())):
                last_contour_receive_time = time.time()
                contours = receive_contour_queue.get() #Extract contour
                # Extract the contour of the largest blue object
                if (len(contours)>0):
                    maxContour = len(contours)
                    maxIndex = 0
                for i in range (len(contours)):
                    if (len(contours[i]) > maxContour):
                        maxContour = len(contours[i])
                        maxIndex = i
                    M = cv2.moments(contours[maxIndex])
                # Compute center position of the largest blue object
                if (M["m00"] != 0):
                    cX = int(M["m10"] / M["m00"])
                    cY = int(M["m01"] / M["m00"])
                    # PID Control Algo to calculate strength for servo control
                    x_diff = abs(cX-center_x)
                    y_diff = abs(cY-center_y)
                    kp_x = 3
                    kd_x = 0.005
                    kp_y = 3
                    kd_y = 0.005 
                    proportional_x = x_diff/(x_res/2.0)
                    proportional_y = y_diff/(y_res/2.0)
                    derivative_x = (prevX_diff - x_diff)/(time.time() - start_time)
                    derivative_y = (prevY_diff - y_diff)/(time.time() - start_time)
                    strength_x = proportional_x*kp_x - derivative_x*kd_x
                    strength_y = proportional_y*kp_y - derivative_y*kd_y

                # Check if within range, move servos if not
                if (x_diff <= x_tol): #Within range, do nothing
                    a = 1
                    #print("horizontal-axis in range")
                elif (cX > center_x):
                    #print("Move Right by ", x_diff, "px")
                    rotate5(1,strength_x)
                else:
                    #print("Move Left by ", x_diff, "px")
                    rotate5(-1,strength_x)
                #print("--------")
                prevX_diff = x_diff
                prevY_diff = y_diff
        #Display last receiving contours for 0.5 sec
        if ((time.time()-last_contour_receive_time) < 0.5):
            cv2.circle(frame, (cX, cY), 7, (255, 255, 255), -1) #Draw center of object
            cv2.drawContours(frame,contours,-1,(255,0,0),3) #Draw contour of object
        
        cv2.circle(frame, (center_x, center_y), 2, (0, 0, 255), -1) #Draw center of camera
        cv2.imshow('frame',frame) #Display Frame
        
        k = cv2.waitKey(5) & 0xFF
        if k == ord('q'): # Press q to exit program safely
            run_flag.value = 0
            print("set run_flag --- 0")
        
    print("Quiting Main Processor 0")

# Function for the Worker Process 1
def process_frame_1(run_flag, send_frame_queue, receive_contour_queue, p_start_turn, p_end_turn, p_start_lock, p_end_lock):
    while (run_flag.value):
        startTime = datetime.now()
        startTime_ms = startTime.second *1000 + startTime.microsecond/1000
        # If frame queue not empty and it is Worker Process 1's turn
        if ((not send_frame_queue.empty()) and (p_start_turn.value == 1)):
            mask = send_frame_queue.get() # Grab a frame
            p_start_turn.value = 2 
            maskOpen=cv2.morphologyEx(mask,cv2.MORPH_OPEN,kernelOpen)
            maskClose=cv2.morphologyEx(maskOpen,cv2.MORPH_CLOSE,kernelClose)
            # 2. Extract contour
            _, contours,_=cv2.findContours(maskClose.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
            receive_contour_queue.put(contours) # Put contour back 
        else:
            #print("Processor 1 Didn't Receive Frame, sleep for 30ms")
            time.sleep(0.03)
        currentTime = datetime.now()
        currentTime_ms = currentTime.second *1000 + currentTime.microsecond/1000
        #print ("Processor 1 Processing Time: " + str(currentTime_ms-startTime_ms))
    print("Quiting Processor 1")

# Function for the Worker Process 2
def process_frame_2(run_flag, send_frame_queue, receive_contour_queue, p_start_turn, p_end_turn, p_start_lock, p_end_lock):
    
    while (run_flag.value):
        startTime = datetime.now()
        startTime_ms = startTime.second *1000 + startTime.microsecond/1000
        if ((not send_frame_queue.empty()) and (p_start_turn.value == 2)):
            mask = send_frame_queue.get()
            p_start_turn.value = 3
            maskOpen=cv2.morphologyEx(mask,cv2.MORPH_OPEN,kernelOpen)
            maskClose=cv2.morphologyEx(maskOpen,cv2.MORPH_CLOSE,kernelClose)
            # 2. Extract contour
            _,contours,_=cv2.findContours(maskClose.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
            receive_contour_queue.put(contours)
        else:
            #print("Processor 2 Didn't Receive Frame, sleep for 30ms")
            time.sleep(0.03)
        currentTime = datetime.now()
        currentTime_ms = currentTime.second *1000 + currentTime.microsecond/1000
        #print ("Processor 2 Processing Time: " + str(currentTime_ms-startTime_ms))
    print("Quiting Processor 2")

# Function for the Worker Process 3
def process_frame_3(run_flag, send_frame_queue, receive_contour_queue, p_start_turn, p_end_turn, p_start_lock, p_end_lock):
    
    while (run_flag.value):
        startTime = datetime.now()
        startTime_ms = startTime.second *1000 + startTime.microsecond/1000
        
        if ((not send_frame_queue.empty()) and (p_start_turn.value == 3)):
            mask = send_frame_queue.get()
            p_start_turn.value = 1
            maskOpen=cv2.morphologyEx(mask,cv2.MORPH_OPEN,kernelOpen)
            maskClose=cv2.morphologyEx(maskOpen,cv2.MORPH_CLOSE,kernelClose)
            # 2. Extract contour
            _,contours,_=cv2.findContours(maskClose.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
            receive_contour_queue.put(contours)
        else:
            #print("Processor 3 Didn't Receive Frame, sleep for 30ms")
            time.sleep(0.03)
        currentTime = datetime.now()
        currentTime_ms = currentTime.second *1000 + currentTime.microsecond/1000
        #print ("Processor 3 Processing Time: " + str(currentTime_ms-startTime_ms))
    print("Quiting Processor 3")

#Main: Step 1. Set Video Resolution Parameters
#Note: There will be less info to process if resolution decreases
x_res = 640 #320 
y_res = 480 #240 
center_x = x_res/2
center_y = y_res/2
#Main: Step 2. Create a VideoCapture object to capture video
videoCap = cv2.VideoCapture(0)
videoCap.set(3, x_res)
videoCap.set(4, y_res)
#Main: Step 3. Center Tolerance Parameters
tolerance = 10
x_tol = x_res * tolerance / 100
y_tol = y_res * tolerance / 100
blue_threshold = 500000
lowerC = np.array([65,60,60])
upperC = np.array([80,255,255])
# Setting Kernel Convolution Parameters
kernelOpen=np.ones((5,5))
kernelClose=np.ones((20,20))
x_diff = 0
y_diff = 0
#Global Run Flag
frame = 0 
contours = 0
cX = 0
cY = 0
contour_ready = False

if __name__ == '__main__':
    # run_flag is used to safely exit all processes
    run_flag = Value('i', 1) 
    # p_start_turn is used to keep worker processes process in order
    p_start_turn = Value('i', 1)  
    # p_end_turn is used to keep worker processes return frame in order
    # but code was commented out and hadn't tested its functionalities
    p_end_turn = Value('i', 1)
    send_frame_queue = Queue()
    receive_contour_queue = Queue()
    p_start_lock = Lock() #Safety lock, but didnt use
    p_end_lock = Lock() #Safety lock, but didnt use
    # Start four processes: 1 master process, 3 worker processes
    p0 = Process(target=grab_frame_display, args=(run_flag, send_frame_queue, receive_contour_queue, p_start_turn, p_end_turn,
        p_start_lock, p_end_lock))
    p1 = Process(target=process_frame_1, args=(run_flag, send_frame_queue, receive_contour_queue, p_start_turn, p_end_turn,
        p_start_lock, p_end_lock))
    p2 = Process(target=process_frame_2, args=(run_flag, send_frame_queue, receive_contour_queue, p_start_turn, p_end_turn,
        p_start_lock, p_end_lock))
    p3 = Process(target=process_frame_3, args=(run_flag, send_frame_queue, receive_contour_queue, p_start_turn, p_end_turn,
        p_start_lock, p_end_lock))
    p0.start()
    p1.start()
    p2.start()
    p3.start()
    # Wait for four processes to safely exit
    p0.join()
    p1.join()
    p2.join()
    p3.join()

    pi_hw.stop()                    #Turn off hardware PWM
    GPIO.cleanup()                  #Reset GPIO pins before exit
    cv2.destroyAllWindows()         #Turn off cv2 window