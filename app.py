#! /usr/bin/python
from flask import Flask, request, render_template, url_for
from pymongo import MongoClient
import bson
from flask.ext.headers import headers

app = Flask(__name__)
app.secret_key = 'abc'

# mongo stuff
client = MongoClient('ds054288.mongolab.com', 54288)
client.pollr.authenticate('admin', 'pollr')

db = client.pollr
questions = db.questions
users = db.users
votes = db.votes

# dummy user
userId = '5647efffa4c06b853bb97d9a'
userId = bson.objectid.ObjectId(userId)
# print o

# root view
@app.route("/", methods=['GET', 'POST'])
def hello():
    if request.method == 'GET':
        q = [q for q in questions.find()]
        v = [v for v in votes.find({'user': userId})]
        for qq in q:
            qq['vote'] = None
            for vv in v:
                if vv['question'] == qq['_id']:
                    qq['vote'] = vv['answer']
                    break
        return render_template('main.html', data=q, count=len(q), keyword=None)
        
    if request.method == 'POST':
        kw = request.form["keyword"]
        if not kw:
            q = [q for q in questions.find()]
            v = [v for v in votes.find({'user': userId})]
            for qq in q:
                qq['vote'] = None
                for vv in v:
                    if vv['question'] == qq['_id']:
                        qq['vote'] = vv['answer']
                        break
            return render_template('main.html', data=q, count=len(q), keyword=None)
        q = [q for q in questions.find({'poll': kw})]
        v = [v for v in votes.find({'user': userId})]
        for qq in q:
            qq['vote'] = None
            for vv in v:
                if vv['question'] == qq['_id']:
                    qq['vote'] = vv['answer']
                    break
        return render_template('main.html', data=q, count=len(q), keyword=kw)


@app.route("/<string:poll_id>")
def display_poll(poll_id):
    poll_id = bson.objectid.ObjectId(poll_id)
    q = [q for q in questions.find({'_id': poll_id})]
    v = [v for v in votes.find({'user': userId, 'question' : poll_id })]
    print v[0]
    for qq in q:
        qq['vote'] = None
        for vv in v:
            if vv['question'] == qq['_id']:
                qq['vote'] = vv['answer']
                break
    return render_template('poll.html', data=q)

@app.route("/poll/<string:poll_id>", methods=["POST", "OPTIONS"])
@headers({'Access-Control-Allow-Origin':'*'})
def cast_vote(poll_id):
    for v in votes.find():
        print v
    poll_id, vote = poll_id.split("-")
    poll_id = bson.objectid.ObjectId(poll_id)
    print poll_id, vote
    result = votes.update_one({'user': userId, 'question' : poll_id}, {"$set": {'answer' : float(vote)}}, upsert=True)
    print result.matched_count
    print result.modified_count
    return "abc"

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
