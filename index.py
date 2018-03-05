import numpy as np
from PIL import ImageGrab
import cv2
import time


last_time = time.time()

while(True):
    printscreen_pil = ImageGrab.grab(bbox=(0,40, 800, 640))
    cv2.imshow('window', cv2.cvtColor(np.array(printscreen_pil), cv2.COLOR_BGR2RGB))
    if cv2.waitKey(25) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        break
    print('Loop took %s seconds' % format(time.time()-last_time))
    last_time = time.time()