#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 24 19:38:53 2020

@author: shashanknigam

#Function to parse the webpage and get the following details like
    #1. Product name: given by h3 tag
    #2. Producr Price: tags[1].span.span.text
    #3. Product Description(if available) :tags[3].text
    #4. Product Rating : tags[2].span.div["aria-label"]
    #5. Product total review: for j in tags[2].find_all("span"):
                                #if j.text!='':
                                    #print(j.text)
    #6. Product seller url: "https://www.google.com/"+tags[0].a["href"]
    #7. Product image url: Having issues in this :() 
    #8. Product tags : tags[4].text.split('·')
    #9. Seller Name: tags[1].a.text
Needs cleaning of the data
"""
from selenium import webdriver
from bs4 import BeautifulSoup as s
import pandas as pd

#Function to open the webpage using selenium and extracting the details
def webPage(url):
    #browser can be changed here operating in mac so using safari
    browser = webdriver.Chrome('/Users/shashanknigam/Downloads/Beautiful Soup/chromedriver')
    browser.get(url)
    contents = browser.page_source
    #time.sleep(10)
    browser.close()
    return contents

    
#List for the product name
pName=[]
#List of pPrice
pPrice=[]
#List of Product Description
pDescription=[]
#List of Product Rating
pRating=[]
#List of Product average rating
pTR=[]
#List of product seller url
pSUrl=[]
#product tags
ptags = []
#Product seller name
pSeller = []

def getParentTags(source):
    tag = source.parent.parent.parent
    tags=[]
    for i in tag.children:
        tags.append(i)
    return tags
    
#Function Parser informations 

def parser(url):
    soup = s(webPage(url),'html.parser')
    h3 = soup.find_all('h3')
    l = len(h3)
    if l!=0:
        h3 = h3[:20] # Each page contains 20 items only .
        for tag in h3:
            pName.append(str(tag.string))      
            tags=getParentTags(tag)
            pSeller.append(tags[1].a.text)
            pSUrl.append("https://www.google.com"+tags[0].a["href"])
            pPrice.append(tags[1].span.span.text)
            if tags[2]['class']==['hBUZL', 'Rv2Cae']:        
                for j in tags[2].find_all("span"):
                    if j.text!="":
                        pTR.append(j.text.split()[0])
                pRating.append(tags[2].span.div["aria-label"])
                pDescription.append(tags[3].text)
                if len(tags)>4 and tags[4]["class"] == ['hBUZL']:
                    ptags.append(','.join(tags[4].text.split('·')))
                else:
                    ptags.append('')
                
            else:
                pTR.append('')
                pDescription.append(tags[2].text)
                ptags.append('')
                pRating.append('')
        return True        
    else:
        return False
#Testing and debuging the function
def test_tags(h3):
    print(h3.string)
    tags = getParentTags(h3)
    print("Number:",len(tags))
    print("Seller:",tags[1].a.text)
    print("Site:https://www.google.com"+tags[0].a["href"])
    
    if tags[2]['class'] == ['hBUZL', 'Rv2Cae']:
        for j in tags[2].find_all("span"):
            if j.text!="":
                print("Total Review:",j.text)
        print("Rating Stars:",tags[2].span.div["aria-label"])
        print("Description:",tags[3].text)
        if len(tags)>4 and tags[4]["class"] == ['hBUZL']:
            print("Tags:",','.join(tags[4].text.split('·')))
    else:
        print("Description:",tags[2].text)
    print("Price:",tags[1].span.span.text)         
    

#Google has around 20 webpages for headphones across we are navigating through the webpages until there are no pages of results. 
e=True
i=0


while e:
    e=parser("https://www.google.com/search?q=headphones&tbs=vw:l,ss:44&tbm=shop&sxsrf=ACYBGNSksZM-VBAgL4fWgXhoZsQmGKSVLg:1579867580549&ei=vN0qXpjxIOfWz7sPyt-lyAY&start="+str(10*i)+"&sa=N&ved=0ahUKEwiYv7ivmZznAhVn63MBHcpvCWkQ8tMDCKgE&biw=1280&bih=689")    
    i+=2
    
#Converting the list into data frame
df = pd.DataFrame({
        "ProductName":pName,
        "Seller": pSeller,
        "Seller URL":pSUrl,
        "Product Price":pPrice,
        "Product Total Reviews":pTR,
        "Rating":pRating,
        "Product Description":pDescription,
        "Tags":ptags
        })
#Saving as an excel
df.to_excel('/Users/shashanknigam/downloads/nlp_project/shopBot/webscraping/googleProductList.xls')        
