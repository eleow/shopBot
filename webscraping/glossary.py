#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Web Jan 29 11:14:36 2020

@author: eleow

The website https://www.headphones.com/pages/glossary has following details:
1. Term
2. Description of term

"""
from bs4 import BeautifulSoup  as s
# import requests
import pandas as pd
import re

# set options to be headless
from selenium import webdriver
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

# note: ensure that driver and chrome version match
chrome_driver_path = 'chromedriver' #'D:/Users/Edmund/Documents/GitHub/shopBot/webscraping/chromedriver_79.exe'
# driver = webdriver.Chrome('chromedriver', chrome_options=chrome_options)

# function definitions
def web_browser(web):
    # browser = webdriver.Safari()
    browser = webdriver.Chrome(chrome_driver_path, options=chrome_options)
    browser.get(web)
    content = browser.page_source
    return content

pTerm = []
pDesc = []

# Scrape from headphones.com/pages/glossary
url="https://www.headphones.com/pages/glossary"
webpage = web_browser(url)
soup = s(webpage,'html.parser')

soupGlossary = s(str(soup))
for i,p in enumerate(soupGlossary.select("div.rte.rte--nomargin p")):
  if len(p.select("b")) != 0:
    t = p.find("b").extract()

    if (p.text.strip() != ''):
      pTerm.append(t.text.strip().lower())
      pDesc.append(p.text.strip())
    # myGlossary.append((t.text, p.text))
    # print(p.text)
# myGlossary

import pandas as pd
#Converting the list into data frame
df = pd.DataFrame({
        "Term":pTerm,
        "Description": pDesc
        })

#Saving as an excel
df.to_excel('glossary.xls')
