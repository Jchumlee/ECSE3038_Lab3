from flask import Flask, request, jsonify, json
from flask_restful import Api, Resource
from datetime import datetime 
from flask_cors import CORS
from flask_pymongo import PyMongo
from marshmallow import Schema, fields, ValidationError
from bson.json_util import dumps
from json import loads



app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb+srv://lab3:hoplki@cluster0.y2vbf.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
mongo = PyMongo(app)

class TankSchema(Schema):
    location = fields.String(required=True)
    lat = fields.Float(required=True)
    long = fields.Float(required=True)
    percentage_full = fields.Integer(required=True)


CORS(app) 
api = Api(app)

@app.route("/")
def welcome():   
    return "Welcome!"

profile = {
    "success": True,
    "data": {
        "last_updated": "14/2/2022, 8:48:51 PM", 
        "username": "Joshua C",
        "role": "Engineer",
        "color": "#3478ff"
    }
}

tank_info = []
tank_id = 0

class Profile(Resource):
    def get(self):
        return profile

    def post(self):
        profile["data"]["last_updated"] = datetime.now().strftime("%c")
        profile["data"]["username"] = request.json['username']
        profile["data"]["role"] = request.json['role']
        profile["data"]["color"] = request.json['color']
        return profile

    def patch(self):
        profile["data"]["last_updated"] = datetime.now().strftime("%c")

        data = (request.json)
        for key in data:
            profile["data"][key] = request.json[key]
        
        return profile

class Data(Resource):
    def get(self):
        tanks = mongo.db.tanks.find()
        return jsonify(loads(dumps(tanks)))


    def post(self):
        try: 
            newTank = TankSchema().load(request.json)
            tank_id = mongo.db.tanks.insert_one(newTank).inserted_id
            tank = mongo.db.tanks.find_one(tank_id)
            return loads(dumps(tank))
        except ValidationError as ve:
            return ve.messages, 400
        


class Data2(Resource):
    def patch(self, id):
        mongo.db.tanks.update_one({"_id":id}, {"$set": request.json})
        tank = mongo.db.tanks.find_one(id)
        return loads(dumps(tank))


    def delete(self, id):
        check = mongo.db.tanks.delete_one({"_id":id})

        if check.deleted_count == 1:
            return {
                "success": True
            }
        else:
            return {
                "success": False
            }, 400


api.add_resource(Profile, "/profile")
api.add_resource(Data, "/data")
api.add_resource(Data2, "/data/<ObjectId:id>")

if __name__ == "__main__":
    app.run(
        debug=True,
        port = 3000,
        host = "0.0.0.0"
    )