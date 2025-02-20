import cv2
from utils import get_limits
from PIL import Image

yellow = (0, 255, 255)
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    hsv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_limit, upper_limit = get_limits(color=yellow)
    mask = cv2.inRange(hsv_image, lower_limit, upper_limit)
    mask_ = Image.fromarray(mask)
    bbox = mask_.getbbox()
    if bbox is not None:
        x1, y1, x2, y2 = bbox
        frame = cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)


    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
