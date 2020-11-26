import os
from voc_eval import voc_eval

detpath = '../results/{}.txt'  # person.txt
annopath = '/data/hbk/data/coco/yolo/Annotations/{}.xml'
imagesetfile = '/data/hbk/data/coco/yolo/val.txt'
cachedir = '.'


classnames = ['person', 'suitcase', 'handbag', 'backpack']

def process_image_list_name(image_file, save = 'val.txt'):
    lines = open(image_file).readlines()
    f = open(save,'w')
    for line in lines:
        line = os.path.basename(line).split('.')[0]
        f.write('{}\n'.format(line))
    f.close()

save = 'val_name.txt'
process_image_list_name(imagesetfile, save)

for classname in classnames:
    rec, prec, ap = voc_eval(detpath, annopath, save, classname, cachedir)
    print('{} ===> rec : {}, prec : {}, ap : {}'.format(classname, rec, prec, ap))

