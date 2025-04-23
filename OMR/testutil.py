import cv2
import numpy as np

## TO STACK ALL THE IMAGES IN ONE WINDOW
def stackImages(imgArray,scale,lables=[]):
    rows = len(imgArray)
    cols = len(imgArray[0])
    rowsAvailable = isinstance(imgArray[0], list)
    width = imgArray[0][0].shape[1]
    height = imgArray[0][0].shape[0]
    if rowsAvailable:
        for x in range ( 0, rows):
            for y in range(0, cols):
                imgArray[x][y] = cv2.resize(imgArray[x][y], (0, 0), None, scale, scale)
                if len(imgArray[x][y].shape) == 2: imgArray[x][y]= cv2.cvtColor( imgArray[x][y], cv2.COLOR_GRAY2BGR)
        imageBlank = np.zeros((height, width, 3), np.uint8)
        hor = [imageBlank]*rows
        hor_con = [imageBlank]*rows
        for x in range(0, rows):
            hor[x] = np.hstack(imgArray[x])
            hor_con[x] = np.concatenate(imgArray[x])
        ver = np.vstack(hor)
        ver_con = np.concatenate(hor)
    else:
        for x in range(0, rows):
            imgArray[x] = cv2.resize(imgArray[x], (0, 0), None, scale, scale)
            if len(imgArray[x].shape) == 2: imgArray[x] = cv2.cvtColor(imgArray[x], cv2.COLOR_GRAY2BGR)
        hor= np.hstack(imgArray)
        hor_con= np.concatenate(imgArray)
        ver = hor
    if len(lables) != 0:
        eachImgWidth= int(ver.shape[1] / cols)
        eachImgHeight = int(ver.shape[0] / rows)
        #print(eachImgHeight)
        for d in range(0, rows):
            for c in range (0,cols):
                cv2.rectangle(ver,(c*eachImgWidth,eachImgHeight*d),(c*eachImgWidth+len(lables[d][c])*13+27,30+eachImgHeight*d),(255,255,255),cv2.FILLED)
                cv2.putText(ver,lables[d][c],(eachImgWidth*c+10,eachImgHeight*d+20),cv2.FONT_HERSHEY_COMPLEX,0.7,(255,0,255),2)
    return ver

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

    batas_pemotongan = int(width / 4.5)  
    pilihan_jawaban = img_resized[:, batas_pemotongan:]

    pilihan_jawaban_width = pilihan_jawaban.shape[1]
    pilihan_jawaban_width = (pilihan_jawaban_width // 5) * 5
    pilihan_jawaban = cv2.resize(pilihan_jawaban, (pilihan_jawaban_width, height))

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