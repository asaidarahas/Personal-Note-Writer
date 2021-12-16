import pytesseract


# load the input image and grab the image dimensions
# img = cv2.imread("sample3.png")
# # Adding custom options
# custom_config = r'--psm 6'
# print(pytesseract.image_to_string(img, config=custom_config))
#


def get_letters(image):
    custom_config = r'--psm 9'
    return pytesseract.image_to_string(image, config=custom_config)

# EasyOCR
# reader = Reader(['en'])
# img = cv2.imread("math3.png")
#
#
# def cleanup_text(text):
#     # strip out non-ASCII text so we can draw the text on the image
#     # using OpenCV
#     return "".join([c if ord(c) < 128 else "" for c in text]).strip()
#
#
# results = reader.readtext(img, allowlist = '0123456789')
#
# print(results)
# for (bbox, text, prob) in results:
#     # display the OCR'd text and associated probability
#     print("[INFO] {:.4f}: {}".format(prob, text))
#     # unpack the bounding box
#     (tl, tr, br, bl) = bbox
#     tl = (int(tl[0]), int(tl[1]))
#     tr = (int(tr[0]), int(tr[1]))
#     br = (int(br[0]), int(br[1]))
#     bl = (int(bl[0]), int(bl[1]))
#     # cleanup the text and draw the box surrounding the text along
#     # with the OCR'd text itself
#     text = cleanup_text(text)
#     cv2.rectangle(img, tl, br, (0, 255, 0), 2)
#     cv2.putText(img, text, (tl[0], tl[1] - 10),
#                 cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
#
# express = results[-1][1]
# print("Expression = ", express)
# # Math mode
# express = express.replace('X', '*')
# express = express.replace('x', '*')
# print("Answer = ", eval(express))
#
# # show the output image
# cv2.imshow("Image", img)
# cv2.waitKey(0)

# output = []
# for res in results:
#     if len(res) > 1:
#         alist = [int(i) for i in res.split(' ')]
#         output.extend(alist)
#     else:
#         output.append(int(res))
#
# print(output)
