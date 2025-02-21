import cv2
import mediapipe as mp
import argparse
import os

def proses_image(img, face_detection):
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = face_detection.process(img_rgb)

    if results.detections is not None:
        for detection in results.detections:
            bbox = detection.location_data.relative_bounding_box
            ih, iw, _ = img.shape
            x, y, w, h = int(bbox.xmin * iw), int(bbox.ymin * ih), int(bbox.width * iw), int(bbox.height * ih)
            
            # Blur face
            face = img[y:y+h, x:x+w]
            face = cv2.GaussianBlur(face, (99, 99), 30)
            img[y:y+h, x:x+w] = face

    return img

def process_image_file(image_path, face_detection):
    img = cv2.imread(image_path)
    img = proses_image(img, face_detection)
    output_dir = 'output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    cv2.imwrite(f'{output_dir}/face_anonymized.jpg', img)
    cv2.imshow('Face Detection', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def process_webcam(face_detection):
    cap = cv2.VideoCapture(0)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame = proses_image(frame, face_detection)
        cv2.imshow('Face Detection', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Face Anonymizer')
    parser.add_argument('--image', type=str, help='Path to the image file')
    parser.add_argument('--webcam', action='store_true', help='Use webcam for real-time face anonymization')
    args = parser.parse_args()

    mp_face_detection = mp.solutions.face_detection

    with mp_face_detection.FaceDetection(
            model_selection=0, 
            min_detection_confidence=0.5
        ) as face_detection:
        
        if args.webcam:
            process_webcam(face_detection)
        elif args.image:
            process_image_file(args.image, face_detection)
        else:
            print("Please provide an image file path with --image or use --webcam for real-time face anonymization.")