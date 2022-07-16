from pymongo import MongoClient

api_id = "8165510"
api_hash = "bc8ac39ed06bcbf5e7e3104cdd2998b9"
session_name = 'telethon-session'

HOST = 'localhost'
PORT = 27017

mongoClient = MongoClient(host=HOST, port=PORT)
db = mongoClient["teletask"]
actions_collection = db["actions"]
