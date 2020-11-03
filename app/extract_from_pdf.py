from tika import parser
from urllib import request
import requests
#import pandas
import pprint
import re
import dlx
from dlx import DB
from dlx.marc import Bib, Auth, Matcher, OrMatch
import pymongo
from app.config import Config
from bson.regex import Regex
import time

DB.connect(Config.connect_string)
#db_client=MongoClient(Config.connect_string)
class PDFExtract:
    def __init__(self,url):
        self.url=url

    @staticmethod
    def get_file(url):
        r=requests.get(url, verify=False)
        fileName = url.split('/')[-1]
        with open(fileName,'wb',) as f: 
            f.write(r.content)
        return fileName

    @staticmethod
    def get_txt_from_url(url):
        r=requests.get(url, verify=False)
        r.encoding='utf-8'
        return r.content
        #parsed=parser.from_buffer(r.content)
        #return parsed["content"]

    def get_metadata(self):
        parsed = parser.from_file(self.get_file(self.url))
        return parsed["metadata"]

    def get_text(self):
        parsed = parser.from_file(self.get_file(self.url))
        return parsed["content"]

    @staticmethod
    def clean_text(l):
        PERMITTED_CHARS = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_- /.()"
        return ''.join(ch for ch in l if ch in PERMITTED_CHARS)
        
    @staticmethod
    def is_clean_text(l):
        PERMITTED_CHARS = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_- /.()"
        if ''.join(ch for ch in l if ch in PERMITTED_CHARS) not in l:
            return False  
    '''        
    def get_words_list(self):
        try:
            return [self.clean_text(l) for l in parser.from_file(self.get_file(self.url))["content"].splitlines() if l]
        except:
            print(f" the problem with splitlines with {self.get_file(self.url)}")
    '''
    def get_words_dict(self):
        dictW={}
        for line in self.get_words_list():
            for word in line.split(' '):
                if word in dictW.keys():
                    dictW[word.lower()]=int(dictW[word])+1
                else:
                    dictW[word.lower()]=1
        return dictW

    def get_words_set(self):
        set1=set()
        for line in self.get_words_list():
            for word in line.split(' '):
                set1.add(word.lower())
        return set1


    def diff_words(self,set1):
        return self.get_words_set()-set1

class Txt:
    def __init__(self,symbol,txt):
        self.symbol=symbol
        self.txt=txt

    def to_bson(self):
        return {

	            "doc_sym":self.symbol,
	            "raw_txt":self.txt 
            }

'''

start_time=time.time()

bibs = Bib.match(
                    Matcher('191',('r',Regex('^A5[23]'))),
                    Matcher('191',('a',Regex('^A/RES')))
                )
'''
'''
bibs = Bib.match(
                    Matcher('269',('a',Regex('^20[1][9]'))),
                    Matcher('191',('a',Regex('^S/RES')))
                )
'''
'''
a_res_en=[]


#build list of tuples (striped_doc_sum, url to the pdf in s3)
for bib in bibs:
    a_res_en.append((bib.get_value('191','a').replace('/',""), 'http://'+''.join(bib.files('EN'))))
    
    

for url in a_res_en:
    #txt_name = url.split('/')[-1]
    #url is a tuple ; url[0] is a DS; url[1] is a s3 link to the pdf
    txt_name = url[0]
    #txt_name = txt_name.split('.')[0] +'.txt'
    txt_name = txt_name +'.txt'
    #txt_loc='\\txts\\'+txt_name
    if len(url[1])>10:
        print(f"the {txt_name} is {url[1]}")
        pdf=PDFextract(url[1])
        #txt_l=Txt(url[0], pdf.get_text())
        #print (txt_l.to_bson())
        with open(txt_name,'w', encoding="utf-8") as f: 
            #pass
            try:
                #print(f"the doc is {txt_name}")
                f.write(pdf.get_text())
            except:
                print(f"--- {txt_name} could not be generated ---")
#try!!!!
    #print (pdf.get_words_dict())
    #print ("set count "+ len(pdf.get_words_set()))
    try:
        print(len(pdf.get_words_list()))
    except:
        print(f"problem with splitlines")
print("--- %s seconds for extract run---" % (time.time() - start_time))

'''