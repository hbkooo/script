import xml.etree.ElementTree as ET
import xml.dom.minidom as DOC
import pickle
import os
from os import listdir, getcwd
from os.path import join
import cv2
import shutil

####################################################################################
################################# 用户配置修改 #####################################
####################################################################################

classes = ["person", "cigarette", "mobilephone"]            # 类别标签名字，顺序要注意
img_root_path = os.path.join('..', 'JPEGImages')            # 原始图片的路径
txt_root_path = os.path.join('..', 'labels')         # 原始图片的对应的yolo txt标签路径
xml_save_path = os.path.join('..', 'Annotations')    # 生成的voc xml标签存储路径

####################################################################################
####################################################################################
####################################################################################

#将bounding box信息写入xml文件中, bouding box格式为[[x_min, y_min, x_max, y_max, name]]
def generate_xml(img_name,coords,img_size,out_root_path):
    '''
    输入：
        img_name：图片名称，如a.jpg
        coords:坐标list，格式为[[x_min, y_min, x_max, y_max, name]]，name为概况的标注
        img_size：图像的大小,格式为[h,w,c]
        out_root_path: xml文件输出的根路径
    '''
    doc = DOC.Document()  # 创建DOM文档对象

    annotation = doc.createElement('annotation')
    doc.appendChild(annotation)

    title = doc.createElement('folder')
    title_text = doc.createTextNode('Tianchi')
    title.appendChild(title_text)
    annotation.appendChild(title)

    title = doc.createElement('filename')
    title_text = doc.createTextNode(img_name)
    title.appendChild(title_text)
    annotation.appendChild(title)

    source = doc.createElement('source')
    annotation.appendChild(source)

    title = doc.createElement('database')
    title_text = doc.createTextNode('The smoke Database')
    title.appendChild(title_text)
    source.appendChild(title)

    title = doc.createElement('annotation')
    title_text = doc.createTextNode('smoke')
    title.appendChild(title_text)
    source.appendChild(title)

    size = doc.createElement('size')
    annotation.appendChild(size)

    title = doc.createElement('width')
    title_text = doc.createTextNode(str(img_size[1]))
    title.appendChild(title_text)
    size.appendChild(title)

    title = doc.createElement('height')
    title_text = doc.createTextNode(str(img_size[0]))
    title.appendChild(title_text)
    size.appendChild(title)

    title = doc.createElement('depth')
    title_text = doc.createTextNode(str(img_size[2]))
    title.appendChild(title_text)
    size.appendChild(title)

    for coord in coords:

        object = doc.createElement('object')
        annotation.appendChild(object)

        title = doc.createElement('name')
        title_text = doc.createTextNode(coord[4])
        title.appendChild(title_text)
        object.appendChild(title)

        pose = doc.createElement('pose')
        pose.appendChild(doc.createTextNode('Unspecified'))
        object.appendChild(pose)
        truncated = doc.createElement('truncated')
        truncated.appendChild(doc.createTextNode('1'))
        object.appendChild(truncated)
        difficult = doc.createElement('difficult')
        difficult.appendChild(doc.createTextNode('0'))
        object.appendChild(difficult)

        bndbox = doc.createElement('bndbox')
        object.appendChild(bndbox)
        title = doc.createElement('xmin')
        title_text = doc.createTextNode(str(int(float(coord[0]))))
        title.appendChild(title_text)
        bndbox.appendChild(title)
        title = doc.createElement('ymin')
        title_text = doc.createTextNode(str(int(float(coord[1]))))
        title.appendChild(title_text)
        bndbox.appendChild(title)
        title = doc.createElement('xmax')
        title_text = doc.createTextNode(str(int(float(coord[2]))))
        title.appendChild(title_text)
        bndbox.appendChild(title)
        title = doc.createElement('ymax')
        title_text = doc.createTextNode(str(int(float(coord[3]))))
        title.appendChild(title_text)
        bndbox.appendChild(title)

    # 将DOM对象doc写入文件
    f = open(os.path.join(out_root_path, img_name[:-4]+'.xml'),'w')
    f.write(doc.toprettyxml(indent = ''))
    f.close()

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

# yolo 的txt格式转化为VOC格式
# size：[w, h], box: [x, y, w, h]
def convert_yolotxt_to_vocxml(size, box):
    '''
    输入：
        size：图片宽和高，格式[w, h]
        box: 坐标list，格式为[x, y, w, h]
    '''
    x,y,w,h = box
    W,H = size[0], size[1]
    x = x*W
    w = w*W
    y = y*H
    h = h*H
    xmin = int(x+1-w/2)
    ymin = int(y+1-h/2)
    xmax = int(x+1+w/2)
    ymax = int(y+1+h/2)
    if xmin < 0:
        xmin = 0
    if ymin < 0:
        ymin = 0
    if xmax >= W:
        xmax = W-1
    if ymax >= H:
        ymax = H-1
    return [xmin, ymin, xmax, ymax]

def convert_txt_label(txt_file_name):
    print('convert file : {}'.format(txt_file_name))
    
    in_file = open(os.path.join(txt_root_path, txt_file_name))
    lines = in_file.readlines()
    in_file.close()
    
    if len(lines) == 0:
        return
    
    img = cv2.imread(os.path.join(img_root_path, txt_file_name.split('.')[0]+'.jpg'))
    
    
    if img is None:
        print('error : ===> {} image is not exists ...'.format(txt_file_name.split('.')[0]+'.jpg'))
        return
        
    H,W,C = img.shape
    boxes = []
	
    for obj in lines:
        obj = obj.strip().split(' ')
        label = classes[int(obj[0])]
        x,y,w,h = float(obj[1]), float(obj[2]), float(obj[3]), float(obj[4])
        box = convert_yolotxt_to_vocxml((W,H), (x,y,w,h))
        #draw_1=cv2.rectangle(img, (box[0],box[1]), (box[2],box[3]), (0,255,0), 2)
        box.append(label)
        boxes.append(box)
    generate_xml(txt_file_name.split('.')[0]+'.jpg',boxes,img.shape,xml_save_path)
    #cv2.imwrite('t.jpg', draw_1)

if not os.path.exists(xml_save_path):
	os.makedirs(xml_save_path)
	
for file in os.listdir(txt_root_path):
	convert_txt_label(file)


print('done ...')
	
#os.system("cat 2007_train.txt 2007_val.txt 2012_train.txt 2012_val.txt > train.txt")
#os.system("cat 2007_train.txt 2007_val.txt 2007_test.txt 2012_train.txt 2012_val.txt > train.all.txt")

