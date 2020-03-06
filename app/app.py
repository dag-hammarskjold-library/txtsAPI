from flask import Flask, render_template, request, abort, jsonify, Response, url_for
from requests import get
from requests.utils import quote
from bson.objectid import ObjectId
from app.config import Config
import boto3, re, time, os, pymongo
from pymongo import MongoClient
from dlx import DB
from dlx.marc import Bib, Auth, BibSet, QueryDocument,Condition,Or
from app.extract_from_pdf import PDFExtract
from app.load_raw_txt import Txt
from tika import parser
from urllib import request
import urllib
import requests
from bson import Regex
import json
from tika import parser
import re
# Initialize your application.
app = Flask(__name__)
#collection = Config.DB.txts
DB.connect(Config.connect_string)
db_client=MongoClient(Config.connect_string)
db=db_client['undlFiles']
txts_coll = db['txts']


return_data=""
# And start building your routes.
#@app.route('/<path:path>', defaults={'path': ''})
@app.route('/')
def index():
    return(render_template('index.html', data=return_data))

@app.route('/favicon.ico')
def favicon():
    return(render_template('index.html', data=""))
#@app.route('/', defaults={'path': ''})
@app.route('/txt/<path:path>')
def show_txt(path):
    '''displays the text of the document '''
    data=""
    return_data=""
    doc_list=[]
    #path=quote(path)
    path=re.escape(path)
    '''
 i2 = urllib.parse.quote(i.encode("utf-8"))  #need to deal with special characters in each url
        uu2 = urllib.parse.urljoin(uu, i2)         #create url
    '''
    print(f" this is compiled path -- {'^' + str(path)+'$'}")
    doc_list=list(txts_coll.find({"doc_sym":{"$regex":"^"+ str(path)+"$"}}))
    if len(doc_list)==0 and path != 'favicon.ico':
        print(f"no exact DS {str(path)} - generating one")
        bib_value=''
        #doc_list=list(txts_coll.find({"doc_sym":{"$regex":path}}))
        ''' extract text from DB'''
        #build list of tuples (striped_doc_sum, url to the pdf in s3)
        query = QueryDocument(
            Condition(
                    tag='191',
                    subfields={'a': Regex('^'+path+'$')}
                      )
                )
            #)
        print(f" the imp query is  -- {query.to_json()}")
        bibset=BibSet.from_query(query, skip=0, limit=3)
        a_res_en=[]
        if bibset.count==1:
            for bib in bibset.records:
                bib_value=bib.get_value('191','a')
                a_res_en.append((bib.get_value('191','a'), 'http://'+''.join(bib.files('EN'))))
                print (a_res_en)
                for url in a_res_en:
                    #txt_name = url.split('/')[-1]
                    #url is a tuple ; url[0] is a DS; url[1] is a s3 link to the pdf
                    txt_name = url[0] # e.g. ARES721
                    #txt_name = txt_name.split('.')[0] +'.txt'
                    #txt_name = txt_name +'.txt'
                    #txt_loc='\\txts\\'+txt_name
                    if len(url[1])>10:
                        print(f" - - the {url[0]} is {url[1]} - -")
                        pdf=PDFExtract(url[1])
                        parsed=parser.from_buffer(pdf.get_txt_from_url(url[1]))
                        print(f"0----PDFExtract----0")
                        txt=Txt(bib.get_value('191','a'))
                        print(txt.set_txt(parsed["content"]))
                        txt.title=bib.get_value('245','a')
                        #txt.title=bib.get_value('239','a')
                        ''' load text into txts'''
                        if txt.txt is not None:
                            query={"doc_sym":txt.symbol}
                            txts_coll.replace_one(query, txt.to_bson(), upsert=True)
 
    doc_list=[]   
    doc_list=list(txts_coll.find({"doc_sym":{"$regex":"^"+ str(path)+"$"}}))
    print(f" this is compiled path -- {'^' + str(path)+'$'}")
    if len(doc_list)==1:
        print(f"-- it's a hit- 1")
        if doc_list[0]['doc_sym'][0]!='S':
            return_data=doc_list[0]['raw_txt']
        else:
            #for SC docs - temporary measure
            doc_1=doc_list[0].pop('_id')
            return_data=doc_list[0]
    elif len(doc_list)>1:
        print(f"-- it's a hit- many") 
        return_data=sorted([doc['doc_sym'] for doc in doc_list],key =lambda x:int(''.join(c for c in x if c.isdigit())))
        #return_data=sorted(["<a href="+doc['doc_sym']+">" for doc in doc_list])
        #return_data=sorted([url_for('/'+doc_list[0]['raw_txt']) for doc in doc_list])
        
    if return_data=="":
        return jsonify('text with document symbol:%s was not found' % path)
    #return(render_template('ds.html', data=return_data)) 
    #print(return_data)
    return jsonify(return_data)

   
@app.route('/symbols/<path:path>')
def show_symbols(path):
    path=re.escape(path)
    data=""
    return_data=""
    query = QueryDocument(
                Condition(
                    tag='191',
                    subfields={'a': Regex('^'+path)},
                         ),
            )
    print(f" the query is  -- {query.to_json()}")
    bibset=BibSet.from_query(query, projection={'191':True}, skip=0, limit=0)
    a_res_en=[]
    for bib in bibset.records:
        bib_value=bib.get_value('191','a')
        a_res_en.append(bib.get_value('191','a'))
    return_data=sorted([quote(doc) for doc in a_res_en],key =lambda x:int(''.join(c for c in x if c.isdigit())))
    #return_data=a_res_en
    return(jsonify(return_data))

@app.route('/<path:path>')
@app.route('/txts/<path:path>')
def show_txts(path):
    return_data=""
    print(f"before escape - > {path}")
    path=re.escape(path)
    print(f"after escape - > {path}")
    data=""
    doc_list=[]   
    doc_list=list(txts_coll.find({"doc_sym":{"$regex":"^"+str('^' + path)}}))
    print(f" this is compiled path -- {str('^' + path)}")
    #print (f" doc list is {str(doc_list)}")
    if len(doc_list)>=1:
        print(f"-- it's a hit- many") 
        #return_data=sorted([doc['doc_sym'] for doc in doc_list],key =lambda x:int(''.join(c for c in x if c.isdigit())))
        #return_data=sorted(["<a href="+url_for('show_txts', path=path, _external=True)+">"+doc['doc_sym']+">" for doc in doc_list],key =lambda x:int(''.join(c for c in x if c.isdigit())))
        #return_data=sorted([url_for('show_txt', path="", _external=True)+doc['doc_sym'] for doc in doc_list],key =lambda x:int(''.join(c for c in x if c.isdigit())))
        #return_data=sorted([quote(doc['doc_sym']) for doc in doc_list],key =lambda x:int(''.join(c for c in x if c.isdigit())))
        return_data=sorted([doc['doc_sym'] for doc in doc_list],key =lambda x:int(''.join(c for c in x if c.isdigit())))
        #return_data=sorted(["<a href="+doc['doc_sym']+">" for doc in doc_list])
        #return_data=sorted([url_for('/'+doc_list[0]['raw_txt']) for doc in doc_list])
    if return_data=="":
        return jsonify('text with document symbol:%s was not found' % path)
    #return(render_template('ds.html', data=return_data)) 
    #print(return_data)
    return jsonify(return_data)


        