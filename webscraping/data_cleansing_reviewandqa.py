#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 29 20:24:06 2020

@author: shashanknigam
"""

import pandas as pd
import os
import re
import sklearn
"""
1. The script to consolidate the different QA per product and Reviews per product. 
2. Clearing/Cleaning the description

Simple document is to only make use of words..: Issue with this model is it will not consider emoticons. 

For emoticon we can get the dictionary to replace the same in the original review text. 

Getting the clustering information based on the raw word counts per document? Lets explore. 

Word cloud analysis

Spectral K means analysis. ???


Dimensionality reduction: Getting the related terms and coefficients. 
    1. Classic : Latent semantic analysis. Called the truncated SVD. (standard baseline and very difficult to beat.)
        Why this works: 
            Abstracting a way of dimensionality reduction. Sushing it down into 3D
            Method is singular value decomposition 
                US(singular values)V: The combination of the 3 matrices 
        Emoticon library: 
            Need a method of name entity recognition. 
                
    2. LSA cell value : PMI and LSA will have a similar distribution and tractable notation.
    How to pick a dimensionality K. How to pick Trying the bunch of values for K 
    
    sklearn.decomposition manifold composition. 
    
    
Auto encoders: 
    For learning reduced decomposition -- solution of LSA??
    X -> hidden -> X' loss (minimize X'-X) this allows the minimization. 
    Learning the auto encoder for hidden values vector representation 
    Reduce the dimensionality: Model external reconstruction and do the dimensionality reduction. 
    
    Calculation of the computation. Compress the information. 
    Hidden layer : Word 
    
Dimensionality reduction: Why is it required?? Hidden dimension 
Note: Raw counts are note

This can be used for the 


GloVe Vectors: 
    Learn the vectors of the where the dot product of the vectors are the probability distribution of the vectors: 
        
2 vectors i and k, Taking the dot product and the 2 bais term. 
    wiTw_k +bi + bk = log(Xik)
    wiTwk = log(Pik) = log(Xik) -log(Xi) : row probability : The square matrix
    Allowing the rows and columns are different. 
    wiTwk = log(Pik) = log(Xik) -log(Xi.Xk)
    This is similar to PMI:
        pmi(X,i,j) = log(Xij/expected(X,i,j)) = log(P(Xij)/P{xj}.P(xj))
        
    It is drawing same intution as PMI. 

Weighting scheme is also proposed in the original model. Need to explore more... 

Glove:
    Regularized reweighting expression. 
    Capitalizing 

GLove hyper parameters: 
    
    1.Learned representation dimensionality
    2.x_max which flattens out all high counts 
    3.alpha which sclare the values such as x .xmax
    4.Distribution of the counts. Distribution of the cell values. 
    
Glove learning: 

Glove by its nature it does not visit the documents with 0 count. 

Count matrix: wicked gnarly never occur together. 

We get rid of the bias term. We get the bias term.
Look what it happens for the  

Scaling of the network is important in most of the cases. Glove is important in most of the cases. 

Impact of the hyper parameter:
    
    Glove objetive is to learn the dot product of 2 vector and find the correlation of the vectors. 
**gensim is an arbitrary package. 

    
word2vec: 

Take a corpus and setting a window size. 
    Pair of words as the trainign label
            it   was
            it   the
            was  it
            was  the 
            was  best
            the  was
            
word2vec it is a log linear softmax calculation. w is the bias.c is a label vector of the init vector. 20k word then we have 20k dimension for the input
Very difficuly to train and predict the labels. 

It happens in a very large dimension. It can be called as the skip gram variant of the the word2vec. It is similar to the factoization method. 

We are taking all the dot products and pushing all in a particular direction. 

In partical terms: 

skip gram wih noise contrastive estimation. 

Retro fitting: 


Distributional representation of the word vectors. Meaning with the linguist: more of cognitive. 

May may not be fully specified by the the 

No grounding here 


Grounding via supervision: 
Distrivutional vectors and infusing with the sentiment information. It is not well differentiated. The negative and positive. 

PMI space-> sentiment estimate with deep classifier. Shifted the response woth the the deep classifier. 

Retrofitting: 

We need the word vectors to be similar to the original vectors and also need to be similar to the words similar to the neighboring nodes. 

Take any embedding space as long as we embedd it we can: 

\alpha and beta are the different vector representation: Here we are making use of the knowledge graph representation


original retrofitting model : if we are connected to the graph word net edge relation with the antonym. Hyper name like the edge. Release the code. 

More specialized for the graphical representation. Can be applied in a new domain. 

Embedding : 
    Threshold set we need the             

Retrofitting is using congitive skill with word embedding. 

In original paper wordnet and frame net. 

Getting different representation getting the scales can help in weighted learning problem 

Newer contextual word representation: glove included in the paper. 
    
Word vectod and semantic similari ty: 
    
"""

#1. Getting the list of review files
productQA = {"ASIN":[],"Question":[],"Answer":[]}
productReview = {"ASIN":[],"Date":[],"Rating":[],"Title":[],"Detail":[]}

QA = pd.DataFrame(productQA)
Review = pd.DataFrame(productReview)

def appendExcel(file,tag):
    global QA,Review
    #print(file,tag)
    df = pd.read_excel(file,index_col=0)
    
    if tag=="QA":
        #print("QA",len(df))
        QA =  QA.append(df)
        #print(QA)
    else:
        #print("Review",len(df))
        Review =  Review.append(df)
        print(Review)


file_path = "/Users/shashanknigam/downloads/nlp_project/shopBot/webscraping/AmazonDataSet"
j = 0 
for i in os.listdir(file_path):
    if "QA" in i:
        #print(i)
        appendExcel(file_path+"/"+i,"QA")
        j+=1
    elif "prodcutReview" in i:
        #print(i)
        appendExcel(file_path+"/"+i,"Review")
        j+=1
QA.to_excel(file_path+"/QA.xlsx")
Review.to_excel(file_path+"/Review.xlsx")
        


import pandas as pd
import nltk
import pickle
"""
Creation of word dictionary: can be saved further
"""

"""
Based on the set of questions and description we need to find the key words for each of the product which defines the product. Topic modelling or latent semantic analysis can do the same
"""

file_path="/Users/shashanknigam/downloads/nlp_project/shopBot/webscraping/AmazonDataSet"



Review=Review.append(QA[QA["Title"].isnull()==False][["ASIN",'Date', 'Rating', 'Title', 'Body']])
QA= QA.drop(['Date', 'Rating', 'Title','Body'],axis=1)
QA = QA.dropna(axis=0,thresh=2)
#Basic preprocessing on the dataset.
QA.Answer =QA.Answer.str.replace('\n',' ').str.replace('…','').str.replace('  ',' ')
QA.Question = QA.Question.str.replace('\n',' ').replace('  ','')
#Converting the rating into number
Review.drop(["Detail"],inplace=True,axis=1)

Review.Rating = Review.Rating.str.split(' ').str[0]

Review.Body = Review.Body.str.replace('\n',' ').replace('…',' ').str.replace('\.\.\.','.').str.replace('"','').str.replace('``','').str.replace("''",'')

QA = pd.read_excel(file_path+"/QA.xlsx",index_col=0)
Review = pd.read_excel(file_path+"/Review.xlsx",index_col =0)
        
        
        

