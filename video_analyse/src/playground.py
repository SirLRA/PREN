import cv2
import numpy as np
import os
import json
import helper as hp


#region CONFIGURATION CONSTANTS

VIDEO_PATH = '../ressources/video_example/video_example.mp4'

IN_DEBUG_MODE = True
FRAME_STEP_BY_STEP = True

ROTATION_SIDES = 4

CHECKED_FRAMES_PER_SIDE = 10

OUTPUT_FILE_NAME = "output.json"
OUTPUT_FILE_DIR = "../tmp"


#endregion

def create_color_mask(hsv, colors):

    mask = []

    for color in colors:
        if len(mask) == 0:
            mask = cv2.inRange(hsv, color["lower_bounds"], color["upper_bounds"])
        else:
            mask = cv2.bitwise_or(mask, cv2.inRange(hsv, color["lower_bounds"], color["upper_bounds"]))

    return mask

#region CORDINATE CALCULATION

def calculate_object_cordinates_with_blob_detection(gray_image, image):
    params = cv2.SimpleBlobDetector.Params()
    params.filterByColor = True
    params.blobColor = 255

    # params.filterByArea = True
    # params.minArea = 100

    kernel = np.ones((5, 5), np.uint8)
    eroded = cv2.erode(gray_image, kernel, iterations=1)
    dilate = cv2.dilate(eroded, kernel, iterations=1)

    # Use blob detection on the mask to identify objects
    detector = cv2.SimpleBlobDetector_create(params)
    keypoints = detector.detect(dilate)

    print(keypoints)


    # Loop through the detected keypoints (blobs)
    for keypoint in keypoints:
        x, y, size = int(keypoint.pt[0]), int(keypoint.pt[1]), int(keypoint.size)
        cv2.circle(image, (x, y), size, (0,0,255), 2)

        # Calculate the top-left and bottom-right coordinates of the bounding box
        top_left = (x - size // 2, y - size // 2)
        bottom_right = (x + size // 2, y + size // 2)

        # Draw a rectangle (border) around the blob
        cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)  # You can change the color and thickness as needed


#endregion

#region IMAGE_PROECESSING

def erode_image_processing(non_erode_mask, result):
    eroded_mask = hp.Video.eroded_mask(non_erode_mask)
    eroded_mask2 = hp.Video.eroded_mask(non_erode_mask, (10,10))        
    eroded_mask3 = hp.Video.eroded_mask(non_erode_mask, (20,20))
    eroded_mask4 = hp.Video.eroded_mask(non_erode_mask, (50,50))


    test = cv2.bitwise_and(result, result, mask=non_erode_mask)
    test2 = cv2.bitwise_and(result, result, mask=eroded_mask)
    test3 = cv2.bitwise_and(result, result, mask=eroded_mask2)
    test4 = cv2.bitwise_and(result, result, mask=eroded_mask3)
    test5 = cv2.bitwise_and(result, result, mask=eroded_mask4)

    hp.Out.image_show('no erode', test, IN_DEBUG_MODE)
    hp.Out.image_show('erode (5,5)', test2, IN_DEBUG_MODE)
    hp.Out.image_show('erode (10,10)', test3, IN_DEBUG_MODE)
    hp.Out.image_show('erode (20,20)', test4, IN_DEBUG_MODE)
    hp.Out.image_show('erode (50,50)', test5, IN_DEBUG_MODE)

def gamma_correction(gray, result):
    gamma = hp.Video.gamma_correction(gray, 1.5)

    test = cv2.bitwise_and(result, result, mask=gamma)

    hp.Out.image_show('no gamma', result, IN_DEBUG_MODE)
    hp.Out.image_show('gamma', test, IN_DEBUG_MODE)


def contrast_stretching(gray, result):
    stretched = hp.Video.contrast_stretching(gray)

    test = cv2.bitwise_and(result, result, mask=stretched)

    hp.Out.image_show('no stretching', result, IN_DEBUG_MODE)
    hp.Out.image_show('stretching', test, IN_DEBUG_MODE)


def contour_enhancement(gray, result):
    # clahe = hp.Video.clahe_correction(gray)
    stretched = hp.Video.contrast_stretching(gray)
    # gamma = hp.Video.gamma_correction(stretched)
    blur = hp.Video.blur_mask(stretched)
    threshed = hp.Video.threshold_mask(blur)
    # eroded_mask = hp.Video.eroded_mask(threshed)


    min_contour_area = 1000  # Adjust this value as needed

    contours, _ = cv2.findContours(threshed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    max_area = 0
    c = 0
    for contour in contours:
        contour_area = cv2.contourArea(contour)
        if min_contour_area <= contour_area:
            if contour_area > max_area:
                    max_area = contour_area
                    best_cnt = contour
                    result = cv2.drawContours(result, contours, c, (0, 255, 0), 20)
        c+=1

    mask = np.zeros((gray.shape),np.uint8)
    cv2.drawContours(mask,[best_cnt],0,255,-1)
    cv2.drawContours(mask,[best_cnt],0,0,2)

    hp.Out.image_show("Zwischenresultat", result, IN_DEBUG_MODE)

    print(mask == 0)


    # segment regions of interests (no biggest contours)
    out = np.zeros_like(gray)
    out[mask == 255] = gray[mask == 255]

    hp.Out.image_show("Out image", out, IN_DEBUG_MODE)

    # Image preprocessing
    blur = hp.Video.blur_mask(out)
    processed = hp.Video.threshold_mask(blur)
    eroded = hp.Video.eroded_mask(processed, (10,10))

    hp.Out.image_show("Enhanced image", eroded, IN_DEBUG_MODE)

    contours, _ = cv2.findContours(eroded, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    c = 0
    for i in contours:
            cv2.drawContours(result, contours, c, (0, 0, 0), 20)
            c+=1



    # Draw the contours on the result image
    # cv2.drawContours(result, contours, -1, (0, 0, 0), -1)  # -1 means fill the contours

    # Display the result (you can also save it if needed)
    hp.Out.image_show("Result", result, IN_DEBUG_MODE)

    # test = cv2.bitwise_or(result, result, mask=threshed)
    
    # image_show('Contour enhanced Mask', threshed)
    # image_show('Contour enhanced bitwise and', test)
    # image_show('Original', result)


#endregion

def main():
    video = hp.Video(os.path.join(os.path.dirname(os.path.abspath(__file__)), VIDEO_PATH))
    exit_analyse = False

    while True: 
        ret, frame = hp.Video.get_next_frame(video)

        if not ret:
            break

        # blue = np.uint8([[[0,255,0]]])
        # blue_hsv = cv2.cvtColor(blue, cv2.COLOR_BGR2HSV)  
        # print(blue_hsv)
        # lowerLimit = blue_hsv[0][0][0] - 10, 100, 100
        # upperLimit = blue_hsv[0][0][0] + 10, 255, 255
        # print(lowerLimit)
        # print(upperLimit)

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        color_mask = hp.Video.create_color_mask(hsv, hp.HSVRanges.red_color + hp.HSVRanges.blue_color + hp.HSVRanges.yellow_color)
        result = cv2.bitwise_and(frame, frame, mask=color_mask)

        gray_mask = hp.Video.grey_mask(result)

        contour_enhancement(gray_mask, result)

        # contrast_stretching(gray_mask, result)
        # gamma_correction(gray_mask, result)        



        # clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        # enhanced = clahe.apply(gray_mask)
        # enhanced = hp.Video.contrast_improvement_mask(gray_mask)

        # blur_mask = hp.Video.blur_mask(enhanced)
        # no_gamma = hp.Video.threshold_mask(blur_mask)


        # erode_image_processing(thresh_mask, result)




        # calculate_object_cordinates_with_blob_detection(test, result)

        if IN_DEBUG_MODE:

            if FRAME_STEP_BY_STEP:
                while True:
                    # Press enter to run next frame
                    if cv2.waitKey(1) == 13:
                        break

                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        exit_analyse = True
                        break

            if exit_analyse or (cv2.waitKey(1) & 0xFF == ord('q')):
                break



if __name__ == "__main__":
    main()
