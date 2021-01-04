import cv2
import numpy as np
import base64
import pickle
import os
import json

recognizer = cv2.face.LBPHFaceRecognizer_create(1, 5, 8, 8)
detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

def convert_image(image):
    old_image = image.replace("{","[").replace("}","]")
    json_image = json.loads(old_image)
    return np.array(json_image, dtype=np.uint8)

def verify(image, images):
    images = list(map(convert_image, images))
    labels = np.array([1] * len(images))
    cv_image = convert_to_cv_image(image)
    gray_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
    face_image = get_face(gray_image)
    resized_image = resized(face_image)
    
    #recognizer.read("trainer.yml")
    cv2.imwrite("old.png", images[0])
    cv2.imwrite("new.png", resized_image)
    recognizer.train(images, labels)
    id, confidence = recognizer.predict(resized_image)
    
    print(confidence)
    print(id)

    return confidence > 30 and confidence < 70

def register(image):
    cv_image = convert_to_cv_image(image)
    gray_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
    face_image = get_face(gray_image)
    resized_image = resized(face_image)
    return str(resized_image.tolist())

def save(image, id):
    cv_image = convert_to_cv_image(image)
    gray_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
    face_image = get_face(gray_image)
    recognizer.train([face_image], np.array(id))
    recognizer.save('trainer.yml')

def convert_to_cv_image(image):
    jpg_original = base64.b64decode(image.replace("data:image/png;base64,", ""))
    jpg_as_np = np.frombuffer(jpg_original, dtype=np.uint8)
    img = cv2.imdecode(jpg_as_np, flags=cv2.COLOR_BGR2GRAY)
    return img

def get_face(image):
    faces = detector.detectMultiScale(image, 1.1, 4)
    if len(faces):
        x,y,w,h = faces[0]
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        return image[y:y + h, x:x + w]
    else:    
        raise NameError('Face not detected')

def resized(image):
    return cv2.resize(image, (30, 30), interpolation = cv2.INTER_AREA)