#coding=utf-8
#Author: ZeLun Zhang

import re
import sys
import requests
import urllib
import sys
import os
import json

def get_picurls_in_one_page(html_text, pic_url_key = '"objURL":"(.*?)",'):
    '''
    pageurl: 输入一个页面的url，获得这个页面所有图片的url
    pic_url_key: 图片url的识别头
    '''
    pic_urls = re.findall(pic_url_key, html_text, re.S)
    return pic_urls

def get_next_pageurl(html_text, head = 'http://image.baidu.com', \
        next_page_key = r'<a href="(.*)" class="n">下一页</a>'):
    '''
    获得下一个页面的url
    '''
    next_page_url = re.findall(re.compile(next_page_key), html_text, flags = 0)
    if len(next_page_url) == 0:
        return -1
    else:
        return head + next_page_url[0] 

def down_pic(pic_url, save_path):
    '''
    输入一个图像的url下载到指定位置
    '''
    pic = requests.get(pic_url, timeout = 10)
    with open(save_path, 'wb+') as tem:
        tem.write(pic.content)

def main():
    init_url = 'http://image.baidu.com/search/flip?tn=baiduimage&ipn=r&ct=201326592&cl=2&lm=-1&st=-1&fm=result&fr=&sf=1&fmq=1497491098685_R&pv=&ic=0&nc=1&z=&se=1&showtab=0&fb=0&width=&height=&face=0&istype=2&ie=utf-8&ctd=1497491098685%5E00_1519X735&word='
    for keyword in keywords:
        print('[info]: downloading pics of {}'.format(keyword))
        save_dir = os.path.join(root_dir, keyword)
        if not os.path.isdir(save_dir):
            os.mkdir(save_dir)
        page_url = init_url + keyword
        html = requests.get(page_url)
        html = html.text
        pic_urls = get_picurls_in_one_page(html)
        idx = 0
        while idx < num:
            print('[info]: downloading {}th'.format(idx + 1), end = '\n')
            pic_url = pic_urls.pop()
            save_path = os.path.join(save_dir, 'holl_{}.jpg'.format(idx))
            try:
                down_pic(pic_url, save_path)
                idx += 1
            except:
                pass
            if len(pic_urls) == 0:
                page_url = get_next_pageurl(html)
                if page_url == -1:
                    print()
                    print('[info]: already reach last page, only save {} pics'\
                            .format(idx + 1))
                    break
                else:
                    html = requests.get(page_url)
                    html = html.text
                    pic_urls = get_picurls_in_one_page(html)
                    if len(pic_urls) == 0:
                        print()
                        print('[info]: already reach last page, only save {} pics'\
                                .format(idx + 1))
                        break



if __name__ == '__main__':
    print('process id: {}'.format(os.getpid()))
    '''
    with open('label_id_name.json', 'r') as tem:
        label_d = json.load(tem)
    label_l = list(label_d.items())[4:5]
    print(label_l)
    keywords = [i[1].split('/')[1] for i in label_l]
    print(keywords)
    '''
    keywords = ['钢板击穿','弹痕']
    #num = int(input('输入下载图片数量：'))
    num = 200
    assert num > 0
    root_dir = 'holl/'
    if not os.path.isdir(root_dir):
        raise FileNotFoundError('Root dir {} does not exist.'.format(root_dir))
    main()
