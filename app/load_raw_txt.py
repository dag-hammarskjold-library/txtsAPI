#from tika import parser
#from urllib import request
#import requests
#import pandas
#import pprint
#import re
import dlx
from dlx import DB
from dlx.marc import Bib, Auth, Matcher, OrMatch
import pymongo
from pymongo import MongoClient
from app.config import Config
from bson.regex import Regex


DB.connect(Config.connect_string)
db_client=MongoClient(Config.connect_string)
db=db_client['undlFiles']
txts_coll = db['txts']
txt=None

class Txt:
    def __init__(self,symbol):
        self.symbol = symbol
        self.title = None
        self.txt = None

    def to_bson(self):
        return {

	            "doc_sym":self.symbol,
	            "raw_txt":self.txt,
                "title":self.title
            }

    def get_txt_from_file(self, txt_file_name):
        try:
            with open(txt_file_name,'r', encoding="utf-8") as f: 
                return f.read()
        except:
            pass

    def set_txt(self, txt):
        self.txt=txt    
'''
bibs = Bib.match(
                    Matcher('269',('a',Regex('^20[0][0]'))),
                    Matcher('191',('a',Regex('^S/RES')))
                )
'''
'''           
bibs = Bib.match_values(

    ('191','r','A62'), 
    ('191','a',re.compile('A/RES',re.IGNORECASE)))


for bib in bibs:
    txt=Txt(bib.get_value('191','a'))
	txt.title=bib.get_value('239','a')
    if txt.txt is not None:
        query={"doc_sym":txt.symbol}
        txts_coll.replace_one(query, txt.to_bson(), upsert=True)
    print(txt.to_bson())
'''