#contour processing of images
def test_model(image,version):
    
    #test either digit model or letter model + load corresponding h5 file
    if version == "digits":
        model = load_model(r"C:\Users\Peter McGurk\Desktop\Cornell\ECE MEng\Embedded OS\Final Project\digit_model.h5")
        labels = [0,1,2,3,4,5,6,7,8,9]
    if version == "letters":
        model = load_model(r"C:\Users\Peter McGurk\Desktop\Cornell\ECE MEng\Embedded OS\Final Project\letter_model.h5")
        labels = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s',
                     't','u','v','w','x','y','z']
        
    # load the input image from disk, convert it to grayscale, and blur
    # it to reduce noise
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    # perform edge detection, find contours in the edge map, and sort the
    # resulting contours from left-to-right
    edged = cv2.Canny(blurred, 30, 150)

    cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    cnts = sort_contours(cnts, method="left-to-right")[0]
    # initialize the list of contour bounding boxes 
    chars = []

    word = ""
    # loop over the contours
    for c in cnts:
        # compute the bounding box of the contour
        (x, y, w, h) = cv2.boundingRect(c)
        # filter out bounding boxes, ensuring they are neither too small
        # nor too large
        #***************************************************8
        if (w >= 10 and w <= 400) and (h >=50 and h <= 400):
            # extract the character and threshold it to make the character
            # appear as *white* (foreground) on a *black* background, then
            # grab the width and height of the thresholded image
            roi = gray[y:y + h, x:x + w]
            thresh = cv2.threshold(roi, 0, 255,
                cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
            (tH, tW) = thresh.shape

            # if the width is greater than the height, resize along the
            # width dimension
            if tW > tH:
                pad = int(tW * 0.15)
                padded1 = cv2.copyMakeBorder(thresh, top=0, bottom=0,
                left=pad, right=pad, borderType=cv2.BORDER_CONSTANT,
                value=(0, 0, 0))

                thresh = imutils.resize(padded1, width=28)
            # otherwise, resize along the height
            else:
                pad = int(tH * 0.15)
                padded1 = cv2.copyMakeBorder(thresh, top=pad, bottom=pad,
                left=0, right=0, borderType=cv2.BORDER_CONSTANT,
                value=(0, 0, 0))
                thresh = imutils.resize(padded1, height=28)

            # re-grab the image dimensions (now that its been resized)
            # and then determine how much we need to pad the width and
            # height such that our image will be 32x32
            (tH, tW) = thresh.shape
            dX = int(max(0, 28 - tW) / 2.0)
            dY = int(max(0, 28 - tH) / 2.0)
            # pad the image and force 32x32 dimensions
            padded = cv2.copyMakeBorder(thresh, top=dY, bottom=dY,
                left=dX, right=dX, borderType=cv2.BORDER_CONSTANT,
                value=(0, 0, 0))
            padded = cv2.resize(padded, (28, 28))
            plt.subplot(2, 1, 1)
            plt.imshow(padded,cmap=plt.get_cmap('gray'))
            plt.show()

            # prepare the padded image for classification via our
            # handwriting OCR model
            padded = padded.astype("float32") / 255.0
            padded = np.expand_dims(padded, axis=-1)
            # update our list of characters that will be OCR'd
            chars.append((padded, (x, y, w, h)))
            padded = padded.T
            padded = padded.reshape(1, 28, 28, 1)
            predict_value = model.predict(padded);
            label_index = np.argmax(predict_value)
            print("This character looks like a " + str(labels[label_index-1]))
            word += str(labels[label_index-1])
    print(word)

