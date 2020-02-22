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
import pandas as pd
from bs4 import BeautifulSoup as soup 
import bs4
import sys
import traceback

product_dict={"ASIN":[],"Name":[]}
productDetails = {"ASIN":[],"Name":[],"Average Rating":[],"TotalRating":[],"Price":[],"Features":[]}
Description = {"ASIN":[],"ShortDescription":[],"LongDescription":[]}
productReview = {"ASIN":[],"Date":[],"Rating":[],"Title":[],"Detail":[]}
productQA = {"ASIN":[],"Question":[],"Answer":[]}
productInformation={"ASIN":[]} #Rest of the fields are optional
productRating={"ASIN":[],"5":[],"4":[],"3":[],"2":[],"1":[]}
ASIN=""
#QA= {"Question":[],"Answers":[],"ASIN":[]}
#customerReviews = {"ASIN":[],"UserRating":[],"Title":[],"detailedReview":[]}



def readWebpage(url):
    browser = webdriver.Chrome('/Users/shashanknigam/Downloads/Beautiful Soup/chromedriver')
    browser.get(url)
    contents = browser.page_source
    #time.sleep(10)
    browser.close()
    return contents

def getSoup(url):
    s = soup(readWebpage(url),'html.parser')
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
    s_div = get(s,'div','class')
    qa_div = [q for q in s_div if q['class']==['celwidget']]
    
    if len(qa_div)>1:
        qa_div = qa_div[1]
    else:
        qa_div = qa_div[0]
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
        next_url='https://www.amazon.com/'+li_last[0].a['href']
    return QA,next_url

def parseReview(url,review,ASIN):
    #cm_cr-review_list
    
    s=getSoup(url)
    s_div = get(s,'div','id')
    div_reviews = [d for d in s_div if d['id']=="cm_cr-review_list"][0]
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
            pass
        
            
    li = get(s,'li','class')
    next_url = [l for l in li if l['class']==["a-last"]]
    if len(next_url)>0:
        url ='https://www.amazon.com'+next_url[0].a['href']
    else:
        url=None
    #span 
        # data-hook = "review-date"
        # i data-hook "review-star-rating"
        # span data-hook "review-title"
    #a-section review aok-relative    
    return url,review

"a-section","celwidget"


def parseAmazon(url):
    global product_dict,productDetails,Description,productQA,productInformation,ASIN,productReview
    ASIN=""
    s=getSoup(url)
    s_span = get(s,'span','id')
    try:
        title = [t for t in s_span if t['id']=="productTitle"]
        title = title[0].text.strip()
        numberOfRating = [r for r in s_span if r['id']=="acrCustomerReviewText"]
        numberOfRating = numberOfRating[0].text.strip()
        averageRating = [i for i in s_span if i['id']=="acrPopover"]
        averageRating = averageRating[0].text.strip()
        productPrice = [p for p in s_span if (p['id']=="priceblock_ourprice" or p['id']=="priceblock_saleprice")]
        productPrice = productPrice[0].text
        s_div = get(s,'div','id')
        features = [f for f in s_div if f['id']=="feature-bullets"]
        features = features[0].text.strip().replace('\n','').replace('\t','')
        
        product_Information =[pi for pi in s_div if pi['id']=='prodDetails']   
        pi_th = get(product_Information[0],'th')
        pi_td = get(product_Information[0],'td')
        pi_th_text = [t.text.strip() for t in pi_th if t.text.strip()!='']
        pi_td_text = [t.text.strip().replace('\n','').replace('\t','') for t in pi_td if t.text.strip()!='']
        label_col = []
        
        for i in range(len(pi_th_text)):
            if pi_th_text[i]!="Customer Reviews":
                if pi_th_text[i]=="ASIN":
                    ASIN = pi_td_text[i]
                label_col.append(pi_th_text[i])
                if pi_th_text[i] not in  productInformation.keys():
                    productInformation[pi_th_text[i]]=[]
                productInformation[pi_th_text[i]].append(pi_td_text[i])
        for i in productInformation.keys():
            if i not in label_col:
                productInformation[i].append("")
        
        
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
                if h3_title_text[i]!="OTHER FEATURES":
                    Description['ASIN'].append(ASIN)
                    Description['ShortDescription'].append(h3_title_text[i])
                    Description['LongDescription'].append(p_description_text[j])
                    #product_description[h3_title_text[i]]=p_description_text[j]
                j+=1
        
            for i in range(len(h4_title_text)):
                Description['ASIN'].append(ASIN)
                Description['ShortDescription'].append(h4_title_text[i])
                Description['LongDescription'].append(p_description_text[j])
                #product_description[h4_title_text[i]]=p_description_text[j]
                j+=1
        else:
            productDescription = [p for p in s_div if p['id']=="productDescription"]
            productDescription_b = get(productDescription[0],'b')
            for i in productDescription_b:
            #print(i.text.strip(),getNextSiblingText(i).strip())
                if getNextSiblingText(i).strip()!='':
                    Description['ASIN'].append(ASIN)
                    Description['ShortDescription'].append(i.text.strip())
                    Description['LongDescription'].append(getNextSiblingText(i).strip())
        #            product_description[i.text.strip()] = getNextSiblingText(i).strip()
        
    

        
        qa_desc = [q for q in s_div if q['id']=='ask_lazy_load_div']
        qa_url = qa_desc[0].a['href']
    
    
        #QA = {}
        while qa_url!='':
            productQA,qa_url=parseQA(qa_url,productQA,ASIN)
            review_summary = [d for d in s_div if d['id']=='reviewsMedley'][0]
        
        
        rev_span = get(review_summary,'span','class')
    
    
        global productRating
        rev_span = [r for r in rev_span if r['class']==["a-size-base"]]
        for i in [0,2,4,6,8]:
            productRating['ASIN'].append(ASIN)
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
        rev_div_footer = [r for r in rev_div if r['id']=="reviews-medley-footer"]
        rating_url = 'https://www.amazon.com'+rev_div_footer[0].a['href']
        while rating_url is not None:
            rating_url,productReview=parseReview(rating_url,productReview,ASIN)
    except:
        print(sys.exc_info())
        print(traceback.format_exc())





