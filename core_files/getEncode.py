import os
import face_recognition
import pickle

face_dir = 'faces/'

known_face_encodings = []
known_face_names = []

def auto_encode():
    if not os.path.exists(face_dir):
        print(f"The directory {face_dir} does not exist.")
        return

    for image_name in os.listdir(face_dir):
        if image_name.lower().endswith(('.jpg', '.jpeg', '.png')):
            image_path = os.path.join(face_dir, image_name)

            try:
                image = face_recognition.load_image_file(image_path)
                face_encodings = face_recognition.face_encodings(image)

                if face_encodings:
                    known_face_encodings.append(face_encodings[0])
                    known_face_names.append(os.path.splitext(image_name)[0])
                else:
                    print(f"No faces found in {image_name}. Skipping.")
            except Exception as e:
                print(f"Error processing {image_name}: {e}")

    with open('face_encodings.pkl', 'wb') as f:
        pickle.dump((known_face_encodings, known_face_names), f)
