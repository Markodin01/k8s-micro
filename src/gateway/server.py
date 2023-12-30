import os, gridfs, pika, json
from flask import Flask, request
from flask_pymongo import PyMongo
from auth_svc import validate
from auth import access
from storage import util

from bson.objectid import ObjectId

server = Flask(__name__)

mongo_video =  PyMongo(
    server,
    uri="mongodb://host.minikube.internal:27017/videos"
    )

mongo_mp3 = PyMongo(
    server,
    uri="mongodb://host.minikube.internal:27017/mp3s"
    )

# comment out the following line to disable auth
fs_videos = gridfs.GridFS(mongo_video.db)
fs_mp3s = gridfs.GridFS(mongo_mp3.db)

connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
channel = connection.channel()

@server.route("/login", methods=["POST"])
def login():
    token, err = access.login(request)
    
    if not err:
        return token
    else:
        return err
    

@server.route("/upload", methods=["POST"])
def upload():
    access, err = validate.token(request)
    access = json.loads(access)

    if err:
        return err

    if access["admin"]:
        if len(request.files) == 0:
            return "no file uploaded", 400
        
        for _, f in request.files.items():
            err = util.upload(f, fs_videos, channel, access)

            if err:
                return err
            
        return "ok", 200
    
    else:
        return "access denied", 401
    
@server.route("/download", methods=["GET"])
def download():
    access, err = validate.token(request)

    if err:
        return err

    access = json.loads(access)
    if access["admin"]:
        fid_string = request.args.get("fid")

        if not fid_string:
            return "no fid provided", 400
        
        try:
            out = fs_mp3s.get(ObjectId(fid_string)).read()
            return send_file(out, download_name=fid_string + ".mp3")
        
        except Exception as e:
            return str(e), 500


    return "not authorized", 401




if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8080)