 #!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  2 16:14:12 2020

@author: shashanknigam
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 30 16:03:19 2020

@author: shashanknigam
"""

"""
Earphone feature extraction
"""


Description = {"Name":[],"URL":[],"Features":[],"Miscellaneous":[]}
#here id is a mapping from product name and the url from the original excel sheet
Feature_dictionary = {"Feature_Name":[],"Description":[],"Name":[],"ID":[]}

features = {'Name':[],
'URL':[],
'Additional Tech Specs':[]
,'Availability':[]
,'Cable Length (cm)':[]
,'Cable Style':[]
,'Colour':[]
,'Country of Manufacture':[]
,'Driver Configuration':[]
,'Features':[]
,'Frequency Response (Hz)':[]
,'Headphone Design':[]
,'Impedance (Ω)':[]
,'Input Connectivity':[]
,'Output Power':[]
,'Package Contents':[]
,'Product Type':[]
,'Product Weight (g)':[]
,'Sensitivity':[]
,'Signal-to-Noise Ratio (SNR)':[]
,'Style/Type':[]
, 'Total Harmonic Distortion (THD)':[]
,'Warranty':[]
}    

import requests
from bs4 import BeautifulSoup as soup
import pandas as pd
#import numpy as np
#import spacy 
import bs4

#nlp = spacy.load("en_core_web_sm")

def nextSibling(tag):
    while True:
        if tag.next_sibling == '' or tag.next_sibling is None:
            return None
        elif tag.next_sibling in ['\n','\xa0'] or tag.next_sibling.name=='br':
            tag = tag.next_sibling 
        else:          
            return tag.next_sibling


def nextSiblingText(tag):
    while True:
        #print(tag)
        if tag.next_sibling == '' or tag.next_sibling is None:
            return ''
        elif tag.next_sibling in ['\n','\xa0'] or tag.next_sibling.name=='br':
            tag = tag.next_sibling 
        else:
            if isinstance(tag.next_sibling,bs4.element.Tag):
                return tag.next_sibling.text
            else:
                return str(tag.next_sibling)

def readwebPage(url):
    req=requests.get(url)
    s =soup(req.content,'html.parser')
    return s

def populateFeatures(s,url,Name):
    labels =  ['Additional Tech Specs','Availability','Cable Length (cm)','Cable Style','Colour','Country of Manufacture','Driver Configuration','Features','Frequency Response (Hz)','Headphone Design','Impedance (Ω)','Input Connectivity','Output Power','Package Contents','Product Type','Product Weight (g)','Sensitivity','Signal-to-Noise Ratio (SNR)','Style/Type', 'Total Harmonic Distortion (THD)','Warranty']
    features['Name'].append(Name)
    features['URL'].append(url)
    th = s.find_all('th')
    td = s.find_all('td')
    t = [t for t in th if 'class' in t.attrs.keys() and t['class']==['label']]
    d = [t for t in td if 'class' in t.attrs.keys() and t['class']==['data']]
    for i in range(len(t)):
        index = t[i].text
        if index in labels:
            labels.remove(index)
            features[index].append(d[i].text.replace('\n','. '))
    #Encoding rest as Null or NA    
    for i in labels:
        features[i].append(" ")
        

#Function gives the description and features
def getDescriptions(url,name,id):
    s = readwebPage(url)
    populateFeatures(s,url,name)
    div = s.find_all('div')
    d = [d for d in div if 'class' in d.attrs.keys() and d['class']==['std']]
    if len(d)<2:
        return None
    Description["Name"].append(name)
    Description["URL"].append(url)
    Description["Features"].append(". ".join((d[0].text.strip().split('\n')))) 
    """
    Getting the feature of the values around..
    """
    #checking if strong is in the text..
    #print(d[1])
    strong =d[1].find_all('strong')
    for i in strong:
        Feature_dictionary["Feature_Name"].append(i.text)
        Feature_dictionary["Description"].append(nextSiblingText(i))
        Feature_dictionary["Name"].append(name)
        Feature_dictionary["ID"].append(id)
    while d[1].strong is not None:
        if isinstance(nextSibling(d[1].strong),bs4.element.Tag):
            nextSibling(d[1].strong).decompose()
            d[1].strong.decompose()
        else:
            d[1].strong.parent.decompose()
    img = d[1].find_all('img')
    for i in img:
        if 'alt' in i.attrs.keys() and '.' in str(i['alt']):
            desc = i['alt'].split('.')
            Feature_dictionary["Feature_Name"].append(desc[0])
            Feature_dictionary["Description"].append(desc[1])
            Feature_dictionary["Name"].append(name)
            Feature_dictionary["ID"].append(id)
            i.decompose()
    h4 = d[1].find_all('h4')
    for i in h4:
        Feature_dictionary["Feature_Name"].append(i.text)
        Feature_dictionary["Description"].append(nextSiblingText(i))
        Feature_dictionary["Name"].append(name)
        Feature_dictionary["ID"].append(id)
        if nextSibling(i) is not None:
            nextSibling(i).decompose()
            i.decompose()
    Description["Miscellaneous"].append(d[1].text.replace('\n',' ').strip())    
        
#Test functions    
def returndiv2(url):
    s=readwebPage(url)
    div = s.find_all('div')    
    d = [d for d in div if 'class' in d.attrs.keys() and d['class']==['std']]
    return d[1]
    
#Test Functions
def returndiv1(url):
    s=readwebPage(url)
    div = s.find_all('div')    
    d = [d for d in div if 'class' in d.attrs.keys() and d['class']==['std']]
    return d[0]
    
    

    
#def getlabelsdesc(soup):
#    th = soup.find_all('th')
#    t = [t for t in th if 'class' in t.attrs.keys() and t['class']==['label']]
#    for i in t:
#        headphone_labels.append(i.text)
        

df = pd.read_excel('/Users/shashanknigam/downloads/nlp_project/shopBot/webscraping/treoo_dataset/treoo_earphone_headphone_directory.xls',index_col=0,names=['ID','Name','URL','IMAGE','PRICE'])    

url = df.URL
name = df.Name
for i in range(len(url)):
    print(i)
    #populateFeatures(url[i],name[i])
    getDescriptions(url[i],name[i],i)
   
    
df1 = pd.DataFrame(features)  
df2 = pd.DataFrame(Feature_dictionary)  
df3 = pd.DataFrame(Description)  


df1.to_excel('/Users/shashanknigam/downloads/nlp_project/shopBot/webscraping/treoo_dataset/feature.xls')  
df2.to_excel('/Users/shashanknigam/downloads/nlp_project/shopBot/webscraping/treoo_dataset/feature_dictionary.xls')  
df3.to_excel('/Users/shashanknigam/downloads/nlp_project/shopBot/webscraping/treoo_dataset/description_earphone.xls')  

