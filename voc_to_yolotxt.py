# encoding: utf-8
import xml.etree.ElementTree as ET
import pickle
import os
from os import listdir, getcwd
from os.path import join
import cv2
import shutil

####################################################################################
################################# 用户配置修改 #####################################
####################################################################################

classes = ["person", "cigarette", "mobilephone"]    # 类别标签名字，顺序要注意
img_root_path = 'JPEGImages'                        # 原始图片的路径
xml_root_path = 'Annotations'                       # 原始图片的对应的xml标签路径
txt_save_path = 'labels'                            # 生成的yolo txt标签存储路径

####################################################################################
####################################################################################
####################################################################################

# voc 格式转化为yolo的txt格式
# size：[w, h], box: [xmin, ymin, xmax, ymax]
def convert_vocxml_to_yolotxt(size, box):
    '''
    输入：
        size：图片宽和高，格式[w, h]
        box: 坐标list，格式为[xmin, ymin, xmax, ymax]
    '''
    dw = 1./(size[0])
    dh = 1./(size[1])
    x = (box[0] + box[1])/2.0 - 1
    y = (box[2] + box[3])/2.0 - 1
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x*dw
    w = w*dw
    y = y*dh
    h = h*dh
    return (x,y,w,h)

def convert_annotation(xml_file_name):
    print('convert file : {}'.format(xml_file_name))
    in_file = open(os.path.join(xml_root_path, xml_file_name), encoding='UTF-8')
    out_file = open(os.path.join(txt_save_path, xml_file_name.split('.')[0] + '.txt'), 'w')
    tree=ET.parse(in_file)
    root = tree.getroot()
    size = root.find('size')
    w = int(size.find('width').text)
    h = int(size.find('height').text)
	
    if w == 0:
        print('xml file {} is wrong'.format(xml_file_name))
        '''
        img_path = os.path.join(img_root_path, xml_file_name.split('.')[0]+'.jpg')
        if os.path.exists(img_path):
            shutil.move(img_path, img_path.split('.')[0] + '.png')
        img_path = img_path.split('.')[0] + '.png'
        img = cv2.imread(img_path)
        print(img.shape)
        w = img.shape[1]
        h = img.shape[0]
        '''
        continue

    for obj in root.iter('object'):
        difficult = obj.find('difficult').text
        cls = obj.find('name').text
        if cls not in classes or int(difficult)==1:
            continue
        cls_id = classes.index(cls)
        xmlbox = obj.find('bndbox')
        b = (float(xmlbox.find('xmin').text), float(xmlbox.find('ymin').text), float(xmlbox.find('xmax').text), float(xmlbox.find('ymax').text))
        bb = convert_vocxml_to_yolotxt((w,h), b)
        # print(bb)
        out_file.write(str(cls_id) + " " + " ".join([str(a) for a in bb]) + '\n')

wd = getcwd()

if not os.path.exists(txt_save_path):
	os.makedirs(txt_save_path)
	
for file in os.listdir(xml_root_path):
	convert_annotation(file)
	
#os.system("cat 2007_train.txt 2007_val.txt 2012_train.txt 2012_val.txt > train.txt")
#os.system("cat 2007_train.txt 2007_val.txt 2007_test.txt 2012_train.txt 2012_val.txt > train.all.txt")

