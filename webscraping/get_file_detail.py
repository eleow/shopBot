lot #!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 30 16:03:19 2020

@author: shashanknigam
"""

"""
Table designing: 
    
    Main Table(created earlier) : Product name, URL,Image URL,price
    Description : Product name,Description, detailed description
    Feature : 
Among the features following are the major identifed: 
    
'Additional Tech Specs','Availability','Cable Length (cm)','Cable Style','Colour','Country of Manufacture','Driver Configuration','Features','Frequency Response (Hz)','Headphone Design','Impedance (Ω)','Input Connectivity','Output Power','Package Contents','Product Type','Product Weight (g)','Sensitivity','Signal-to-Noise Ratio (SNR)','Style/Type', 'Total Harmonic Distortion (THD)','Warranty','Web Reviews'}    

Thus intializing the dictionary for the same. This can be used for the    


For Description we maintain the excel sheet as: Name, url, Feature
For each of the feature description we can have following details (Dictionary table): Feature_name: Description
The site contains the data under <div  class="std">
<li> contains each of the list name. 
Since the data is split on the new line for cleaning purpose The characters with length less than 1or 2 character long in the string. 

For the word dictionary: 
    
    1. The site contains the general feature explaination
    2. The sencond part contains the detailed explaination of the site. 
    
The second part is usually stored as a dictionary with following details:  May or may not exists
1. Name: This is a sequence of words: we make use of pos tagging for finding the continuous occurrence of noun, np,pronoun adjective: The text is extracted from the text in <strong></strong>,img tags!!!
2. Description: It is the text sans the Name. The 
3. Product: The product containing this feature will be appended in the containing column. (Can give the list of products having same features).

h4 feature title
followed by p
strong

h3 text
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
        

"""
#Test function
def getdivlength(soup):
    div = soup.find_all('div')
    d = [d for d in div if 'class' in d.attrs.keys() and d['class']==['std']]
    #print(len(d))
    if len(d)!=0:
        if len(d[0].text.split('\n'))==1:
            if len(d[0].text.split('-'))==1:
                print(d[0].text.split('-'))
            return len(d[0].text.split('-')),d[0].text.split('-')
        else:
            return len(d[0].text.split('\n')),d[0].text.split('\n')
    else: 
        return 0,0
"""

#Function gives the description and features
def getDescriptions(url,name,id):
    
    s = readwebPage(url)
    populateFeatures(s,url,name)
    div = s.find_all('div')
    d = [d for d in div if 'class' in d.attrs.keys() and d['class']==['std']]
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
        if '.' in str(i['alt']):
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
        

df = pd.read_excel('treoo.xls',index_col=0,names=['ID','Name','URL','IMAGE','PRICE'])    

url = df.URL
name = df.Name
for i in range(len(url)):
    print(i)
    #populateFeatures(url[i],name[i])
    getDescriptions(url[i],name[i],i)
   
    
df1 = pd.DataFrame(features)  
df2 = pd.DataFrame(Feature_dictionary)  
df3 = pd.DataFrame(Description)  


df1.to_excel('/Users/shashanknigam/downloads/nlp_project/shopBot/webscraping/features_treoo.xls')  
df2.to_excel('/Users/shashanknigam/downloads/nlp_project/shopBot/webscraping/Feature_dictionary.xls')  
df3.to_excel('/Users/shashanknigam/downloads/nlp_project/shopBot/webscraping/Description.xls')  

"""
The data for the product attribute are of the form 

class "label" : 
class "data"  :
label = contains: the label heading
class


Package contents : 
color
Warranty
Availability ---Not Required. 
Product type --- Not required
Style 
Features
Driver Configuration
Headphone design
Cable Style


Product weight:-  324 g
Frequency response

Impedence

Sensitivity

Output power

Additional  tech specs 


h3: next sibling is not correct 
"""
    
    