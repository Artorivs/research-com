# import requests
# from bs4 import BeautifulSoup as bs
# import pandas as pd
# import numpy as np
import selenium.webdriver as webdriver
import re
import time

#### CAUTION ####
#### Research.json is get manually from the website: https://research.com/scientists-rankings/<subject> ####
#### You need to add '?page=<number>' manually to test the max page number ####
import json

# Load the json file from hkul-publications/dataset/research/000_research.json
with open('./data/research/research-subjects.json', 'r') as f:
    research = json.load(f)
    f.close()

def _get_content(url, ranking, subject):
    content = []
    for i in range(ranking[subject]):
        browser = webdriver.Safari()
        
        if i == 0:
            browser.get(url+subject)
        else:
            browser.get(url+subject+'/?page='+str(i+1))
            
        content.append(browser.page_source)
        
        browser.close()
        time.sleep(0.5)
        
    return content


def _to_tsv(raw: list) -> str:
    compiler_url = re.compile(r'<a href="(?P<url>.*?)" title="Read more">')
    
    for i in range(len(raw)):
        # del content in front of <div class="col col--1 cols mx-0 py-0 px-0 center">, after <div id="rankingPagination" class="rankings-pagination flex">
        raw[i] = raw[i].split('<div class="col col--1 cols mx-0 py-0 px-0 center">')[1].split('<div id="rankingPagination" class="rankings-pagination flex">')[0]
        # del all newlines
        raw[i] = raw[i].replace('\n', '')
        # seperate rows by tags
        raw[i] = re.sub(r'(</span></span></span></div>|</div></div></div>)', '\n', raw[i])
        
        ## del all tags
        raw[i] = raw[i].replace('</div>', '\t').replace('</span>', '\t')
        # replace all <div class="col col--3 px-0"> with 
        raw[i] = re.sub(r'<div .*?">', '', raw[i])
        # del <span class="show-tablet desc">.*?</span>
        raw[i] = re.sub(r'<span class="show-tablet desc">(H-index|Citations|World|National)', '', raw[i])
        raw[i] = re.sub(r'<span .*?">', '', raw[i])
        raw[i] = re.sub(r'<img .*?">', '', raw[i])
        
        ## scholar values: make a tuple of scholar name and the link to the scholar's profile
        raw[i] = re.sub(r'<h4>', '', raw[i])
        raw[i] = re.sub(r'</a></h4>', '|', raw[i])
        # extract link from <a href="(?P<url>.*?)" title="Read more">
        raw[i] = re.sub(compiler_url, r'\g<url> ,', raw[i])
        
        ## del extra tabs
        raw[i] = re.sub(r'(\t+|\t\s|\t\s\t)', '\t', raw[i])
        raw[i] = re.sub(r'(?<=\n)\t(?=\d+)', '', raw[i])
        raw[i] = re.sub(r'(?<=\d+)\t(?=\d+\s\d+\s(https:))', '\n', raw[i])
        
        # del 'World	National	Scholar	H-index	Citations	Publications' except for the first row
        if i != 0:
            raw[i] = re.sub(r'(World)\s(National)\s(Scholar)\s(H-index)\s(Citations)\s(Publications)', '', raw[i])
            
    return raw

def _save_to_tsv(processed: list, filename: str):
    with open(filename, 'w') as f:
        for i in range(len(processed)):
            f.write(processed[i])

url = 'https://research.com/scientists-rankings/'
driverpath = '/Applications/Safari.app'

for subject in research.keys():
    content = _get_content(url, research, subject)
    processed = _to_tsv(content)
    
    # write to file
    _save_to_tsv(processed, subject+'.tsv')
    print(subject+'.tsv is saved')
    