import cv2
import mediapipe as mp
from pynput.mouse import Controller
import time
import os

cap = cv2.VideoCapture(0)  # Object to capture the video stream.
mouse = Controller()

# Three required objects to manipulate the input from the capture.
mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils


def isAGesture(p1, p2, p3):
    disIndexThumbTip = ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5
    disIndexDipThumbTip = ((p1[0] - p3[0]) ** 2 + (p1[1] - p3[1]) ** 2) ** 0.5
    if disIndexThumbTip < 35 and disIndexDipThumbTip < 60:
        return False
    return True

def calc_distance(finger1, finger2):
    # Calculate the Euclidean distance between thumb tip and index tip (finding the distance between two points in a 2-dimensional axis).
    return ((finger1[0] - finger2[0]) ** 2 + (finger1[1] - finger2[1]) ** 2) ** 0.5

def action(f1, f2, ID_finger, f3):
    if calc_distance(f1, f2) < 35 and isAGesture(f1, f2, f3): #Threshold adjustable.
        if(ID_finger == "IR"):
            os.system("open /Applications/Google\ Chrome.app")
        if(ID_finger == "IL"):
            os.system("open /Applications/Discord.app")
        if(ID_finger == "PR"):
            os.system("pkill -f Google \"Chrome\"")
        if(ID_finger == "PL"):
            os.system("killall Discord")
        time.sleep(0.02)

def main():
    while True:
        success, image = cap.read()  # Reads the image.
        imageRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Converts it to the desired format (RGB to BGR).
        results = hands.process(imageRGB)  # Processing the results.
        # Checking whether a hand is detected.
        if results.multi_hand_landmarks:
            for handLms, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):  # Working with each hand and its handedness.
                hand_list = []
                for id, lm in enumerate(handLms.landmark):  # Getting the landmarks for the blueprint of the hand.
                    h, w, c = image.shape  # Getting the height, width, and channel of the image.
                    cx, cy = int(lm.x * w), int(lm.y * h)  # Getting the central positions of the hand.
                    hand_list.append([id, cx, cy])

                    if id == 4:  # Id == 4 is for the tip of the thumb.
                        thumb_tip = (cx, cy)
                        cv2.putText(image, f'({cx}, {cy})', (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (40, 252, 3), 2)
                    elif id == 8:  # Id == 8 is for the tip of the index finger.
                        index_tip = (cx, cy)
                    elif id == 20:  # Id == 8 is for the tip of the pinky finger.
                        pinky_tip = (cx, cy)
                    elif id == 7:  # Id == 7 is for under the tip of the index finger.
                        gesture_dependency = (cx, cy)
                        cv2.putText(image, f'({cx}, {cy})', (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (40, 252, 3), 2)

                if handedness.classification[0].label == 'Left': #Its opposite that's why it's on left while it's recognising the right hand
                    action(thumb_tip, index_tip, "IR", gesture_dependency)
                    action(thumb_tip, pinky_tip, "PR", gesture_dependency)
                else:
                    action(thumb_tip, index_tip, "IL", gesture_dependency)
                    action(thumb_tip, pinky_tip, "PL" ,gesture_dependency)

                mpDraw.draw_landmarks(image, handLms, mpHands.HAND_CONNECTIONS)
                cv2.imshow("Output", image)

        # Check for Enter on the keyboard and then break the loop so the window stops.
        if cv2.waitKey(1) == 13:
            break

    # Release the camera and close the OpenCV window.
    cap.release()
    cv2.destroyAllWindows()



if __name__ == '__main__':
    main()