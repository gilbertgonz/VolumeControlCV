import cv2
import time
import numpy as np
import HandTrackingModule as htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Variables
wCam, hCam = 640, 480
pTime = 0
cTime = 0
vol = 0
volBar = 400
volPer = 0

#Initializations
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
detector = htm.handDetector(detectionCon = 0.7)
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]

while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)

    if len(lmList) != 0:        
        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        cx, cy = (x1+x2)//2, (y1+y2)//2,
        
        cv2.circle(img, (x1, y1), 10, (0, 255, 0), cv2.FILLED)
        cv2.circle(img, (x2, y2), 10, (0, 255, 0), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 3)
        cv2.circle(img, (cx, cy), 10, (0, 255, 0), cv2.FILLED)

        length = math.hypot(x2-x1, y2-y1)

        if length < 30:
            cv2.circle(img, (cx, cy), 10, (255, 0, 0), cv2.FILLED)
        if length > 220:
            cv2.circle(img, (cx, cy), 10, (0, 0, 255), cv2.FILLED)

        vol = np.interp(length, [30,220], [minVol, maxVol])
        volBar = np.interp(length, [30, 220], [400, 150])
        volPer = np.interp(length, [30, 220], [0, 100])

        # print(int(length), vol)
        volume.SetMasterVolumeLevel(vol, None)

        cv2.rectangle(img, (50, 150), (85, 400), (0, 255, 0), 3)
        cv2.rectangle(img, (50, int(volBar)), (85, 400), (0, 255, 0), cv2.FILLED)
        cv2.putText(img, f'{int(volPer)} %', (40,450), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 3)


    # FPS Display
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (10,40), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 0), 3)

    # Displaying Image
    cv2.imshow("Image", img)

    # Press 'q' to close
    if cv2.waitKey(1) == ord('q'):
        break