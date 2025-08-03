import cv2
import numpy as np

def rectContour(contours):

    rectCon = []
    for i in contours:
        area = cv2.contourArea(i)
        #print("Area",area)
        if area>40000:
            peri = cv2.arcLength(i,True)
            approx = cv2.approxPolyDP(i,0.02*peri,True)
            #print("Corner Point",len(approx))
            if len(approx) == 4:
                rectCon.append(i)
    rectCon = sorted(rectCon,key=cv2.contourArea,reverse=True)

    return rectCon

def getCornerPoints(cont):
    peri = cv2.arcLength(cont, True)
    approx = cv2.approxPolyDP(cont, 0.02 * peri, True)
    return approx

def reorder(myPoints):
    myPoints = myPoints.reshape((4, 2))
    myPointsNew = np.zeros((4, 1, 2), dtype=np.int32)

    add = myPoints.sum(1)
    #print("add", add)
    #print("myPoints", myPoints)
    myPointsNew[0] = myPoints[np.argmin(add)] # [0, 0]
    myPointsNew[3] = myPoints[np.argmax(add)] # [w, h]
    diff = np.diff(myPoints, axis=1)
    myPointsNew[1] = myPoints[np.argmin(diff)] # [w, 0]
    myPointsNew[2] = myPoints[np.argmax(diff)] # [0, h]
    #print(diff)

    return myPointsNew

def splitBoxes(img_resized):
    height, width = img_resized.shape[:2]

    # Misalkan nomor jawaban berada di antara 1/3 dan 1/4 bagian kiri gambar
    batas_pemotongan = int(width / 4.5)  # Sesuaikan batas pemotongan
    pilihan_jawaban = img_resized[:, batas_pemotongan:]

    # Pastikan lebar pilihan_jawaban dapat dibagi secara merata menjadi 5 kolom
    pilihan_jawaban_width = pilihan_jawaban.shape[1]
    pilihan_jawaban_width = (pilihan_jawaban_width // 5) * 5
    pilihan_jawaban = cv2.resize(pilihan_jawaban, (pilihan_jawaban_width, height))

    # Bagi gambar menjadi 30 baris
    rows = np.vsplit(pilihan_jawaban, 30)
    boxes = []
    for r in rows:
        # Bagi setiap baris menjadi 5 kolom (karena ada 5 pilihan: A, B, C, D, E)
        cols = np.hsplit(r, 5)
        for box in cols:
            boxes.append(box)

    cv2.imshow("Split Test", rows[0])
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return boxes

def showAnswer(img, myIndex, answer, grading):
    secW = int(img.shape[1] / 5)
    secH = int(img.shape[0] / 30)

    for x in range(0, 30):
        myAns = myIndex[x]
        correctAns = answer[x]
        cX = (myAns * secW) + secW // 2 + 32
        cY = (x * secH) + secH // 2 + 5

        if grading[x] == 1:
            color = (0, 255, 0)
        else:
            color = (0,0,255)
            correctAns = answer[x]

        cv2.circle(img, (cX, cY), 12, color, cv2.FILLED)

        if grading[x] == 0:
            correctCX = (correctAns * secW) + secW // 2 + 32
            cv2.circle(img, (correctCX, cY), 10, (0, 255, 0), cv2.FILLED)

    return img