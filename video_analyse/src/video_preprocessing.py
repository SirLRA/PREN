import cv2
import numpy as np

class HSVRanges:
    red_color = [
        {
            "color_name": "red",
            "lower_bounds": np.array([0, 100, 20]),
            "upper_bounds": np.array([10, 255, 255])
        },
        {
            "color_name": "red",
            "lower_bounds": np.array([160, 100, 20]),
            "upper_bounds": np.array([180, 255, 255]) 
        }
    ]

    yellow_color = [
        {
            "color_name": "yellow",
            "lower_bounds": np.array([20, 100, 100]),
            "upper_bounds": np.array([40, 255, 255]) 
        }
    ]

    blue_color = [
        {
            "color_name": "blue",
            "lower_bounds": np.array([90, 50, 70]),
            "upper_bounds": np.array([128, 255, 255]) 
        }
    ]

    light_grey_color = [
        {
            "color_name": "light grey",
            "lower_bounds": np.array([0, 0, 180]),
            "upper_bounds": np.array([180, 40, 255])
        }
    ]



class Video:
    videoCapture = None

    def __init__(self, path):
        self.videoCapture = cv2.VideoCapture(path)

    def get_next_frame(self):
        return self.videoCapture.read()

    def create_color_mask(hsv, colors):
        mask = []

        for color in colors:
            if len(mask) == 0:
                mask = cv2.inRange(hsv, color["lower_bounds"], color["upper_bounds"])
            else:
                mask = cv2.bitwise_or(mask, cv2.inRange(hsv, color["lower_bounds"], color["upper_bounds"]))

        return mask
    
    def grey_mask(frame):
        return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    def blur_mask(frame, size=(5,5)):
        return cv2.GaussianBlur(frame, size, 0)

    def threshold_mask(frame):
        return cv2.adaptiveThreshold(frame, 255, 1, 1, 11, 2)
    
    def contrast_improvement_mask(frame):
        return cv2.equalizeHist(frame)

    def dilate_mask(frame, shape=(5,5)):
        kernel = np.ones(shape, np.uint8)
        eroded = cv2.erode(frame, kernel, iterations=1)
        return cv2.dilate(eroded, kernel, iterations=1)
    
    def eroded_mask(frame, shape=(5,5)):
        kernel = np.ones(shape, np.uint8)
        dilated = cv2.dilate(frame, kernel, iterations=1)
        return cv2.erode(dilated, kernel, iterations=1)
    
    def clahe_correction(frame):
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        return clahe.apply(frame)
    
    def gamma_correction(frame, gamma=1.5):
        frame = np.power(frame / 255.0, gamma) * 255.0
        return np.uint8(frame)
        
    def contrast_stretching(frame, min_intensity=0, max_intensity=255):
        return cv2.normalize(frame, None, min_intensity, max_intensity, cv2.NORM_MINMAX)
