
from flask import Flask,json,jsonify,request,make_response
import requests,time 
from datetime import datetime,timedelta
from telethon import TelegramClient, events, sync
from telethon.tl.functions.channels import CreateChannelRequest, CheckUsernameRequest, UpdateUsernameRequest, InviteToChannelRequest
from telethon.tl.types import InputChannel, InputPeerChannel
from telethon.tl.functions.messages import AddChatUserRequest
from pymongo import MongoClient


api_id = "17194513"
api_hash = "49eeefc89ac80fbc969e55438de3e715"


app = Flask(__name__)


mongoClient = MongoClient(host="localhost", port=27017)
db = mongoClient["teletask"]
actions_collection = db["actions"]

