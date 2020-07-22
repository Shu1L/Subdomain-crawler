import requests
import sys
import re
import os
import exrex
import threading
import queue
import urllib
from bs4 import BeautifulSoup
import time
import queue
import argparse
import base64
import json
import subprocess
from pyquery import PyQuery as pq
from lxml import etree
from selenium import webdriver


url_list=[]

def wirte_in_txt(yuming,url):
    with open('{}.txt'.format(yuming),'a+') as file:
            file.write(url+"\n")
            file.close()

def get_list(url,alist=url_list):
    alist.append(url)
    f_url=list(set(alist))
    for furl in f_url:
        wirte_in_txt(yuming,furl)


def spyse_spider(yuming,acc):
    for i in range(20,400,20):
        url='https://spyse.com/api/data/domain/subdomain?limit=20&offset={0}&domain={1}'.format(i,yuming)
        headers={
            "Host": "spyse.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
            "Cookie": "acc={}".format(acc)
        }
        r=requests.get(url=url,headers=headers)
        html=r.text
        url=re.findall('"is_PTR":.*?,"name":"(.*?)",',html)
        length=(len(url))
        for ul in url:
            get_list(ul)
        while length < 20:
            break
        time.sleep(2)
    print('spyse_spider爬取完成')


def fofa_spider(yuming,apikey):
    keyword = 'domain:"{}"'.format(yuming)
    keyword = keyword.encode('utf-8')
    keyword = base64.b64encode(keyword)
    keyword = keyword.decode()

    for page in range(1, 20):
        url = 'https://fofa.so/result'
        headers = {
            "Host": "fofa.so",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:48.0) Gecko/20100101 Firefox/48.0",
            "Cookie": "_fofapro_ars_session={}".format(apikey)
        }
        params = {
            'page': page,
            'qbase64': keyword
        }
        r = requests.get(url=url, params=params, headers=headers)
        html = r.text
        soup = BeautifulSoup(html, 'lxml')
        a_url = str((soup.select('.list_mod_t')))
        url = re.findall('target="_blank">(.*?)<i', a_url, re.S)
        for ul in url:
            get_list(ul)
        time.sleep(2)
    print('fofa爬取完成')

def bing_spider(yuming):
    s = requests.session()

    for first in range(1, 200, 10):
        url = 'https://www.bing.com/search'
        headers = {
            "Host": "www.bing.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
            "Cookie": "MUID=21B2752917706F2505437BAB160F6E97; SRCHD=AF=NOFORM; SRCHUID=V=2&GUID=2CA7E322B43049AEB5793BD77AB10370&dmnchg=1; MUIDB=21B2752917706F2505437BAB160F6E97; _EDGE_S=mkt=zh-cn&SID=2A2D984CB1B766650E4196B7B0C867ED; _SS=SID=2A2D984CB1B766650E4196B7B0C867ED&bIm=743; ipv6=hit=1593656891562&t=4; SRCHUSR=DOB=20200504&T=1593653296000; SRCHHPGUSR=CW=1486&CH=743&DPR=1.25&UTC=480&HV=1593653342&WTS=63729250089&DM=0"
        }
        prarms = {
            'q': 'site:{}'.format(yuming),
            'first': first
        }

        res = requests.get(url=url, headers=headers, params=prarms)
        soup = BeautifulSoup(res.text, 'lxml')
        urls = soup.select('h2')
        urls = str(urls)
        url = re.findall('href="(.*?)"', urls, re.S)

        for ul in url:
            durl = ul.split('/')[2]
            get_list(durl)

        time.sleep(2)
    print('bing爬取完成')

def baidu_spider(yuming):
    wd='site:*.{}'.format(yuming)
    s=requests.session()
    headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:73.0) Gecko/20100101 Firefox/73.0",
        "Host": "www.baidu.com",
    }
    for i in range(50):
        url='https://www.baidu.com/s'
        data={
            "wd":wd,
            "pn":i,
        }
        r=requests.get(url=url,params=data,headers=headers)
        soup=BeautifulSoup(r.text,'lxml')
        for so in soup.select('#content_left .t a'):
            gurl=so.get('href')
            vurl=requests.get(url=gurl,headers=headers,allow_redirects=False)
            rurl=vurl.headers['Location']
            durl=rurl.split('/')[2]
            get_list(durl)
            time.sleep(1+(i/10))
    print('baidu爬取完成')

def DNS_A_record_search(yuming):
    url = 'https://hackertarget.com/find-dns-host-records/'
    headers = {
        "Host": "hackertarget.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
        "Cookie": "_ga=GA1.2.1287617525.1593046880; _gid=GA1.2.524299199.1593494993;"
    }
    data = {
        "theinput": yuming,
        "thetest": "hostsearch",
        "name_of_nonce_field": "69f01a5966",
        "&_wp_http_referer": "%2Ffind-dns-host-records%2F"
    }
    r = requests.post(url=url, data=data, headers=headers)
    soup = BeautifulSoup(r.text, 'lxml')
    url = soup.pre.string
    urls=re.findall('(.*?),',url,re.S)
    strurl=" ".join(urls)
    reurl=re.sub('\d+.\d+.\d+.\d+','',strurl)
    lsurl=reurl.split('\n')
    for ul in lsurl:
        get_list(ul)
    print('DNS查询完成')

def SSL_spider(yuming):
    url='https://crt.sh/'
    q=yuming
    headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:73.0) Gecko/20100101 Firefox/73.0",
        "Host": "crt.sh"
    }
    data={
        'q':q
    }
    r=requests.get(url=url,params=data,headers=headers)
    html=r.text
    url=re.findall('<BR>(.*?)<BR>',html)
    for ul in url:
        un = re.sub('\*.*', '', ul)
        get_list(un)
    print('SSL查询完成')

def chaziyu_spider(yuming):
    url='https://chaziyu.com/{}'.format(yuming)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:73.0) Gecko/20100101 Firefox/73.0",
    }
    res=requests.get(url=url,headers=headers)
    html=res.text
    doc=pq(html)
    items=doc('td')
    lis=items.find('a')
    url=(lis.text())
    urls=url.split(' ')
    for ul in urls:
        get_list(ul)
    print('chaziyu爬取完毕')

def threatcrowd_spider(yuming):
    browser=webdriver.Chrome()
    browser.get('https://www.threatcrowd.org/domain.php?domain={}'.format(yuming))
    source=browser.page_source
    browser.close()
    html=etree.HTML(source)
    results=html.xpath('//td/a[contains(@href,"domain.php")]/text()')
    for result in results:
        get_list(result)
    print('threatcrowd爬取完毕')




if __name__ == '__main__':

    yuming=input("请输入域名:")
    fofaapikey=input("请输入fofaapikey:")
    acc=input("请输入spyseapi:")

    threads=[]

    d_fofa_spider=threading.Thread(target=fofa_spider,args=(yuming,fofaapikey))
    threads.append(d_fofa_spider)

    d_bing_spider=threading.Thread(target=bing_spider, args=(yuming,))
    threads.append(d_bing_spider)

    d_baidu_spider=threading.Thread(target=baidu_spider, args=(yuming,))
    threads.append(d_baidu_spider)


    d_spyse_spider=threading.Thread(target=spyse_spider, args=(yuming,acc))
    threads.append(d_spyse_spider)

    d_DNS_A_record_search=threading.Thread(target=DNS_A_record_search, args=(yuming,))
    threads.append(d_DNS_A_record_search)

    d_SSL_spider = threading.Thread(target=SSL_spider, args=(yuming,))
    threads.append(d_SSL_spider)

    d_threatcrowd_spider=threading.Thread(target=threatcrowd_spider,args=(yuming,))
    threads.append(d_threatcrowd_spider)

    d_chaziyu_spider=threading.Thread(target=chaziyu_spider,args=(yuming,))
    threads.append(d_chaziyu_spider)

    for thr in threads:
        print(thr)
        thr.start()
    for thr in threads:
        if thr.isAlive():
            thr.join()

    #for url in url_list:
     #   wirte_in_txt(url)

























































































































