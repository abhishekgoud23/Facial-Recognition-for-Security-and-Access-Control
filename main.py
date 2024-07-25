import cv2  # OpenCV library for image processing
import dlib  # dlib library for face detection and landmark prediction
import numpy as np  # NumPy for numerical operations on arrays
from deepface import DeepFace  # DeepFace library for face recognition
from matplotlib import pyplot as plt  # Matplotlib for displaying images
import os  # OS module for file operations

# Load Dlib models
detector = dlib.get_frontal_face_detector()  # Initialize face detector
predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')  # Load shape predictor for facial landmarks

def preprocess_image(image_path):
    # Check if the image file exists
    if not os.path.isfile(image_path):
        print(f"Error: File {image_path} does not exist.")
        return None
    
    image = cv2.imread(image_path)  # Read the image from the file

    if image is None:
        print(f"Error: Failed to load image from {image_path}")
        return None
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # Convert image to grayscale
    faces = detector(gray)  # Detect faces in the grayscale image
    for face in faces:
        landmarks = predictor(gray, face)  # Get facial landmarks for each detected face
        face_aligned = dlib.get_face_chip(image, landmarks, size=256)  # Align the face
        return face_aligned  # Return the aligned face
    return None  # Return None if no face is detected

def display_image(image):
    plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))  # Convert BGR to RGB for display
    plt.axis('off')  # Hide axis
    plt.show()  # Display the image

image_path = 'person1.jpg'  # Path to the image file
face = preprocess_image(image_path)  # Preprocess the image to get the aligned face
if face is not None:
    display_image(face)  # Display the aligned face if successfully processed

def create_database(image_paths, names):
    db = {}  # Dictionary to store face data and file paths
    for img_path, name in zip(image_paths, names):
        # Check if the image file exists
        if not os.path.isfile(img_path):
            print(f"Error: File {img_path} does not exist.")
            continue
        
        result = DeepFace.extract_faces(img_path=img_path, detector_backend='opencv')  # Extract faces using DeepFace

        # Ensure result is a list and contains at least one face
        if isinstance(result, list) and len(result) > 0:
            face_data = result[0]
            face_image = face_data['face']  # Get the face image

            # Ensure face_image is a valid NumPy array
            if isinstance(face_image, np.ndarray) and face_image.ndim == 3:
                # Normalize result array if necessary
                face_image = np.clip(face_image * 255, 0, 255).astype(np.uint8)

                temp_db_face_path = f'temp_db_face_{name}.jpg'  # Temporary path to save face image
                if not cv2.imwrite(temp_db_face_path, face_image):
                    print(f"Error: Failed to save image to {temp_db_face_path}")
                db[name] = temp_db_face_path  # Add face image path to database
            else:
                print(f"Error: The face image is not a valid NumPy array or has an unexpected shape. Type: {type(face_image)}, Shape: {getattr(face_image, 'shape', 'N/A')}")
        else:
            print(f"Error: The result is not in the expected format. Result: {result}")

    return db  # Return the database of face images

image_paths = ['person1.jpg']  # List of image paths
names = ['Person 1']  # Corresponding names for the images
database = create_database(image_paths, names)  # Create the database of face images

def recognize_face(face, database):
    temp_face_path = 'temp_face.jpg'  # Temporary path to save the new face image
    if not cv2.imwrite(temp_face_path, face):
        print(f"Error: Failed to save image to {temp_face_path}")
        return "Unknown"
    
    new_face_path = temp_face_path

    # Compare the new face with each face in the database
    for name, db_face_path in database.items():
        if not os.path.isfile(db_face_path):
            print(f"Error: Database file {db_face_path} does not exist.")
            continue

        try:
            result = DeepFace.verify(img1_path=new_face_path, img2_path=db_face_path, detector_backend='opencv', model_name='VGG-Face', 
                                     enforce_detection=False)
            if result['verified']:
                return name  # Return the name if faces match
        except Exception as e:
            print(f"Exception while processing face for {name}: {e}")
    
    return "Unknown"  # Return "Unknown" if no match is found

def access_control(name):
    authorized_names = ['Person 1']  # List of authorized names
    if name in authorized_names:
        print(f"Access granted to {name}")  # Grant access if the name is authorized
    else:
        print("Access denied")  # Deny access if the name is not authorized

new_face_path = 'person2.jpg'  # Path to the new face image
new_face = preprocess_image(new_face_path)  # Preprocess the new face image

if new_face is not None:
    recognized_name = recognize_face(new_face, database)  # Recognize the new face
    access_control(recognized_name)  # Check access control based on recognized name
