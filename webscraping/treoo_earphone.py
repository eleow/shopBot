#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 28 21:24:36 2020

@author: shashanknigam

The website treoo.com has following details: 
1. Image url
2. Product name
3. Product Price
4. Product URL
    
    
"""
from bs4 import BeautifulSoup  as s
import requests
import pandas as pd
import re

pUrl = []
pName = []
pIURL = []
pPrice = []
plist=[]
def getProducts(url):
    #print(url)
    request = requests.get(url)
    soup = s(request.content,'html.parser')
    li = soup.find_all('li')
    items = [i for i in li if 'class' in i.attrs.keys() and i['class']==['item', 'last']]
    for i in items:
        #print(i)
        #Adding only the unique set of product name
        if re.sub('- \w+',"",re.sub("\(.*\)","",i.a['title']).strip()).strip().lower() not in plist:
            
            pUrl.append(i.a['href'])
            pName.append(re.sub('- \w+',"",re.sub("\(.*\)","",i.a['title']).strip()).strip())
            plist.append(re.sub('- \w+',"",re.sub("\(.*\)","",i.a['title']).strip()).strip().lower())
            #print(i.a['title'])
            pIURL.append(i.img['src'])
            p = i.find_all('p')
            #print(p)
            para = [j for j in p if 'class' in j.attrs.keys() and j['class']==['special-price']]
            if len(para)==0:
                p = i.find_all('div')
                para = [j for j in p if 'class' in j.attrs.keys() and j['class']==['price-box']]
                #print(para)
            price = [j  for j in para[0].text.split('\n') if '$' in j]
            pPrice.append(price[0])

#Base URL
URL = 'http://store.treoo.com/earphone.html?limit=90&p='
i=1
e=True
for i in range(1,12):
    #print(i)
    getProducts('http://store.treoo.com/headphone.html?limit=90&p='+str(i))
    #i+=1
for i in range(1,19):
    getProducts("http://store.treoo.com/earphone.html?limit=90&p="+str(i))
    
df = pd.DataFrame({
        "Product Name":pName,
        "Product URL":pUrl,
        "Product Image URL":pIURL,
        "Product Price":pPrice
        })    

df.to_excel('/Users/shashanknigam/downloads/nlp_project/shopBot/webscraping/treoo_dataset/treoo_earphone_headphone_directory.xls')        
