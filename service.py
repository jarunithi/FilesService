# -*- coding: utf-8 -*-

from flask import Flask, jsonify, url_for, redirect, request
from flask_pymongo import PyMongo
from flask_restful import Api, Resource
from flask import Response 
from flask_cors import CORS, cross_origin
from bson import json_util
from bson.objectid import ObjectId
from werkzeug.routing import BaseConverter
from flask import send_file
from pymongo import MongoClient	
import gridfs
# from werkzeug.headers import headers
import io

app = Flask(__name__)
CORS(app)
# app.config['CORS_HEADERS'] = 'Content-Type'
app.config["MONGO_DBNAME"] = "filetest"
app.config['MONGO_HOST'] = 'localhost'
app.config['MONGO_PORT'] = 27020
mongo = PyMongo(app, config_prefix='MONGO')
APP_URL = "http://127.0.0.1:5000"

# def get(post_id):
#     # Convert from string to ObjectId:
#     document = client.db.collection.find_one({'_id': ObjectId(post_id)})

class RegexConverter(BaseConverter):
	def __init__(self, url_map, *items):
		super(RegexConverter, self).__init__(url_map)
		self.regex = items[0]
app.url_map.converters['regex'] = RegexConverter

class Files(Resource):
	def get(self):
		json_results = []
		for result in mongo.db.filetestonly.files.find():
			json_results.append(result)
		# return jsonify({"response": json_results})
		return Response( json_util.dumps({'response' : json_results}),mimetype='application/json')

class Delete(Resource):
	def get(self, id=None):
		if id:
			db = MongoClient().myDB
			fs = gridfs.GridFS( mongo.db, collection='filetestonly')
			fs.delete(id)
			return "File Deleted"
		else :
			return "Error ID Not Found!!"

class DeleteByDocumentId(Resource):
	def get(self, id=None):
		db = MongoClient().myDB
		fs = gridfs.GridFS( mongo.db, collection='filetestonly')
		if id:
			for result in mongo.db.filetestonly.files.find({'documentId': id}):
				fs.delete(result['_id'])
			return "Document Files Deleted"
		else :
			return "Error Document ID Not Found!!"

class DeleteAllByDocumentId(Resource):
	def get(self, id=None):
		db = MongoClient().myDB
		fs = gridfs.GridFS( mongo.db, collection='filetestonly')
		if id:
			for result in mongo.db.filetestonly.files.find({'documentId': id}):
				fs.delete(result['_id'])
			# 	mongo.db.filetestonly.chunks.delete_one({'files_id': ObjectId(result['_id'])});
			# mongo.db.filetestonly.files.delete_many({'documentId': id});
			return "Document Files Deleted"
		else :
			return "Error Document ID Not Found!!"

class DownloadById(Resource):
	def get(self, id=None):
		# print "---------------------------------"
		# print (id)
		# print (ObjectId(id))
		if id:
			db = MongoClient().myDB
			fs = gridfs.GridFS( mongo.db, collection='filetestonly')
			file = mongo.db.filetestonly.files.find_one({'_id':  ObjectId(id)})
			# print "---------------------------------"
			# fs.get(ObjectId(id)).read()
			response = Response(fs.get(ObjectId(id)).read())
			# response = Response(binary['data'])
			response.headers['Content-Disposition'] = 'attachment; filename='+file['filename']
			return response

class Upload(Resource):
	def post(self):
		print request.args
		print request.files
		if request.files['file']:
			# if request.args['documentId']:
			# 	documentId = request.args['documentId']
			# else :
			# 	print "No DocumentID"
			# 	return "Error No documentID"
			
			# mongo.save_file(request.files['file'].filename, request.files['file'])
			
			file = request.files['file']
			db = MongoClient().myDB
			fs = gridfs.GridFS( mongo.db, collection='filetestonly')
			# fileID = fs.put( file,filename=file.filename ,aliase=None, contentType=None,documentId=documentId)
			fileID = fs.put( file,filename=file.filename ,aliase=None, contentType=None,documentId='12345')
			out = fs.get(fileID)
			print out
			return "Saved"
		else :
			print "Failed"
			return "Failed"

class FileDetail(Resource):
	def get(self, documentId=None):
		if documentId :  
			result = mongo.db.filetestonly.files.find({'documentId':  documentId})
			return Response( json_util.dumps({'response' : result}),mimetype='application/json')

class AllFileDetail(Resource):
	def get(self, documentId=None):
		if documentId :  
			result = mongo.db.filetestonly.files.find({'documentId':  documentId})
			return Response( json_util.dumps({'response' : result}),mimetype='application/json')

class Chunks(Resource):
	def get(self):
		json_results = []
		for result in mongo.db.filetestonly.chunks.find():
			json_results.append(result)
		# return jsonify({"response": json_results})
		return Response( json_util.dumps({'response' : json_results}),mimetype='application/json')

class Copy(Resource):
	def get(self, fromId=None, toId=None):
		for result in mongo.db.filetestonly.files.find({'documentId':  request.args['fromId']}):
			db = MongoClient().myDB
			fs = gridfs.GridFS( mongo.db, collection='filetestonly')
			file = mongo.db.filetestonly.files.find_one({'_id':  ObjectId(result['_id'])})
			# print "---------------------------------"
			newFileD = fs.put(fs.get(ObjectId(result['_id'])),filename=result['filename'],aliase=None, contentType=None,documentId=request.args['toId'])
			print newFileID
		return "Copy Done"
		


class Test(Resource):
	def post(self):
		print "---------------------------------"
		print request
		print request.data
		print request.files['file'].filename
		print "---------------------------------"
		return "Called"

	def get(self):
		# savedfile = mongo.save_file("game.txt",open("game.txt"),base='filetestonly',documentId=ObjectId('57efdfe0d4c6272e24b7b906'))
		# db = MongoClient().myDB
		# fs = gridfs.GridFS( mongo.db, collection='filetestonly')
		# fileID = fs.put( open( r'game.txt', 'r') ,filename='game.txt' ,aliase=None, contentType=None,documentId='57efdfe0d4c6272e24b7b906')
		# out = fs.get(fileID)
		# print out.length
		# print open("game.txt").read()
		print "Get Test"
		return "Nope"

class Permission(Resource):
	def post(self,fileId,person):
		
		return True

	def get(self):
		fileId = request.args['id']
		result = mongo.db.filetestonly.document.find_one({'fileId':  fileId})
		return result


class Index(Resource):
	def get(self):
		return "Hello From The Other Side!"


api = Api(app)
api.add_resource(Index, "/", endpoint="index")
api.add_resource(Test, "/test", endpoint="test")
api.add_resource(Files, "/files", endpoint="files")
api.add_resource(Copy, "/copy", endpoint="copy")
api.add_resource(Chunks, "/chunks", endpoint="chunks")
api.add_resource(Upload, "/upload", endpoint="upload")
api.add_resource(DownloadById, "/downloadById/<regex(\"[a-zA-Z0-9]{1,30}\"):id>", endpoint="download")
api.add_resource(FileDetail, "/fileDetail/documentId/<regex(\"[a-zA-Z0-9]{1,30}\"):documentId>", endpoint="fileDetail")

if __name__ == "__main__":
	app.run(debug=True)