import cv2
import numpy as np
import utils

answer = [2, 1, 3, 1, 1, 1, 1, 4, 3, 2, 1, 1, 2, 3, 1, 1, 1, 2, 1, 2, 3, 2, 0, 2, 1, 2, 4, 0, 2, 1]

path = 'assets/t1.jpeg'  
img = cv2.imread(path)
img = cv2.resize(img, (700, 700))
imgContour = img.copy()
imgBigContour = img.copy()
imgFinal = img.copy()
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
blur = cv2.GaussianBlur(gray, (5, 5), 1)
thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
cv2.drawContours(img, contours, -1, (0, 255, 0), 2)

cv2.imshow("tresh",thresh)
cv2.imshow("Hasil Deteksi Kontur", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
#FIND Rectangle
rectCon = utils.rectContour(contours)
bigContour = utils.getCornerPoints(rectCon[0])
#print(bigContour.shape)

if bigContour.size != 0:
    cv2.drawContours(imgBigContour, bigContour, -1, (255, 0, 0), 10)
    bigContour = utils.reorder(bigContour)

    pt1 = np.float32(bigContour)
    pt2 = np.float32([[0, 0], [700, 0], [0, 700], [700, 700]])
    matrix = cv2.getPerspectiveTransform(pt1, pt2)
    imgWarpColored = cv2.warpPerspective(img, matrix, (700, 700))

    # Hitung rasio aspek area asli
    width = max(pt1[1][0][0] - pt1[0][0][0], pt1[3][0][0] - pt1[2][0][0])  # Jarak horizontal
    height = max(pt1[2][0][1] - pt1[0][0][1], pt1[3][0][1] - pt1[1][0][1])  # Jarak vertikal
    aspect_ratio = width / height

    # Sesuaikan dimensi target
    target_height = 700  # Tetapkan tinggi target
    target_width = int(target_height * aspect_ratio)  # Sesuaikan lebar target berdasarkan rasio aspek
    pt2 = np.float32([[0, 0], [target_width, 0], [0, target_height], [target_width, target_height]])

    # Transformasi perspektif
    matrix = cv2.getPerspectiveTransform(pt1, pt2)
    imgWarpColored = cv2.warpPerspective(img, matrix, (target_width, target_height))

    # Visualisasi hasil
    cv2.imshow("Warped Image", imgWarpColored)
    
    #Thresholding
    imgWarpGray = cv2.cvtColor(imgWarpColored, cv2.COLOR_BGR2GRAY)
    imgThresh = cv2.adaptiveThreshold(imgWarpGray, 255, 1, 1, 11, 2)
    
    # Resize imgThresh to ensure it can be split into 30 rows and 5 columns
    height, width = imgThresh.shape[:2]
    new_height = (height // 30) * 30
    new_width = (width // 5) * 5  # Pastikan lebar baru adalah kelipatan 5
    img_resized = cv2.resize(imgThresh, (new_width, new_height))

    boxes = utils.splitBoxes(img_resized)
    #cv2.imshow("Test", boxes[9])
    #print(cv2.countNonZero(boxes[2]),cv2.countNonZero(boxes[3]),cv2.countNonZero(boxes[6]))
    
    #Pixel Value
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
    #print(myPixelValue)

    myIndex = []
    for x in range(0, 30):
        arr = myPixelValue[x]
        myIndexVal = np.where(arr == np.amax(arr))
        #print(myIndexVal[0][0])
        myIndex.append(myIndexVal[0][0])
    #print(myIndex)

    grading = []
    for x in range (0,30):
        if answer[x] == myIndex[x]:
            grading.append(1)
        else: grading.append(0)
    print(grading)
    score = (sum(grading)/30)*100
    print("Score", score)

    #Display
    imgResult = imgWarpColored.copy()
    imgResult = utils.showAnswer(imgResult, myIndex, answer, grading)
    imgRawDrawing = np.zeros_like(imgWarpColored)
    imgRawDrawing = utils.showAnswer(imgRawDrawing, myIndex, answer, grading)
    invMatrix = cv2.getPerspectiveTransform(pt2, pt1)
    invInverseWarp = cv2.warpPerspective(imgRawDrawing, invMatrix, (700, 700))

    imgFinal = cv2.addWeighted(imgFinal, 1, invInverseWarp, 1, 0)
    cv2.putText(imgFinal, f'Score: {score:.2f}%', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)


cv2.imshow("Warped Image", imgWarpColored)

cv2.imshow("Hasil", imgResult)
#cv2.imshow("Hasil Gambar", imgRawDrawing)
#cv2.imshow("Hasil Inverse Warp", invInverseWarp)
cv2.imshow("Hasil Akhir", imgFinal)
#cv2.imshow("Hasil Threshold", imgThresh)
#cv2.imshow("Hasil Deteksi Kontur Besar", imgBigContour)
#cv2.imshow("Hasil Warp", imgWarpColored)
cv2.waitKey(0)
cv2.destroyAllWindows()