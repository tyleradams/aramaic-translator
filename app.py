#!/usr/bin/env python3

import json
import os
import random

import flask
import translator

# pylint:disable=invalid-name
app = flask.Flask(__name__)
app.debug = True

TOKEN_CHARS = "ABCDEFGHJKMNPQRSTUVWXYZ0123456789"

DICTIONARY = None
with open("dictionary.json") as f:
    DICTIONARY= json.load(f)


class ApplicationException(Exception):
    pass

class DB:
    def __init__(self, filename):
        print("DEBUG:Creating DB:{}".format(filename))
        self.filename = filename
        self.data = self._load()

    def get_data(self):
        self.data = self._load()
        return self.data

    def save(self):
        print("DEBUG:Saving DB")
        # pylint:disable=invalid-name
        with open("data.json", "w") as f:
            json.dump(self.data, f)

    def _load(self):
        print("DEBUG:Loading DB:{}".format(self.filename))
        # pylint:disable=invalid-name
        with open(self.filename) as f:
            return json.load(f)


DBI = DB("data.json")

def flask_error(error_type):
    error_dict = DBI.get_data()["errors"][error_type]
    response_code = error_dict["response_code"]
    del error_dict["response_code"]
    return flask.make_response(json.dumps(error_dict), response_code)

def get_user_by_condition(condition):
    users = [user for user in enumerate(DBI.get_data()["users"])
             if condition(user[1])]
    if users == []:
        return None, None
    elif len(users) == 1:
        return users[0]
    elif len(users) > 1:
        raise ApplicationException("More than 1 user found")
    else:
        raise ApplicationException("Invalid if tree:{}".format(
            json.dumps({"users": users})))

def get_user_by_token(token):
    return get_user_by_condition(lambda u: u["token"] == token)

def get_user_by_email(email):
    return get_user_by_condition(lambda u: u["email"] == email)

def get_user_from_form(form):
    condition = lambda u: [u["email"],u["password"]] == [form["email"], form["password"]]
    return get_user_by_condition(condition)

def scrub_user(user):
    del user["password"]
    return user

def get_unique_token():
    token = "".join(random.choices(TOKEN_CHARS, k=12))
    while token in [user["token"] for user in DBI.get_data()["users"]]:
        token = "".join(random.choices(TOKEN_CHARS, 12))
    return token

@app.errorhandler(ApplicationException)
def handle_exception(e):
    print(e)
    return flask_error("INTERNAL_ERROR")

@app.route('/test-exception')
def test_exception():
    raise ApplicationException("Message!")

@app.route('/test')
def test():
    print(json.dumps({"GIT_SHA": os.environ["GIT_SHA"]}))
    return {"key": 'value'}


@app.route('/user/sign-in', methods=['POST'])
def user_sign_in():
    attributes = flask.request.get_json()
    print("DEBUG:Submitting signin:{}".format(
        {"email": attributes["email"]}))

    user = get_user_from_form(attributes)[1]
    if user:
        return {"token": user["token"]}
    else:
        return flask_error("INVALID_USER_CREDENTIALS")

@app.route('/user', methods=['GET', 'PATCH', 'POST'])
def user_data():
    print("DEBUG:user:{}".format(json.dumps({
        "method": flask.request.method,
        "cookie": flask.request.cookies,
        "token": flask.request.cookies.get("token")
        })))
    if flask.request.method == "GET":
        token = flask.request.cookies.get("token")
        user = get_user_by_token(token)[1]
        if user:
            return json.dumps(scrub_user(user))
        else:
            return flask_error("USER_NOT_FOUND")
    elif flask.request.method == "PATCH":
        token = flask.request.cookies.get("token")
        user = get_user_by_token(token)[1]
        if not user:
            return flask_error("USER_NOT_FOUND")
        new_attributes = flask.request.get_json()
        print("DEBUG:new_attributes:{}".format(new_attributes))
        for attribute in new_attributes:
            user[attribute] = new_attributes[attribute]
        DBI.save()
        return {}
    elif flask.request.method == "POST":
        attributes = flask.request.get_json()
        if any(user for user in DBI.get_data()["users"] if user["email"] == attributes["email"]):
            return flask_error("EMAIL_IN_USE")
        if any(user for user in DBI.get_data()["users"] if user["token"] == attributes["token"]):
            return flask_error("TOKEN_IN_USE")
        user = {
            "email": attributes["email"],
            "password": attributes["password"],
            "token": attributes["token"],
        }

        DBI.get_data()["users"].append(user)
        DBI.save()
        return {}

    else:
        raise ApplicationException("ERROR:If tree exception:{}".format({"method": flask.request.method}))


@app.route('/user/update-password', methods=['POST'])
def update_password():
    token = flask.request.cookies.get("token")
    user = get_user_by_token(token)[1]
    body = flask.request.get_json()
    if user["password"] == body["oldPassword"]:
        user["password"] = body["newPassword"]
        DBI.save()
        return {}
    else:
        return flask_error("INCORRECT_OLD_PASSWORD")

@app.route("/translate", methods=["POST"])
def translate():
    body = flask.request.get_json()
    word = body["text"]
    print("DEBUG:word:{}".format(word))
    # need to reverse word as translator expects L-R hebrew but the user inputs R-L hebrew
    translations = [w.as_grammar(word) for w in translator.generate_words(DICTIONARY, word, True)]
    return {
        "word": word,
        "translations": translations,
    }

@app.route("/", methods=["GET"])
def homepage():
    return flask.redirect("/static/dashboard.html")


if __name__ == "__main__":
    app.run()
