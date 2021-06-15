from cv2 import cv2       #importing open cv-->converts photo into a format
import os                 
from keras.models import load_model  
import numpy as np        
from pygame import mixer
import time
import smtpmail
from threading import Thread

mixer.init() #for playing sounds
sound = mixer.Sound('alarm.wav')
#Haar cascades is a machine learning based approach
face = cv2.CascadeClassifier(  
    'haar cascade files\haarcascade_frontalface_alt.xml')
leye = cv2.CascadeClassifier(
    'haar cascade files\haarcascade_lefteye_2splits.xml')
reye = cv2.CascadeClassifier(
    'haar cascade files\haarcascade_righteye_2splits.xml')


lbl = ['Close', 'Open']

model = load_model('models/cnncat2.h5')
path = os.getcwd()   #get current working directory
cap = cv2.VideoCapture(0)   #0 is for webcam , else can give a file location
vid_cod = cv2.VideoWriter_fourcc(*'mp4v')  
output = None
font = cv2.FONT_HERSHEY_COMPLEX_SMALL
count = 0
score = 0
thicc = 2
rpred = [99]
lpred = [99]
record_flag = False
record_length = 10  # in seconds
video_count = 0
mail_frequency_delay = 300
start_time = time.time() - mail_frequency_delay

def play_sound(sound):
    try:
        sound.play()
    except:  # isplaying = False
        pass
if __name__ == '__main__':
    while True:
        ret, frame = cap.read()      #(ret)flag-->wether video captured crctly or not , frame

        height, width = frame.shape[:2]
        if record_flag:                        #record flag to send mails
            print(video_count)
            output.write(frame)
            if time.time() - start_time > record_length:
                print("MAKE FALSE")
                record_flag = False
                output.release()
                print("before send")
                sendEmail = Thread(target=smtpmail.send, args=(video_count-1,))
                sendEmail.start()
                print("after send")

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)   #detection works only on a greyscale images

        faces = face.detectMultiScale(                         #it detects faces
            gray, minNeighbors=5, scaleFactor=1.1, minSize=(25, 25)) #(greay scale image,scale factor,minimumneighbours)
        left_eye = leye.detectMultiScale(gray)
        right_eye = reye.detectMultiScale(gray)

        cv2.rectangle(frame, (0, height-50), (200, height), #draw rect for complete screen
                    (0, 0, 0), thickness=cv2.FILLED)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (100, 100, 100), 1)  #draw rectangle for face

        for (x, y, w, h) in right_eye:              #right eye
            r_eye = frame[y:y+h, x:x+w]
            count = count+1
            r_eye = cv2.cvtColor(r_eye, cv2.COLOR_BGR2GRAY)
            r_eye = cv2.resize(r_eye, (24, 24))
            r_eye = r_eye/255
            r_eye = r_eye.reshape(24, 24, -1)
            r_eye = np.expand_dims(r_eye, axis=0)
            rpred = model.predict_classes(r_eye)
            if(rpred[0] == 1):
                lbl = 'Open'
            if(rpred[0] == 0):
                lbl = 'Closed'
            break

        for (x, y, w, h) in left_eye:          #lefteye
            l_eye = frame[y:y+h, x:x+w]
            count = count+1
            l_eye = cv2.cvtColor(l_eye, cv2.COLOR_BGR2GRAY)
            l_eye = cv2.resize(l_eye, (24, 24))
            l_eye = l_eye/255
            l_eye = l_eye.reshape(24, 24, -1)
            l_eye = np.expand_dims(l_eye, axis=0)
            lpred = model.predict_classes(l_eye)
            if(lpred[0] == 1):
                lbl = 'Open'
            if(lpred[0] == 0):
                lbl = 'Closed'
            break

        if(rpred[0] == 0 and lpred[0] == 0):
            score = score+1
            cv2.putText(frame, "Closed", (10, height-20), font,
                        1, (255, 255, 255), 1, cv2.LINE_AA)
        # if(rpred[0]==1 or lpred[0]==1):
        else:
            score = score-1
            cv2.putText(frame, "Open", (10, height-20), font,
                        1, (255, 255, 255), 1, cv2.LINE_AA)

        if(score < 0):
            score = 0
        cv2.putText(frame, 'Score:'+str(score), (100, height-20),
                    font, 1, (255, 255, 255), 1, cv2.LINE_AA)
        if(score > 15):
            # person is feeling sleepy so we beep the alarm
            cv2.imwrite(os.path.join(path, 'image.jpg'), frame)
            play_sound(sound)
            if not record_flag and time.time() - start_time > mail_frequency_delay:
                print("FALSE")
                record_flag = True
                output = cv2.VideoWriter("cam_video"+str(video_count)+".mp4", vid_cod, 10.0, (640,480))
                video_count+=1
                start_time = time.time()

            if(thicc < 16):
                thicc = thicc+2
            else:
                thicc = thicc-2
                if(thicc < 2):
                    thicc = 2
            cv2.rectangle(frame, (0, 0), (width, height), (0, 0, 255), thicc)
        cv2.imshow('frame', frame)                            #image show
        if cv2.waitKey(1) & 0xFF == ord('q'):    #quit
            break
    cap.release()
    cv2.destroyAllWindows()
    if record_flag:
        os.remove("cam_video"+str(video_count-1)+".mp4")