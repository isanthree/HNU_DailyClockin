# coding=utf-8

import json
import base64
import requests
import os
import logging

from retry import retry


from urllib.request import urlopen
from urllib.request import Request
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.parse import quote_plus
from urllib.request import urlretrieve


# 防止https证书校验不正确
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

API_KEY = ''

SECRET_KEY = ''


OCR_URL = "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic"


"""  TOKEN start """
TOKEN_URL = 'https://aip.baidubce.com/oauth/2.0/token'

ID = ''

PASSWORD= ''

SERVERCHAN_SCKEY=''

"""
    获取token
"""
def fetch_token():
    params = {'grant_type': 'client_credentials',
              'client_id': API_KEY,
              'client_secret': SECRET_KEY}
    post_data = urlencode(params)
    post_data = post_data.encode('utf-8')
    req = Request(TOKEN_URL, post_data)
    try:
        f = urlopen(req, timeout=5)
        result_str = f.read()
    except URLError as err:
        print(err)
        result_str = result_str.decode()

    result = json.loads(result_str)

    if ('access_token' in result.keys() and 'scope' in result.keys()):
        if not 'brain_all_scope' in result['scope'].split(' '):
            print ('please ensure has check the  ability')
            exit()
        return result['access_token']
    else:
        print ('please overwrite the correct API_KEY and SECRET_KEY')
        exit()

"""
    读取文件
"""
def read_file(image_path):
    f = None
    try:
        f = open(image_path, 'rb')
        return f.read()
    except:
        print('read image file fail')
        return None
    finally:
        if f:
            f.close()


"""
    调用远程服务
"""
def request(url, data):
    req = Request(url, data.encode('utf-8'))
    has_error = False
    try:
        f = urlopen(req)
        result_str = f.read()
        result_str = result_str.decode()
        return result_str
    except  URLError as err:
        print(err)

def fetch_code():
    # 获取access token
    token = fetch_token()

    # 拼接通用文字识别高精度url
    image_url = OCR_URL + "?access_token=" + token

    text = ""

    # 读取图片
    file_content = read_file('./verify.jpg')

    # 调用文字识别服务
    result = request(image_url, urlencode({'image': base64.b64encode(file_content)}))

    # 解析返回结果
    result_json = json.loads(result)
    for words_result in result_json["words_result"]:
        text = text + words_result["words"]

    return text

def fetch_verifyimage():
    # 获取验证码token
    url="https://fangkong.hnu.edu.cn/api/v1/account/getimgvcode"
    result=requests.get(url)
    result_json=json.loads(result.text)
    
    token=result_json["data"]["Token"]

    # 获取图片
    urlretrieve('https://fangkong.hnu.edu.cn/imagevcode?token='+token, './verify.jpg')

    return token


def fetch_accesscookies(vercode, token):
    headers={
    'Host': 'fangkong.hnu.edu.cn',
    'Connection': 'keep-alive',
    'Accept': 'application/json, text/plain, */*',
    'User-Agent': 'Mozilla/5.0(WindowsNT10.0;Win64;x64) AppleWebKit/537.36(KHTML,likeGecko) Chrome/86.0.4240.111 Safari/537.36',
    'Content-Type': 'application/json;charset=UTF-8',
    'Origin': 'https://fangkong.hnu.edu.cn',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'Referer': 'https://fangkong.hnu.edu.cn/app/',
    'Accept-Encoding': 'gzip,deflate,br',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7'
    }
    payload={"Code":ID,"Password":PASSWORD,"WechatUserinfoCode":"","VerCode":vercode,"Token":token}

    result=requests.post('https://fangkong.hnu.edu.cn/api/v1/account/login',data=json.dumps(payload),headers=headers)

    cookies=result.cookies

    return cookies


def clockin(access_cookies):
    url = 'https://fangkong.hnu.edu.cn/api/v1/clockinlog/add'
    headers = {
        'Host':'fangkong.hnu.edu.cn',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
        'Content-Type':'application/json;charset=UTF-8',
        'Referer': 'https://fangkong.hnu.edu.cn/app/'
    }
    para = {"Longitude":null,"Latitude":null,"RealProvince":"湖南省","RealCity":"长沙市",
            "RealCounty":"岳麓区","RealAddress":"湖南大学天马学生公寓","BackState":1,"MorningTemp":"36.5","NightTemp":"36.5","tripinfolist":[]}
    
    response = requests.post(url, headers=headers, json=para, cookies=access_cookies)
    print(response.text)
    requests.post(url='https://sc.ftqq.com/'+SERVERCHAN_SCKEY+'.send?text='+response.text)
    
@retry(delay=10,tries=10)
def main():
    token=fetch_verifyimage()
    vercode=fetch_code()
    access_cookies=fetch_accesscookies(vercode,token)
    clockin(access_cookies)

if __name__ == '__main__':
    
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('id')
    parser.add_argument('password')
    parser.add_argument('api')
    parser.add_argument('secret')
    parser.add_argument('sckey')

    args = parser.parse_args()
    ID = args.id
    PASSWORD = args.password
    API_KEY = args.api
    SECRET_KEY = args.secret
    SERVERCHAN_SCKEY = args.sckey
    
    main()
