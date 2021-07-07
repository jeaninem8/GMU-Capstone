#!/usr/bin/env python
# coding: utf-8

# In[1]:


# DAEN 690
# Team All(wyn) In
# program to build dataframe with job price, experience, education, and job description
# attempt #2 - using csv download to form urls and scrape - will include 3 years of data

# ORIGINAL FILE 6/11/21 - Jeanine
# Recently updated 7/5


# In[1]:


# import packages
import pandas as pd
import html5lib
import bs4
import lxml.html as html
from selenium import webdriver
import requests
import re
import docx2txt


# In[2]:


# read in CALC data
calc_scrape = pd.read_csv('/Users/Jeanine/Downloads/All_CALC_NEW.csv')


# In[3]:


len(calc_scrape)


# In[ ]:


# First attempt - have descriptions for 5926/30660 rows
    # for pdfs, used string chunks around education, experience, etc. words to collect job description
    # for word, used 1000 characters around job title
    # only removed parentheses on job titles
    
# Second attempt - have descriptions for 13638/30660 rows
    # finding the job title following the one of interest on the pricing chart to determine where the string should begin and end
    # removed * and spaces at end of job titles


# In[60]:


# edit labor categories so the PDF scrape will be more efficient - deleting parentheses, asterisks, and spaces at end of job titles
j = 0
while j < len(calc_scrape["Labor Category"]):
    title = calc_scrape["Labor Category"][j]
    title1 = title.replace('*', '')
    title2 = title1.rstrip()
    if '(' in title2:
        ind = title2.index('(')
        rep = str(title2[0:ind-1])
        calc_scrape["Labor Category"][j] = rep
    j += 1


# In[10]:


# create URLS for the PDFs


# In[6]:


# get contract number without dashes to insert in URL
gsanum_list = []

for x in calc_scrape["Contract #"]:
    gsanum_list.append(x.replace('-', ''))


# In[7]:


calc_scrape["contract_num"] = gsanum_list


# In[8]:


# create PDF links
link_list = []
y = 0
while y < len(calc_scrape):
    urllink = "https://www.gsaadvantage.gov/ref_text/" + calc_scrape["contract_num"][y] + "/" + calc_scrape["contract_num"][y] + "_online.htm"
    link_list.append(urllink)
    y += 1


# In[9]:


# convert links to redirected links
len(link_list)


# In[10]:


# load packages used for link redirects
from urllib.request import build_opener, HTTPCookieProcessor
opener = build_opener(HTTPCookieProcessor())


# In[11]:


n = 0
while n < len(link_list):
    print(n)
    # get pdf url for first dataframe row
    pdf_url = link_list[n]
    # pull the actual link of PDF - the link redirects after opening, so if we don't do this step, the PDF scrape results in an error
    try:
        response = opener.open(pdf_url)
        rep_final = response.read().decode('ISO-8859-1')
    except:
        link_list[n] = ""
        n += 1
        continue
    # get end of URL that is unique from rep_final string above
    url_end = rep_final[rep_final.find('url=')+4:rep_final.find('><title')-1]
    # get the front of the URL that does not change after redirect
    url_split = pdf_url.split("/")[0:5]
    url_beg = "/".join(url_split)
    # combine to form correct URL for PDF scrape
    url_full = url_beg + "/" + url_end
    link_list[n] = url_full
    n += 1


# In[12]:


# add column with good URL
calc_scrape["PDF URL"] = link_list


# In[476]:


display(calc_scrape)


# In[ ]:


# adjust labor categories 


# In[ ]:


# scrape PDFs


# In[49]:


import pdftotext
# have to install libpoppler-cpp-dev as well to get pdftotext to install
from six.moves.urllib.request import urlopen
import docx # have to run pip install python-docx to install
import xlsxwriter
import io
from io import BytesIO
from urllib.error import HTTPError, URLError
import numpy as np


# In[43]:


# use keywords  that occur in most every description as separators
keywords = ['education', 'experience', 'years', 'duties', 'specifications']


# In[18]:


# create blank column for job descriptions and zip code to go in
calc_scrape["job_desc"] = ""
calc_scrape["zipcode"] = ""


# In[320]:


###############
## version 1 ##
###############

m = 0
#job_desc = []
while m < len(calc_scrape):
    print(m)
    # check file type
    # scrape PDF
    if calc_scrape["PDF URL"][m].lower().endswith('.pdf') == True:
        print("PDF")
        # scrape PDF
        try:
            remote_file = urlopen(calc_scrape["PDF URL"][m]).read()
        except (HTTPError, URLError):
            print("URL ERROR !!!!!!!!!!!!!!!!!!!!!!!")
            job_desc.append("")
            m += 1
            continue
        memory_file = io.BytesIO(remote_file)
        pdf = pdftotext.PDF(memory_file)
        text = ".".join(pdf)

        # search for job title
        job_title = calc_scrape["Labor Category"][m].lower() + " "
        print(job_title)
        if (job_title not in text.lower()):
            m += 1
            job_desc.append("")
            continue
        # get words in area to capture job description
        docx_text = text.lower()
        ind = docx_text.index(job_title)
        job_capture = docx_text[ind-1000:ind+1000]
        # capture job desc
        if ('$' in job_capture):
            job_capture = docx_text[ind+1000:]
            if (job_title not in job_capture):
                m += 1
                job_desc.append("")
                continue
            ind_new = job_capture.index(job_title)
            job_capture = job_capture[ind_new-1000:ind_new+1000]

    
        check = [word for word in keywords if(word in job_capture)]
        if len(check) == 0:
            m += 1
            job_desc.append("")
            continue
        # split the string on existing keyword
        page_text_split = job_capture.split(check[0])
        # get targeted string of text from split page where the job title exists
        matching = [s for s in page_text_split if job_title in s]
        job_desc.append(matching)
        m += 1
    # scrape Word doc
    elif calc_scrape["PDF URL"][m].lower().endswith('.docx') == True:
        print("Docx")
        docx = io.BytesIO(requests.get(calc_scrape["PDF URL"][m]).content)
        # extract text
        text = docx2txt.process(docx)
        # search for job title
        job_title = calc_scrape["Labor Category"][m].lower() + " "
        print(job_title)
        if (job_title not in text.lower()):
            m += 1
            job_desc.append("")
            continue
        # get words in area to capture job description
        docx_text = text.lower()
        ind = docx_text.index(job_title)
        job_capture = docx_text[ind-1000:ind+1000]
        # capture job desc
        if ('$' in job_capture):
            job_capture = docx_text[ind+1000:]
            if (job_title not in job_capture):
                m += 1
                job_desc.append("")
                continue
            ind_new = job_capture.index(job_title)
            job_capture = job_capture[ind_new-1000:ind_new+1000]

    
        check = [word for word in keywords if(word in job_capture)]
        if len(check) == 0:
            m += 1
            job_desc.append("")
            continue
        # split the string on existing keyword
        page_text_split = job_capture.split(check[0])
        # get targeted string of text from split page where the job title exists
        matching = [s for s in page_text_split if job_title in s]
        job_desc.append(matching)
        m += 1
    else:
        job_desc.append("")
        m += 1
        continue


# In[321]:


print(len(job_desc))


# In[291]:


job_desc = []
zipcode = []


# In[345]:


###############
## version 2 ##
###############

m = 0
while m < len(calc_scrape):
    print(m)
    # check file type
    # scrape PDF
    if calc_scrape["PDF URL"][m].lower().endswith('.pdf') == True:
        print("PDF")
        # scrape PDF
        try:
            remote_file = urlopen(calc_scrape["PDF URL"][m]).read()
        except (HTTPError, URLError):
            print("URL ERROR !!!!!!!!!!!!!!!!!!!!!!!")
            job_desc.append("")
            zipcode.append("")
            m += 1
            continue
        memory_file = io.BytesIO(remote_file)
        pdf = pdftotext.PDF(memory_file)
        text = ".".join(pdf)
        
        # search for zip code
        page1 = text[0:1500]
        zipsearch = re.findall(r"(?<!\d)\d{5}(?!\d)", page1)
        if len(zipsearch) > 0:
            zipcode.append(zipsearch[0])
        else: 
            zipcode.append("")

        # search for job title
        job_title = calc_scrape["Labor Category"][m].lower()
        print(job_title)
        if (job_title not in text.lower()):
            m += 1
            job_desc.append("")
            continue
        # get words in area to capture job description - looks for job title following one of interest to get string between the two titles
        docx_text = text.lower()
        docx_split = docx_text.split(job_title)
        x = 1
        a = 0
        desc = ""
        secondjob = ""
        while x < len(docx_split):
            if ('$' in docx_split[x] and a == 0):
                print(x)
                secondjob = re.findall(r"\n(.*?(?=\s{2}))", docx_split[x])
                if len(secondjob) == 0:
                    x += 1
                else:
                    secondjob = secondjob[0]
                    a = 1
                    x += 1
            elif ('$' in docx_split[x] and a == 1):
                print(x)
                x += 1
            else: 
                print(x)
                job_capture = " ".join(docx_split[x:])
                search = job_capture.find(secondjob)
                if search == -1 or len(secondjob) == 0:
                    print("1500 Characters")
                    desc = job_capture[0:1200]
                else:
                    desc = job_capture[job_capture.find(job_title)+len(job_title):job_capture.find(secondjob)]
                break
        job_desc.append(desc)
        m += 1
    # scrape Word doc
    elif calc_scrape["PDF URL"][m].lower().endswith('.docx') == True:
        print("Docx")
        docx = io.BytesIO(requests.get(calc_scrape["PDF URL"][m]).content)
        # extract text
        text = docx2txt.process(docx)
        
        # search for zip code
        page1 = text[0:1500]
        zipsearch = re.findall(r"(?<!\d)\d{5}(?!\d)", page1)
        if len(zipsearch) > 0:
            zipcode.append(zipsearch[0])
        else: 
            zipcode.append("")
        
        # search for job title
        job_title = calc_scrape["Labor Category"][m].lower() + " "
        print(job_title)
        if (job_title not in text.lower()):
            m += 1
            job_desc.append("")
            continue
        # get words in area to capture job description
        docx_text = text.lower()
        docx_split = docx_text.split(job_title)
        x = 1
        a = 0
        desc = ""
        secondjob = ""
        while x < len(docx_split):
            if ('$' in docx_split[x] and a == 0):
                print(x)
                secondjob = re.findall(r"\n(.*?(?=\s{2}))", docx_split[x])
                if len(secondjob) == 0:
                    x += 1
                else:
                    secondjob = secondjob[0]
                    a = 1
                    x += 1
            elif ('$' in docx_split[x] and a == 1):
                print(x)
                x += 1
            else: 
                print(x)
                job_capture = " ".join(docx_split[x:])
                search = job_capture.find(secondjob)
                if search == -1 or len(secondjob) == 0:
                    print("1500 Characters")
                    desc = job_capture[0:1200]
                else:
                    desc = job_capture[job_capture.find(job_title)+len(job_title):job_capture.find(secondjob)]
                break
        job_desc.append(desc)
        m += 1
    else:
        job_desc.append("")
        m += 1
        continue


# In[467]:


len(zipcode)


# In[464]:


calc_scrape["job_desc"] = job_desc
calc_scrape["zipcode"] = zipcode


# In[ ]:


# get the city and state combo for each zipcode


# In[13]:


from uszipcode import SearchEngine
import json


# In[2]:


search = SearchEngine(simple_zipcode=True)


# In[36]:


import math
calc_scrape = pd.read_csv('/Users/Jeanine/Documents/calc_scrape070421.csv')


# In[21]:


calc_scrape['city'] = ""
calc_scrape['state'] = ""


# In[22]:


display(calc_scrape)


# In[56]:


city_list = []
state_list = []


# In[57]:


z = 0
while z < len(calc_scrape):
    try:
        zip_return = search.by_zipcode(str(math.trunc(calc_scrape['zipcode'][z])))
    except ValueError:
        z += 1
        city_list.append("")
        state_list.append("")
    city_list.append(zip_return.major_city)
    state_list.append(zip_return.state)
    z += 1


# In[58]:


calc_scrape['city'] = city_list
calc_scrape['state'] = state_list


# In[59]:


calcmatch = pd.read_csv('/Users/Jeanine/Downloads/CALC_predictive_modeling.csv', sep = '|')


# In[61]:


calc_need = calc_scrape[['Unnamed: 0', 'zipcode', 'city', 'state']]


# In[65]:


calc_need = calc_need.rename(columns={"Unnamed: 0": "c_row_id"})


# In[66]:


display(calc_need)


# In[68]:


calcmatch = calcmatch.merge(calc_need, on='c_row_id', how='left')


# In[71]:


calcmatch.to_csv('/Users/Jeanine/Downloads/CALC_predictive_modeling_withlocation.csv', sep = '|')


# In[ ]:




