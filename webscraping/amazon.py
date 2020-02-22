#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  5 00:04:41 2020

@author: shashanknigam

web parser for amazon: 

Things to be extracted: 1. Title of the product    span id = "productTitle"
    2. Number of rating : span id = acrCustomerReviewText
    3. Average rating given:span class a-icon-alt
    4. Description: div id = featurebullets_feature_div.text
    5. Product description: heading description format h3:a-spacing-mini :- neighboring text p class="a-spacing-base"
    6. Other features if any h4 class="a-spacing-mini" p : afterwards.  
    -- later consideration 6.5: Comparison id=HLCXComparisonTable 
         item heading: tr class="comparison_table_image_row"
                img.src :Name 
                class="a-row a-spacing-top-small"
                
                
    7. Product information div id = "productDetails_detailBullets_sections1"
    
        1. Product dimensions th  label td value
        2. Item weight
        3. Shipping weight
        4. Manufacturer
        5. ASIN
        6. Model Number
        7. Customer reviews
        8. Best sellers rank
        9. Warantee if any
    8. Question answers:  div =class="a-section a-spacing-none askBtfTopQuestionsContainer" ;  span class = "a-text-bold" next sibling id  (class="a-declarative")the child question next span class=  askLongText   class="a-color-tertiary a-nowrap" for r the next teritory wrap
    9. Customer reviews: all if possible : - class="cr-lighthouse-term " (terms)
                                        1. data-hook="review-star-rating" user  rating 
                                        2. data-hook="review-title" 
                                        3. class="a-row a-spacing-small review-data" detailed review
                                        4. data-hook="see-all-reviews-link-foot"
                                        5. class="a-last"    
    10. Price: span id = priceblock_ourprice
    

Hanumanji 
a-section celwidget
cr-dp-lighthut
["a-fixed-left-grid","a-spacing-base"]

['a-fixed-left-grid-col', 'a-col-right']


reviews-medley-footer


id="cr-dp-desktop-lighthut"
["a-fixed-right-grid-col","cm_cr_grid_center_right"]

"""

"""
Getting each details out:
"""

from selenium import webdriver
import time
from bs4 import BeautifulSoup as soup 
import bs4
import sys
import traceback
import numpy as np
import pandas as pd
import gc

product_dict={"ASIN":[],"Name":[]}
productDetails = {"ASIN":[],"Name":[],"Average Rating":[],"TotalRating":[],"Price":[],"Features":[]}
Description = {"ASIN":[],"ShortDescription":[],"LongDescription":[]}
productReview = {"ASIN":[],"Date":[],"Rating":[],"Title":[],"Detail":[]}
productQA = {"ASIN":[],"Question":[],"Answer":[]}
productInformation={"ASIN":[]} #Rest of the fields are optional
productRating={"ASIN":[],"5":[],"4":[],"3":[],"2":[],"1":[]}
ASIN=""
failed = []
#QA= {"Question":[],"Answers":[],"ASIN":[]}
#customerReviews = {"ASIN":[],"UserRating":[],"Title":[],"detailedReview":[]}
pages=0
driver = 0

ASIN_LIST = []

def initASIN_LIST():
    global ASIN_LIST
    df = pd.read_excel('/Users/shashanknigam/downloads/nlp_project/shopBot/webscraping/AmazonDataSet/ProductDictionary.xlsx')
    ASIN_LIST = list(df['ASIN'])
    

def readWebpage(url,driver_not_in_use=-1):
    try:
        global pages
        global driver
        driver = np.random.randint(0,2)
        while driver==driver_not_in_use:
            driver = np.random.randint(0,2)
        if driver ==0:
            browser = webdriver.Safari() 
        elif driver==1:
            browser = webdriver.Chrome('/Users/shashanknigam/Downloads/Beautiful Soup/chromedriver')
        #elif driver==2:
        #    browser=webdriver.Firefox('/Users/shashanknigam/Downloads/Beautiful Soup/')
        browser.get(url)
        contents = browser.page_source
        #time.sleep(1)
        browser.close()
        del browser
        return contents
    except:
        try:
            driver = np.random.randint(0,2)
            if driver ==0:
                browser = webdriver.Safari() 
            elif driver==1:
                browser = webdriver.Chrome('/Users/shashanknigam/Downloads/Beautiful Soup/chromedriver')
            #elif driver==2:
            #    browser=webdriver.Firefox('/Users/shashanknigam/Downloads/Beautiful Soup/')
            browser.get(url)
            browser.close()
            del browser
            return contents
        except:
            print(sys.exc_info())
            print(traceback.format_exc())
            
            return None
    

    
    
    #time.sleep(10)
    

def getSoup(url):
    global driver
    w = readWebpage(url)
    if w is not None:
        s = soup(w,'html.parser')
        while "Robot Check" in s.text:
            w = readWebpage(url,driver)
            s = soup(w,'html.parser')
    else: 
        s=None
    return s

def get(s,tag,attr=None):
    
    if attr is  None:
        return s.find_all(tag)
    else:
        #print("searching for attribute:"+attr)
        tags = s.find_all(tag)
        return [t for t in tags if attr in t.attrs.keys()]

def getNextSibling(tag):
    while True:
        if tag.next_sibling == '' or tag.next_sibling is None:
            return None
        elif tag.next_sibling in ['\n','\xa0'] or tag.next_sibling.name=='br':
            tag = tag.next_sibling 
        else:          
            return tag.next_sibling
 
def getNextSiblingText(tag):
    while True:
        #print(tag)
        if tag.next_sibling == '' or tag.next_sibling is None:
            return ''
        elif tag.next_sibling in ['\n','\xa0'] or tag.next_sibling.name=='br' or tag.next_sibling==' ':
            tag = tag.next_sibling 
        else:
            if isinstance(tag.next_sibling,bs4.element.Tag):
                return tag.next_sibling.text
            else:
                return str(tag.next_sibling)

def parseQA(url,QA,ASIN):
    s=getSoup(url)
    if s is not None:
        s_div = get(s,'div','class')
    
        qa_div = [q for q in s_div if q['class']==['celwidget']]
    
        if len(qa_div)>1:
            qa_div = qa_div[1]
        elif len(qa_div)==1: 
            qa_div = qa_div[0]
        else:
            qa_div=None
        if qa_div is not None:
            qa=get(qa_div,'div','class')
            qa_inner = [q for q in qa if q['class']==['a-fixed-left-grid-col', 'a-col-right']]
    #print("qa_inner",len(qa_inner))
            for i in qa_inner:
                qa_inner_temp=get(i,'div','class')
                qa_inner_inner=[q for q in qa_inner_temp if q['class']==['a-fixed-left-grid-col', 'a-col-right']]
                #print(len(qa_inner_inner))
                if len(qa_inner_inner)>1:
                    QA['ASIN'].append(ASIN)
                    QA['Question'].append(qa_inner_inner[0].text.strip())
                    QA['Answer'].append(qa_inner_inner[1].span.text.strip())
                        #QA[qa_inner_inner[0].text.strip()]=qa_inner_inner[1].span.text.strip() 
                elif len(qa_inner_inner)==1:
                    #print(qa_inner_inner)
                    QA['ASIN'].append(ASIN)
                    QA['Question'].append(qa_inner_inner[0].text.strip())
                    QA['Answer'].append('')
                    #QA[qa_inner_inner[0].text.strip()]=''
            li = get(s,'li','class')
            li_last = [l for l in li if l['class']==['a-last']]
            next_url = ""
            if len(li_last)!=0:
                if 'https://www.amazon.com/' not in li_last[0].a['href']:
                    next_url='https://www.amazon.com/'+li_last[0].a['href']
                else: 
                    next_url= li_last[0].a['href']
        else:
            next_url=""
        s.decompose()    
    else:
        next_url=""        
    return QA,next_url

def parseReview(url,review,ASIN):
    #cm_cr-review_list
    s=getSoup(url)
    if s is not None:
        s_div = get(s,'div','id')
        div_reviews = [d for d in s_div if d['id']=="cm_cr-review_list"]
        if len(div_reviews)>0:
            div_reviews=div_reviews[0]
            div_review = get(div_reviews,"div","data-hook")
            div_r = [r for r in div_review if r['data-hook']=='review']
            for i in div_r:
                try:
                    rating_i = get(i,'i','data-hook')
                    rating = [r for r in rating_i if r['data-hook']=="review-star-rating"]
                    rating = rating[0].text.strip()
                    span_d = get(i,'span','data-hook')
                    date = [d for d in span_d if d['data-hook']=="review-date"]
                    date = date[0].text.strip()
                    review_t = get(i,'a','data-hook')
                    review_title=[t for t in review_t if t['data-hook']=="review-title"]
                    review_title = review_title[0].text.strip()
                    review_b=[b for b in span_d if b['data-hook']=="review-body"]
                    review_b = review_b[0].text.strip()
                    review["ASIN"].append(ASIN)
                    review["Rating"].append(rating)
                    review["Date"].append(date)
                    review["Title"].append(review_title)
                    review["Body"].append(review_b)
                except:
                    print(sys.exc_info())
                    print(traceback.format_exc())
                    pass
            li = get(s,'li','class')
            next_url = [l for l in li if l['class']==["a-last"]]
            if len(next_url)>0:
                url ='https://www.amazon.com'+next_url[0].a['href']
            else:
                print("Error")
                url=None
        else:
            url=None
    
        s.decompose()
    else:
        
        url=None        
    #span 
        # data-hook = "review-date"
        # i data-hook "review-star-rating"
        # span data-hook "review-title"
    #a-section review aok-relative    
    return url,review

def appendExcel(filename,df1):
    df = pd.read_excel(filename,index_col=0)
    df = df.append(df1)
    df.to_excel(filename)
    df=None

def parseAmazon(url):
    #global pages
    #global product_dict,productDetails,Description,productQA,productInformation,ASIN,productReview,failed
    global pages,failed,ASIN_LIST
    if pages==0:
        initASIN_LIST()
    product_dict={"ASIN":[],"Name":[]}
    productDetails = {"ASIN":[],"Average Rating":[],"TotalRating":[],"Price":[],"Features":[]}
    Description = {"ASIN":[],"ShortDescription":[],"LongDescription":[]}
    productReview = {"ASIN":[],"Date":[],"Rating":[],"Title":[],"Body":[]}
    productQA = {"ASIN":[],"Question":[],"Answer":[]}
    productInformation={"ASIN":[]} #Rest of the fields are optional
    productRating={"ASIN":[],"5":[],"4":[],"3":[],"2":[],"1":[]}
    ASIN=""
    s=getSoup(url) 
    if s is not None:
        s_span = get(s,'span','id')
        try:
            title = [t for t in s_span if t['id']=="productTitle"]
            title = title[0].text.strip()
            numberOfRating = [r for r in s_span if r['id']=="acrCustomerReviewText"]
            if len(numberOfRating)>0:
                numberOfRating = numberOfRating[0].text.strip()
            else: 
                numberOfRating="Unk"
            averageRating = [i for i in s_span if i['id']=="acrPopover"]
            if len(averageRating)>0:
                averageRating = averageRating[0].text.strip()
            else:
                averageRating="Unk"
            productPrice = [p for p in s_span if (p['id']=="priceblock_ourprice" or p['id']=="priceblock_saleprice")]
            if len(productPrice)>0:
                productPrice = productPrice[0].text
            else:
                productPrice ="Unk"
            s_div = get(s,'div','id')
            features = [f for f in s_div if f['id']=="feature-bullets"]
            if len(features)>0:
                features = features[0].text.strip().replace('\n','').replace('\t','')
            else:
                features=""
            try:
                product_Information =[pi for pi in s_div if pi['id']=='prodDetails']   
                pi_th = get(product_Information[0],'th')
                pi_td = get(product_Information[0],'td')
                pi_th_text = [t.text.strip() for t in pi_th if t.text.strip()!='']
                pi_td_text = [t.text.strip().replace('\n','').replace('\t','') for t in pi_td if t.text.strip()!='']
                #print(pi_th_text,pi_td_text)
                label_col = []
                if pages!=0:
                    columns = pd.read_excel('/Users/shashanknigam/downloads/nlp_project/shopBot/webscraping/AmazonDataSet/ProductInformation.xlsx').columns
                else: 
                    columns= None
                #print(columns)    
                for i in range(len(pi_th_text)):
                    if pi_th_text[i]!="Customer Reviews":
                        if pi_th_text[i]=="ASIN":
                            ASIN = pi_td_text[i]
                        label_col.append(pi_th_text[i])
                        if columns is  None:
                            if pi_th_text[i] not in  productInformation.keys() :
                                productInformation[pi_th_text[i]]=[]
                                productInformation[pi_th_text[i]].append(pi_td_text[i])
                            else:
                                productInformation[pi_th_text[i]].append(pi_td_text[i])
                        else:
                           if pi_th_text[i] not in  productInformation.keys() and  pi_th_text[i] in columns:
                               productInformation[pi_th_text[i]]=[]
                               productInformation[pi_th_text[i]].append(pi_td_text[i])
                           elif pi_th_text[i] in columns:
                               productInformation[pi_th_text[i]].append(pi_td_text[i])
                        #for i in productInformation.keys():
                        #    if i not in label_col:
                        #        productInformation[i].append("")
                if len(pi_th_text)==0:
                    heading=""
                    body=""
                    
                    for i in range(0,len(pi_td_text)-1,2):
                        #print(i,len(pi_td_text))
                        heading = pi_td_text[i]
                        body = pi_td_text[i+1]
                        #print(i,heading,body)
                        if heading=="ASIN":
                            ASIN = body
                            #print(ASIN)
                        if heading!="Customer Reviews":    
                            if columns is None:    
                                if heading not in productInformation.keys():
                                    productInformation[heading]=[]
                                    productInformation[heading].append(body)
                                else:
                                    productInformation[heading].append(body)
                        
                            else:
                                if heading not in productInformation.keys() and heading in columns:
                                    productInformation[heading]=[]
                                    productInformation[heading].append(body)
                                elif  heading in columns:
                                    productInformation[heading].append(body)
                     
            except:
                ASIN="Not available"
                #print(sys.exc_info())
                #print(traceback.format_exc())
                
            if ASIN not in ASIN_LIST:    
                productDescription = [p for p in s_div if p['id']=="aplus"]
                if len(productDescription)!=0:
                    h3_title = get(productDescription[0],'h3')
                    h4_title = get(productDescription[0],'h4')
                    p_description = get(productDescription[0],'p')
                    h3_title_text = [text.text.strip() for text in h3_title if text.text!="" and text.text.strip()!='']
                    p_description_text = [text.text.strip() for text in p_description if text.text!="" and text.text is not None and text.text.strip()!='']
                    h4_title_text =[text.text.strip() for text in h4_title if text.text!="" and text.text.strip()!='']
                    j=0
                    for i in range(len(h3_title_text)):
                        if h3_title_text[i] not in ["OTHER FEATURES","FEATURES"]:
                            Description['ASIN'].append(ASIN)
                            Description['ShortDescription'].append(h3_title_text[i])
                            Description['LongDescription'].append(p_description_text[j])
                            #product_description[h3_title_text[i]]=p_description_text[j]
                            j+=1
        
                    for i in range(len(h4_title_text)):
                        Description['ASIN'].append(ASIN)
                        Description['ShortDescription'].append(h4_title_text[i])
                        if j<len(p_description_text)-1:
                            Description['LongDescription'].append(p_description_text[j])
                        else:
                            Description['LongDescription'].append("")
                        #product_description[h4_title_text[i]]=p_description_text[j]
                        j+=1
                else:
                    productDescription = [p for p in s_div if p['id']=="productDescription"]
                    #print(productDescription)
                    if len(productDescription)>0:
                        productDescription_b = get(productDescription[0],'b')
                        for i in productDescription_b:
                        #print(i.text.strip(),getNextSiblingText(i).strip())
                            if getNextSiblingText(i).strip()!='':
                                Description['ASIN'].append(ASIN)
                                Description['ShortDescription'].append(i.text.strip())
                                Description['LongDescription'].append(getNextSiblingText(i).strip())
        #                 product_description[i.text.strip()] = getNextSiblingText(i).strip()
            #print(Description)
                qa_desc = [q for q in s_div if q['id']=='ask_lazy_load_div']
                qa_url = qa_desc[0].a['href']
    
    
            #QA = {}
                while qa_url!='':
                    productQA,qa_url=parseQA(qa_url,productQA,ASIN)
                    
                    review_summary = [d for d in s_div if d['id']=='reviewsMedley'][0]
            
        
                rev_span = get(review_summary,'span','class')
                #global productRating
                rev_span = [r for r in rev_span if r['class']==["a-size-base"]]
                #print(rev_span)
                productRating['ASIN'].append(ASIN)
                for i in [0,2,4,6,8]:
                    
                    if "1" in rev_span[i].text.strip():
                        productRating["1"].append(rev_span[i+1].text.strip())
                    elif "2" in rev_span[i].text.strip():
                        productRating["2"].append(rev_span[i+1].text.strip())
                    elif "3" in rev_span[i].text.strip():
                        productRating["3"].append(rev_span[i+1].text.strip())
                    elif "4" in rev_span[i].text.strip():
                        productRating["4"].append(rev_span[i+1].text.strip())
                    else:
                        productRating["5"].append(rev_span[i+1].text.strip())
                    #      rating[rev_span[i].text.strip()] = rev_span[i+1].text.strip()
            
                rev_div = get(review_summary,'div','id')
                rev_div_footer = [r for r in rev_div if r['id']=="reviews-medley-footer" or "footer" in r['id']]
                #print(len(rev_div_footer),rev_div_footer)
                if len(rev_div_footer)>0:
                    try:
                        if 'https://www.amazon.com' in rev_div_footer[0].a['href']:
                            rating_url = rev_div_footer[0].a['href']
                        else:    
                            rating_url = 'https://www.amazon.com'+rev_div_footer[0].a['href']
                    except:
                        rating_url = None
                        while rating_url is not None:
                            rating_url,productReview=parseReview(rating_url,productReview,ASIN)
                product_dict['ASIN'].append(ASIN)
                product_dict['Name'].append(title)
                productDetails['ASIN'].append(ASIN)
                productDetails['Average Rating'].append(averageRating)
                productDetails['TotalRating'].append(numberOfRating)
                productDetails['Price'].append(productPrice)
                productDetails['Features'].append(features)
                #(productReview)
                #print(productRating)
                print("URL processed",pages+1)
                if pages==0:
                    pd.DataFrame(product_dict).to_excel('/Users/shashanknigam/downloads/nlp_project/shopBot/webscraping/AmazonDataSet/ProductDictionary.xlsx')
                    pd.DataFrame(productDetails).to_excel('/Users/shashanknigam/downloads/nlp_project/shopBot/webscraping/AmazonDataSet/ProductDetails.xlsx')
                    pd.DataFrame(Description).to_excel('/Users/shashanknigam/downloads/nlp_project/shopBot/webscraping/AmazonDataSet/Description.xlsx')
                    pd.DataFrame(productQA).to_excel('/Users/shashanknigam/downloads/nlp_project/shopBot/webscraping/AmazonDataSet/QA_'+ASIN+'.xlsx')
                    pd.DataFrame(productInformation).to_excel('/Users/shashanknigam/downloads/nlp_project/shopBot/webscraping/AmazonDataSet/ProductInformation.xlsx')
                    pd.DataFrame(productRating).to_excel('/Users/shashanknigam/downloads/nlp_project/shopBot/webscraping/AmazonDataSet/productRating.xlsx')
                    pd.DataFrame(productReview).to_excel('/Users/shashanknigam/downloads/nlp_project/shopBot/webscraping/AmazonDataSet/prodcutReview_'+ASIN+'.xlsx')            
                else:
                    appendExcel('/Users/shashanknigam/downloads/nlp_project/shopBot/webscraping/AmazonDataSet/ProductDictionary.xlsx',pd.DataFrame(product_dict))
                    appendExcel('/Users/shashanknigam/downloads/nlp_project/shopBot/webscraping/AmazonDataSet/ProductDetails.xlsx',pd.DataFrame(productDetails))
                    appendExcel('/Users/shashanknigam/downloads/nlp_project/shopBot/webscraping/AmazonDataSet/Description.xlsx',pd.DataFrame(Description))
                    appendExcel('/Users/shashanknigam/downloads/nlp_project/shopBot/webscraping/AmazonDataSet/ProductInformation.xlsx',pd.DataFrame(productInformation))
                    appendExcel('/Users/shashanknigam/downloads/nlp_project/shopBot/webscraping/AmazonDataSet/productRating.xlsx',pd.DataFrame(productRating))
                    pd.DataFrame(productQA).to_excel('/Users/shashanknigam/downloads/nlp_project/shopBot/webscraping/AmazonDataSet/QA_'+ASIN+'.xlsx')
                    pd.DataFrame(productReview).to_excel('/Users/shashanknigam/downloads/nlp_project/shopBot/webscraping/AmazonDataSet/prodcutReview_'+ASIN+'.xlsx') 
                
                """
                with pd.ExcelWriter('/Users/shashanknigam/downloads/nlp_project/shopBot/webscraping/AmazonDataSet/ProductDictionary.xlsx',engine="openpyxl" ,mode='a') as writer:
                    pd.DataFrame(product_dict).to_excel(writer)    
                with pd.ExcelWriter('/Users/shashanknigam/downloads/nlp_project/shopBot/webscraping/AmazonDataSet/ProductDetails.xlsx',engine="openpyxl",mode='a') as writer:
                    pd.DataFrame(productDetails).to_excel(writer)
                with pd.ExcelWriter('/Users/shashanknigam/downloads/nlp_project/shopBot/webscraping/AmazonDataSet/Description.xlsx',engine="openpyxl",mode='a') as writer:    
                    pd.DataFrame(productDescription).to_excel(writer)
                with pd.ExcelWriter('/Users/shashanknigam/downloads/nlp_project/shopBot/webscraping/AmazonDataSet/QA.xlsx',engine="openpyxl",mode='a') as writer: 
                    pd.DataFrame(productQA).to_excel(writer)
                with pd.ExcelWriter('/Users/shashanknigam/downloads/nlp_project/shopBot/webscraping/AmazonDataSet/ProductInformation.xlsx',engine="openpyxl",mode='a') as writer:    
                    pd.DataFrame(productInformation).to_excel(writer)
                with pd.ExcelWriter('/Users/shashanknigam/downloads/nlp_project/shopBot/webscraping/AmazonDataSet/productRating.xlsx',engine="openpyxl",mode='a') as writer:    
                    pd.DataFrame(productRating).to_excel(writer)
                with pd.ExcelWriter('/Users/shashanknigam/downloads/nlp_project/shopBot/webscraping/AmazonDataSet/productReview.xlsx',mode='a'):
                    pd.DataFrame(productReview).to_excel(writer)
                """    
            pages+=1
            product_dict=None
            productDetails=None
            Description=None
            productQA=None
            productInformation=None
            productRating=None
            productReview=None
        except:
            print(sys.exc_info())
            print(traceback.format_exc())
            print(url)
            failed.append(url)
        s.decompose()
        gc.collect()
    else:
        failed.append(url)
        print("Could Not Open ",url)