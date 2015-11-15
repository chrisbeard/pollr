#! /usr/bin/python
from flask import Flask, request, render_template, url_for
from pymongo import MongoClient
import bson, json
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
# userId = '5648bbd09c5238a2004f926f'
userId = bson.objectid.ObjectId(userId)

# root view
@app.route("/", methods=['GET', 'POST'])
def hello():
    for u in users.find():
        print u
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
    for qq in q:
        qq['vote'] = None
        for vv in v:
            if vv['question'] == qq['_id']:
                qq['vote'] = vv['answer']
                break
    return render_template('poll.html', data=q)

@app.route("/stats/<string:poll_id>")
@headers({'Access-Control-Allow-Origin':'*', 'Content-Type':'application/json'})
def poll_stats(poll_id):
    #poll = question!!
    poll_id = bson.objectid.ObjectId(poll_id)
    q = [q for q in questions.find({'_id': poll_id})]
    v = [v for v in votes.find({'question' : poll_id })]
    u = [u for u in users.find({})]
    u_dict = {}
    for user in u:
        u_dict[user["_id"]] = user

    d = {}
    d["n_women_yes"] = d["n_men_yes"] = d["n_women_no"] = d["n_men_no"] = 0
    ay = {}
    an = {}
    ay["1-10"] = ay["11-20"] = ay["21-30"] = ay["31-40"] = ay["41-50"] = \
        ay["51-60"] = ay["61-70"] = ay["71-80"] = ay["81-90"] = ay["91-100"] = 0
    an["1-10"] = an["11-20"] = an["21-30"] = an["31-40"] = an["41-50"] = \
        an["51-60"] = an["61-70"] = an["71-80"] = an["81-90"] = an["91-100"] = 0
    d["age-yes"] = ay
    d["age-no"] = an
    for vote in v:
        #0=no, 1=yes
        gender = u_dict[vote["user"]]["gender"]
        if gender == 0: #boi
            if (vote["answer"] == 0):
                d["n_men_no"] += 1
            else:
                d["n_men_yes"] += 1
        elif gender == 1: #gurl
            if (vote["answer"] == 0):
                d["n_women_no"] += 1
            else:
                d["n_women_yes"] += 1

        age = int(u_dict[vote["user"]]["age"])
        if (vote["answer"] == 1):
            if age < 11:
                ay["1-10"] += 1
            elif age < 21:
                ay["11-20"] += 1
            elif age < 31:
                ay["21-30"] += 1
            elif age < 41:
                ay["31-40"] += 1
            elif age < 51:
                ay["41-50"] += 1
            elif age < 61:
                ay["51-60"] += 1
            elif age < 71:
                ay["61-70"] += 1
            elif age < 81:
                ay["71-80"] += 1
            elif age < 91:
                ay["81-90"] += 1
            else:
                ay["91-100"] += 1
        else:
            if age < 11:
                an["1-10"] += 1
            elif age < 21:
                an["11-20"] += 1
            elif age < 31:
                an["21-30"] += 1
            elif age < 41:
                an["31-40"] += 1
            elif age < 51:
                an["41-50"] += 1
            elif age < 61:
                an["51-60"] += 1
            elif age < 71:
                an["61-70"] += 1
            elif age < 81:
                an["71-80"] += 1
            elif age < 91:
                an["81-90"] += 1
            else:
                an["91-100"] += 1

    return json.dumps(d)


@app.route("/poll/<string:poll_id>", methods=["POST", "OPTIONS"])
@headers({'Access-Control-Allow-Origin':'*'})
def cast_vote(poll_id):
    poll_id, vote = poll_id.split("-")
    poll_id = bson.objectid.ObjectId(poll_id)
    result = votes.update_one({'user': userId, 'question' : poll_id}, {"$set": {'answer' : float(vote)}}, upsert=True)
    return "abc"

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
