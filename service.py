# -*- coding: utf-8 -*-

from flask import Flask, jsonify, url_for, redirect, request
from flask_pymongo import PyMongo
from flask_restful import Api, Resource
from flask import Response 
from bson import json_util
from bson.objectid import ObjectId
from werkzeug.routing import BaseConverter
from flask import send_file
from pymongo import MongoClient	
import gridfs
# from werkzeug.headers import headers
import io

app = Flask(__name__)
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
        	mongo.db.filetestonly.files.delete({'_id': ObjectId(id)});
        	mongo.db.filetestonly.chunks.delete({'files_id': ObjectId(id)});
        	return "File Deleted"
        else :
    		return "Error ID Not Found!!"

class DeleteByDocumentId(Resource):
    def get(self, id=None):
        if id:
        	for result in mongo.db.filetestonly.files.find():
        		mongo.db.filetestonly.chunks.delete_one({'files_id': ObjectId(result['_id'])});
        	mongo.db.filetestonly.files.delete_many({'documentId': id});
        	return "Document Files Deleted"
        else :
    		return "Error Document ID Not Found!!"

class DeleteAllByDocumentId(Resource):
    def get(self, id=None):
        if id:
        	for result in mongo.db.filetestonly.files.find():
        		mongo.db.filetestonly.chunks.delete_one({'files_id': ObjectId(result['_id'])});
        	mongo.db.filetestonly.files.delete_many({'documentId': id});
        	return "Document Files Deleted"
        else :
    		return "Error Document ID Not Found!!"

class DownloadById(Resource):
	def get(self, id=None):
		# print "---------------------------------"
		# print (id)
		# print (ObjectId(id))
		if id:
			file = mongo.db.filetestonly.files.find_one({'_id':  ObjectId(id)})
			binary = mongo.db.filetestonly.chunks.find_one({'files_id':  ObjectId(id)})

			# print (file['filename'])
			# print (binary['data'])
			# print "---------------------------------"
    		response = Response(binary['data'])
    		response.headers['Content-Disposition'] = 'attachment; filename='+file['filename']
    		return response

class Upload(Resource):
	def post(self, files=None, documentId=None):
		if file:
			mongo.save_file(filename, request.files['file'])
			return "Saved"
		else :
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
			print result


class Test(Resource):
	def post(self):
		print "---------------------------------"
		print request
		print request.data
		print "---------------------------------"
	def get(self):
		# savedfile = mongo.save_file("game.txt",open("game.txt"),base='filetestonly',documentId=ObjectId('57efdfe0d4c6272e24b7b906'))
		# db = MongoClient().myDB
		fs = gridfs.GridFS( mongo.db, collection='filetestonly')
		fileID = fs.put( open( r'game.txt', 'r') ,filename='game.txt' ,aliase=None, contentType=None,documentId='57efdfe0d4c6272e24b7b906')
		out = fs.get(fileID)
		print out.length

		# print open("game.txt").read()

class Permission(Resource):
    def post(self):
        
        return True
    def get(self):
        documentId = args['id']
        result = mongo.db.filetestonly.document.find_one({'documentId':  documentId})
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
api.add_resource(DownloadById, "/downloadById/<regex(\"[a-zA-Z0-9]{1,30}\"):id>", endpoint="download")
api.add_resource(FileDetail, "/fileDetail/documentId/<regex(\"[a-zA-Z0-9]{1,30}\"):documentId>", endpoint="fileDetail")
# api.add_resource(Student, "/api/<string:registration>", endpoint="registration")
# api.add_resource(Student, "/api/department/<string:department>", endpoint="department")

if __name__ == "__main__":
    app.run(debug=True)