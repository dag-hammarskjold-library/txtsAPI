from flask import Flask, render_template, request, abort, jsonify, Response, url_for
from requests import get
from bson.objectid import ObjectId
from app.config import Config
import boto3, re, time, os, pymongo
from pymongo import MongoClient
from dlx import DB, Bib, Auth

# Initialize your application.
app = Flask(__name__)
#collection = Config.DB.txts
DB.connect(Config.connect_string)
db_client=MongoClient(Config.connect_string)
db=db_client['undlFiles']
txts_coll = db['txts']

return_data=""
# And start building your routes.
@app.route('/')
def index():
    return(render_template('index.html', data=return_data))
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def show_text(path):
    data=""
    return_data=""
    #return 'The text with document symbol: %s was not found' % path
    #return_data=path
    #return(render_template('ds.html', data=path))
    #return 'You want path: %s' % path
    #1. connect to mongo DB and issue a query 
    
 
    for doc in txts_coll.find({"doc_sym":path}):
        return_data=doc['raw_txt']
        
    if return_data=="":
        return jsonify('text with document symbol:%s was not found' % path)
    #return(render_template('ds.html', data=return_data))
    return jsonify(return_data)

   


        
