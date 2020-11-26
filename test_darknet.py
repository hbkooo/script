#! /usr/bin/python
# encoding: utf-8
from ctypes import *
import math
import random
import cv2
import os
import argparse
import numpy
from PIL import Image, ImageDraw, ImageFont

parser = argparse.ArgumentParser(description='darknet demo')
parser.add_argument('--type',dest='type', help='the source file', default='damage')
parser.add_argument('--weights',dest='weights', help='the source file', default='"/home/hbk/darknet/backup/damage/damage_33000.weights"')

parser.add_argument('--test_batch', dest='test_batch', help='images name')
parser.add_argument('--batch', help='is batch', action='store_true')
parser.add_argument('--image',dest='image', help='the source file')

args = parser.parse_args()
classes = ['suitcase', 'handbag', 'backpack']
LABEL_COLOR = {'suitcase':(0,0,255),
               'handbag':(0,255,0),
               'backpack':(255,255,0)}
               

def sample(probs):
    s = sum(probs)
    probs = [a/s for a in probs]
    r = random.uniform(0, 1)
    for i in range(len(probs)):
        r = r - probs[i]
        if r <= 0:
            return i
    return len(probs)-1

def c_array(ctype, values):
    arr = (ctype*len(values))()
    arr[:] = values
    return arr

class BOX(Structure):
    _fields_ = [("x", c_float),
                ("y", c_float),
                ("w", c_float),
                ("h", c_float)]

class DETECTION(Structure):
    _fields_ = [("bbox", BOX),
                ("classes", c_int),
                ("prob", POINTER(c_float)),
                ("mask", POINTER(c_float)),
                ("objectness", c_float),
                ("sort_class", c_int)]


class IMAGE(Structure):
    _fields_ = [("w", c_int),
                ("h", c_int),
                ("c", c_int),
                ("data", POINTER(c_float))]

class METADATA(Structure):
    _fields_ = [("classes", c_int),
                ("names", POINTER(c_char_p))]

    

#lib = CDLL("/home/pjreddie/documents/darknet/libdarknet.so", RTLD_GLOBAL)
lib = CDLL("libdarknet.so", RTLD_GLOBAL)
lib.network_width.argtypes = [c_void_p]
lib.network_width.restype = c_int
lib.network_height.argtypes = [c_void_p]
lib.network_height.restype = c_int

predict = lib.network_predict
predict.argtypes = [c_void_p, POINTER(c_float)]
predict.restype = POINTER(c_float)

set_gpu = lib.cuda_set_device
set_gpu.argtypes = [c_int]

make_image = lib.make_image
make_image.argtypes = [c_int, c_int, c_int]
make_image.restype = IMAGE

get_network_boxes = lib.get_network_boxes
get_network_boxes.argtypes = [c_void_p, c_int, c_int, c_float, c_float, POINTER(c_int), c_int, POINTER(c_int)]
get_network_boxes.restype = POINTER(DETECTION)

make_network_boxes = lib.make_network_boxes
make_network_boxes.argtypes = [c_void_p]
make_network_boxes.restype = POINTER(DETECTION)

free_detections = lib.free_detections
free_detections.argtypes = [POINTER(DETECTION), c_int]

free_ptrs = lib.free_ptrs
free_ptrs.argtypes = [POINTER(c_void_p), c_int]

network_predict = lib.network_predict
network_predict.argtypes = [c_void_p, POINTER(c_float)]

reset_rnn = lib.reset_rnn
reset_rnn.argtypes = [c_void_p]

load_net = lib.load_network
load_net.argtypes = [c_char_p, c_char_p, c_int]
load_net.restype = c_void_p

do_nms_obj = lib.do_nms_obj
do_nms_obj.argtypes = [POINTER(DETECTION), c_int, c_int, c_float]

do_nms_sort = lib.do_nms_sort
do_nms_sort.argtypes = [POINTER(DETECTION), c_int, c_int, c_float]

free_image = lib.free_image
free_image.argtypes = [IMAGE]

letterbox_image = lib.letterbox_image
letterbox_image.argtypes = [IMAGE, c_int, c_int]
letterbox_image.restype = IMAGE

load_meta = lib.get_metadata
lib.get_metadata.argtypes = [c_char_p]
lib.get_metadata.restype = METADATA

load_image = lib.load_image_color
load_image.argtypes = [c_char_p, c_int, c_int]
load_image.restype = IMAGE

rgbgr_image = lib.rgbgr_image
rgbgr_image.argtypes = [IMAGE]

predict_image = lib.network_predict_image
predict_image.argtypes = [c_void_p, IMAGE]
predict_image.restype = POINTER(c_float)

def classify(net, meta, im):
    out = predict_image(net, im)
    res = []
    for i in range(meta.classes):
        res.append((meta.names[i], out[i]))
    res = sorted(res, key=lambda x: -x[1])
    return res

def detect(net, meta, image, thresh=.5, hier_thresh=.5, nms=.45):
    image = bytes(image, encoding='utf-8')
    im = load_image(image, 0, 0)
    num = c_int(0)
    pnum = pointer(num)
    predict_image(net, im)
    dets = get_network_boxes(net, im.w, im.h, thresh, hier_thresh, None, 0, pnum)
    num = pnum[0]
    if (nms): do_nms_obj(dets, num, meta.classes, nms);

    res = []
    for j in range(num):
        for i in range(meta.classes):
            if dets[j].prob[i] > 0:
                b = dets[j].bbox
                res.append((meta.names[i], dets[j].prob[i], (b.x, b.y, b.w, b.h)))
    res = sorted(res, key=lambda x: -x[1])
    free_image(im)
    free_detections(dets, num)
    return res
    
def cv2ImgAddText(img, text, left, top, textColor=(0, 255, 0), textSize=20):
    if (isinstance(img, numpy.ndarray)):  
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img)
    fontText = ImageFont.truetype(
        "cfg/kaiti_GB2312.ttf", textSize, encoding="utf-8")
    draw.text((left, top), text, textColor, font=fontText)
    return cv2.cvtColor(numpy.asarray(img), cv2.COLOR_RGB2BGR)

def detect_one_img(net, meta, image, thresh=.5):
    r = detect(net, meta, image, thresh)
    #print r
    image_ = cv2.imread(image)

    for result in r:
        label = result[0]
        score = result[1]
        x, y, w, h = result[2]
        #print(label)
        cv2.rectangle(image_, (int(x-w/2),int(y-h/2)), (int(x+w/2),int(y+h/2)), LABEL_COLOR[label], 2)
        img = cv2.putText(image_, label.decode('utf-8'), (int(x-w/2),int(y-h/2)), cv2.FONT_HERSHEY_COMPLEX, 1, LABEL_COLOR[label], 2)
        #img =cv.putText(img, text, org, fontFace,fontScale,color[, thickness[, lineType[, bottomLeftOrigin]]])
        #image_ = cv2ImgAddText(image_, label, int(x-w/2), int(y-h/2), LABEL_COLOR[label], 20)
    return image_

if __name__ == "__main__":
    #net = load_net("cfg/densenet201.cfg", "/home/pjreddie/trained/densenet201.weights", 0)
    #im = load_image("data/wolf.jpg", 0, 0)
    #meta = load_meta("cfg/imagenet1k.data")
    #r = classify(net, meta, im)
    #print r[:10]
    cfg = "cfg/baggage.cfg"
    weights = "baggage_13000.weights"
    data = "cfg/baggage.data"
    
    if args.weights is not None:
        weights = args.weights
        
    test = args.test_batch
    img = args.image
    
    test_result_dir = 'test/result/'
    
    net = load_net(cfg, weights, 0)
    meta = load_meta(data)
    
    
    print('test type : ', args.type)
    print('model cfg : ', cfg)
    print('model weights : ', weights)
    print('test_result path : ', test_result_dir)
    print('test image lists : ', test)
    

    if test is not None and os.path.exists(test):
        if not os.path.exists(test_result_dir):
            os.makedirs(test_result_dir)
        f = open(test)
        lines = f.readlines()
        f.close()
        for line in lines:
            line = line.strip()
            print('img_path : ', line)
            image = detect_one_img(net, meta, line, 0.4)
            cv2.imwrite(os.path.join(test_result_dir, line.split('/')[-1]), image)

    if img is not None:
        image = detect_one_img(net, meta, img, 0.4)
        cv2.imwrite('result.jpg', image)
        print('write result in result.jpg')

