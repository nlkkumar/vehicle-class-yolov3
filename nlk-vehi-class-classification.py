import streamlit as st
import cv2
import time
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from streamlit_lottie import st_lottie


# Initialize the parameters
confThreshold = 0.2  #Confidence threshold
nmsThreshold = 0.4   #Non-maximum suppression threshold
inpWidth = 416       #Width of network's input image
inpHeight = 416      #Height of network's input image 


def obj_detection(my_img):
    st.set_option('deprecation.showPyplotGlobalUse', False)

    column1, column2 = st.beta_columns(2)

    column1.subheader("Input image")
    st.text("")
   # plt.figure(figsize=(16, 16))
   # plt.imshow(my_img)
   # original = Image.open(image)
    #col1.header("Original")
    if my_img.mode != 'RGB':
        my_img = my_img.convert('RGB')
    column1.image(my_img, use_column_width=True)
    # column1.pyplot(use_column_width=True)


    # YOLO model : # load the YOLO network
   # net = cv2.dnn.readNet("yolov3_training_last.weights","yolov3_testing.cfg")
   # net = cv2.dnn.readNetFromDarknet("yolov4-custom.cfg","yolov4-custom_best.weights" )
    net = cv2.dnn.readNet('yolov4-custom_best.weights', 'yolov4-custom.cfg')

   # labels = []
   # with open("classes.txt", "r") as f:
   #     labels = [line.strip() for line in f.readlines()]

   # loading all the class labels (objects)

    classes = []
    with open("classes.txt", "r") as f:
        classes = f.read().splitlines()

    # names_of_layer = net.getLayerNames()
    # output_layers = [names_of_layer[i[0] - 1] for i in net.getUnconnectedOutLayers()]

    # generating colors for each object for later plotting
    font = cv2.FONT_HERSHEY_PLAIN
    colors = np.random.uniform(0, 255, size=(100, 3))

    # colors = np.random.uniform(0, 255, size=(len(classes), 3))
    print("Colors:", colors)

    # Image loading
    newImage = np.array(my_img.convert('RGB'))
    img = cv2.cvtColor(newImage, 1)
    height, width, channels = img.shape

    # Objects detection (Converting into blobs)
    # (image, scalefactor, size, mean(mean subtraction from each layer), swapRB(Blue to red), crop)
    # blob = cv2.dnn.blobFromImage(img, 0.00392, (inpWidth, inpHeight), (0, 0, 0), True,
                                 # crop=False)
    blob = cv2.dnn.blobFromImage(img, 1/255, (416, 416), (0,0,0), swapRB=True, crop=False)

    # sets the blob as the input of the network
    net.setInput(blob)
    # outputs = net.forward(output_layers)
    output_layers_names = net.getUnconnectedOutLayersNames()
    # layerOutputs = net.forward(output_layers_names)

    # get all the layer names
    # ln = net.getLayerNames()
    # ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]
    # names_of_layer = net.getLayerNames()
    # output_layers = [names_of_layer[i[0] - 1] for i in net.getUnconnectedOutLayers()]
    # feed forward (inference) and get the network output
    # measure how much it took in seconds
    # start = time.perf_counter()
    # outputs = net.forward(output_layers)
    outputs = net.forward(output_layers_names)
    # time_took = time.perf_counter() - start
    # print(f"Time took: {time_took:.2f}s")

    # The function getPerfProfile returns the overall time for inference(t) and the timings for each of the layers(in layersTimes)
    t, _ = net.getPerfProfile()
    infLabel = 'Inference time: %.2f ms' % (t * 1000.0 / cv2.getTickFrequency())
  #  cv2.putText(frame, label, (0, 15), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255))


    classID = []
    confidences = []
    boxes = []

    # SHOWING INFORMATION CONTAINED IN 'outputs' VARIABLE ON THE SCREEN
    # loop over each of the layer outputs
    for op in outputs:
        for detection in op:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.2:
                # OBJECT DETECTED
                # Get the coordinates of object: center,width,height
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)  # width is the original width of image
                h = int(detection[3] * height)  # height is the original height of the image

                # use the center (x, y)-coordinates to derive the top and
                # and left corner of the bounding box
                # RECTANGLE COORDINATES
                x = int(center_x - w / 2)  # Top-Left x
                y = int(center_y - h / 2)  # Top-left y

                # To organize the objects in array so that we can extract them later
                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                classID.append(class_id)

    # score_threshold = st.sidebar.slider("Confidence_threshold", 0.00, 1.00, 0.5, 0.01)
    # nms_threshold = st.sidebar.slider("NMS_threshold", 0.00, 1.00, 0.4, 0.01)
    score_threshold = 0.2
    st.sidebar.info(f"Confidence_threshold:{ score_threshold }")
    nms_threshold = 0.4
    st.sidebar.info(f"NMS_threshold :{nms_threshold} ")
    st.sidebar.success(infLabel)


    indexes = cv2.dnn.NMSBoxes(boxes, confidences, score_threshold, nms_threshold)
    print("DNN Index:", indexes)

    font = cv2.FONT_HERSHEY_SIMPLEX
    items = []
    for i in range(len(boxes)):
        if i in indexes.flatten():
            x, y, w, h = boxes[i]
            # To get the name of object
            label = str.upper((classes[classID[i]]))
            # label = str(classes[class_ids[i]])
            confidence = str(round(confidences[i], 2))
            print("value of i:", i)
            color = colors[i]
            cv2.rectangle(img, (x, y), (x + w, y + h), color, 3)
            cv2.putText(img, label + " " + confidence, (x, y + 10), font, 0.25, (0, 0, 255), 1)
            items.append(label)

    st.text("")
    st.spinner('Model working....')
    column2.subheader("Output image")
    st.text("")
  #  plt.figure(figsize=(15, 15))
   # plt.imshow(img)
    # column2.pyplot(use_column_width=True)
    column2.image(img, use_column_width=True)


    if len(indexes) > 1:
        st.success("Found {} Objects - {}".format(len(indexes), [item for item in set(items)]))
        st.balloons()
    elif len(indexes) == 1:
        st.success("Found {} Object - {}".format(len(indexes), [item for item in set(items)]))
        st.balloons()
    else:
        st.warning("Found {} Object - {}".format(len(indexes), [item for item in set(items)]))


# with open("custom.css") as f:
  #  st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title('Welcome to Vehicle Classification App')

st.markdown("Welcome to this  Computer Vision application that classifies Vehicles on Indian Highways. The Vehicles are classified into Seven different classes namely: Bus, Truck, Car, Jeep,Van,miniTruck and Lorry.It will find Person too if present.")

def main():
    st.write(
        "You can view Vehicle Classification using YOLO model here. Select one of the following options to proceed:")

    choice = st.radio("", ("Default", "Choose an image of your choice"))
    # st.write()

    if choice == "Choose an image of your choice":
        # st.set_option('deprecation.showfileUploaderEncoding', False)
        image_file = st.file_uploader("Upload", type=['jpg', 'png', 'jpeg'])

        if image_file is not None:
            my_img = Image.open(image_file)
            obj_detection(my_img)

    elif choice == "Default":
        my_img = Image.open("v999.jpg")
        obj_detection(my_img)


if __name__ == '__main__':
    main()

    
