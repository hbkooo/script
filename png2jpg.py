"""
    先来说一下jpg图片和png图片的区别
    jpg格式:是有损图片压缩类型,可用最少的磁盘空间得到较好的图像质量
    png格式:不是压缩性,能保存透明等图

"""
from PIL import Image
import cv2 as cv
import os

def PNG_JPG(PngPath, savePath):
    img = cv.imread(PngPath, 0)
    w, h = img.shape[::-1]
    infile = PngPath
    img = Image.open(infile)
    #img = img.resize((int(w / 2), int(h / 2)), Image.ANTIALIAS)
    try:
        if len(img.split()) == 4:
            # prevent IOError: cannot write mode RGBA as BMP
            r, g, b, a = img.split()
            img = Image.merge("RGB", (r, g, b))
            img.convert('RGB').save(savePath, quality=95, subsampling=0)  
            # os.remove(PngPath)
        else:
            # quality : 95, 大于95之后会增加图片大小，但是图片质量相差不大
            # subsampling=0， 这样会使转化后的图片大小变大，满足一些需求
            img.convert('RGB').save(savePath, quality=95, subsampling=0)
            # os.remove(PngPath)
        return savePath
    except Exception as e:
        print("PNG转换JPG 错误", e)


if __name__ == '__main__':
    PNG_JPG(r"zs2.png", "zs2.jpg")
    
    for png in os.listdir('.'):
        if not png.endswith('.png'):
            continue
        PNG_JPG(png, png.split('.')[0] + ".jpg")
