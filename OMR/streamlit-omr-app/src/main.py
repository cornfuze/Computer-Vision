import streamlit as st
import cv2
import numpy as np
import testutil as utils
from PIL import Image

def main():
    st.title("Optical Mark Recognition (OMR) Application")
    
    st.write("Upload an image for OMR processing:")
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    
    # Input for user's answers
    st.write("Enter the correct answers (comma-separated, e.g., A,B,C,A,...):")
    user_answers = st.text_input("Correct Answers", value="C,B,D,B,B,B,B,E,D,C,B,B,C,D,B,B,B,C,B,C,D,C,A,C,B,C,E,A,C,B")

    if uploaded_file is not None:
        # Read the image using OpenCV
        image = Image.open(uploaded_file)
        img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Resize the image
        img = cv2.resize(img, (700, 700))
        imgFinal = img.copy()

        # Convert to grayscale, blur, and threshold
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 1)
        thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

        # Find contours
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        rectCon = utils.rectContour(contours)

        # Add a select box to choose between rectCon[0] and rectCon[1]
        contour_option = st.selectbox("Select processing version:", options=["Version 1", "Version 2"])
        selected_index = 0 if contour_option == "Version 1" else 1

        # Use the selected index to determine the contour
        bigContour = utils.getCornerPoints(rectCon[selected_index])

        if bigContour.size != 0:
            bigContour = utils.reorder(bigContour)

            # Calculate aspect ratio and adjust target dimensions
            pt1 = np.float32(bigContour)
            width = max(pt1[1][0][0] - pt1[0][0][0], pt1[3][0][0] - pt1[2][0][0])  # Horizontal distance
            height = max(pt1[2][0][1] - pt1[0][0][1], pt1[3][0][1] - pt1[1][0][1])  # Vertical distance
            aspect_ratio = width / height

            target_height = 700  # Fixed target height
            target_width = int(target_height * aspect_ratio)  # Adjust target width based on aspect ratio
            pt2 = np.float32([[0, 0], [target_width, 0], [0, target_height], [target_width, target_height]])

            # Perspective transform
            matrix = cv2.getPerspectiveTransform(pt1, pt2)
            imgWarpColored = cv2.warpPerspective(img, matrix, (target_width, target_height))

            # Thresholding on warped image
            imgWarpGray = cv2.cvtColor(imgWarpColored, cv2.COLOR_BGR2GRAY)
            imgThresh = cv2.adaptiveThreshold(imgWarpGray, 255, 1, 1, 11, 2)

            # Resize for splitting into boxes
            height, width = imgThresh.shape[:2]
            new_height = (height // 30) * 30
            new_width = (width // 5) * 5
            img_resized = cv2.resize(imgThresh, (new_width, new_height))

            # Split into boxes
            boxes = utils.splitBoxes(img_resized)

            # Calculate pixel values
            myPixelValue = np.zeros((30, 5))
            countC = 0
            countR = 0

            for image in boxes:
                totalPixels = cv2.countNonZero(image)
                myPixelValue[countR][countC] = totalPixels
                countC += 1
                if countC == 5: 
                    countR += 1
                    countC = 0

            # Determine answers
            myIndex = []
            for x in range(0, 30):
                arr = myPixelValue[x]
                myIndexVal = np.where(arr == np.amax(arr))
                myIndex.append(myIndexVal[0][0])

            # Parse user answers
            try:
                # Convert A-E to 0-4
                answer = [ord(char.upper()) - ord('A') for char in user_answers.split(",")]
                if len(answer) != 30:
                    st.error("Please enter exactly 30 answers.")
                    return
                if not all(0 <= val <= 4 for val in answer):
                    st.error("Answers must be between A and E.")
                    return
            except ValueError:
                st.error("Invalid input. Please enter letters A-E separated by commas.")
                return

            # Grading
            grading = []
            for x in range(0, 30):
                if answer[x] == myIndex[x]:
                    grading.append(1)
                else:
                    grading.append(0)

            score = (sum(grading) / 30) * 100

            # Display results
            imgResult = imgWarpColored.copy()
            imgResult = utils.showAnswer(imgResult, myIndex, answer, grading)
            imgRawDrawing = np.zeros_like(imgWarpColored)
            imgRawDrawing = utils.showAnswer(imgRawDrawing, myIndex, answer, grading)
            invMatrix = cv2.getPerspectiveTransform(pt2, pt1)
            invInverseWarp = cv2.warpPerspective(imgRawDrawing, invMatrix, (700, 700))

            imgFinal = cv2.addWeighted(imgFinal, 1, invInverseWarp, 1, 0)
            cv2.putText(imgFinal, f'Score: {score:.2f}%', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)

            # Display final image and score
            st.image(imgFinal, channels="BGR", caption=f"Final Result (Score: {score:.2f}%)", use_container_width=True)

if __name__ == "__main__":
    main()