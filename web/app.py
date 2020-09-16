from flask import Flask, jsonify, request, make_response
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt
import spacy

app = Flask(__name__)
api = Api(app)

client = MongoClient('mongodb://db:27017')
db = client.SimilarityDB

users = db['Users']


def userExists(username):
    if users.find({'Username': username}).count() != 0:
        return True
    return False


def verifyPw(username, password):
    if not userExists(username):
        return False

    hashed_pw = users.find({
        'Username': username
    })[0]['Password']

    if bcrypt.hashpw(password.encode('utf8'), hashed_pw) == hashed_pw:
        return True
    return False


def countTokens(username):
    return users.find({'Username': username})[0]['Tokens']


def createResponse(**kwargs):
    ret_json = {}
    for key, value in kwargs.items():
        ret_json[key] = value
    return ret_json


class Register(Resource):
    def post(self):
        data = request.get_json()

        username = data['username']
        password = data['password']

        if userExists(username):
            ret_json = createResponse(msg=f'user with the username: {username} already exists')
            return make_response(jsonify(ret_json), 401)

        hashed_pw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

        users.insert({
            'Username': username,
            'Password': hashed_pw,
            'Tokens': 6
        })

        ret_json = createResponse(msg='You successfully signed in')
        return make_response(jsonify(ret_json), 200)


class Detect(Resource):
    def post(self):
        data = request.get_json()

        username = data['username']
        password = data['password']
        text1 = data['text1']
        text2 = data['text2']

        if not userExists(username):
            ret_json = createResponse(msg=f'user with the username: {username} does not exist')
            return make_response(jsonify(ret_json), 401)

        correct_pw = verifyPw(username, password)

        if not correct_pw:
            ret_json = createResponse(msg='Credentials do not match')
            return make_response(jsonify(ret_json), 401)

        num_tokens = countTokens(username)
        if num_tokens <= 0:
            ret_json = createResponse(msg='Out of tokens')
            return make_response(jsonify(ret_json), 401)

        # Calculate the edit distance
        nlp = spacy.load('en_core_web_sm')

        text1 = nlp(text1)
        text2 = nlp(text2)

        '''
            Ratio is number between 0 and 1
            the closer the ratio is to 1, the similarity of two texts is stronger
        '''
        ratio = text1.similarity(text2)
        ret_json = createResponse(similarity=ratio,
                                  description='The closer the number is to 1, the stronger the similarity is',
                                  msg='Similarity score calculated successfully')
        users.update({'Username': username},
                     {'$set': {'Tokens': num_tokens - 1}})

        return make_response(jsonify(ret_json), 200)


class Refill(Resource):
    def post(self):
        data = request.get_json()

        username = data['username']
        password = data['admin_pw']
        refill_amount = data['refill']

        if not userExists(username):
            ret_json = createResponse(msg=f'user with the username: {username} does not exist')
            return make_response(jsonify(ret_json), 401)

        '''
           This part is just for the sake of testing, we hardcoded the admin pw.
           You can fix it by adding admin user to MongoDb and comparing pw with his
        '''
        admin_pw = 'test123'
        if not password == admin_pw:
            ret_json = createResponse(msg='Invalid admin password')
            return make_response(jsonify(ret_json), 401)

        current_tokens = countTokens(username)
        users.update({'Username': username}, {'$set': {'Tokens': current_tokens + refill_amount}})

        ret_json = createResponse(msg=f'{username} tokens refilled')
        return make_response(jsonify(ret_json), 200)


api.add_resource(Register, '/register')
api.add_resource(Detect, '/detect')
api.add_resource(Refill, '/refill')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
