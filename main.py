import argparse
from flask import Flask, render_template, request, url_for, flash, redirect, Response
from pygtail import Pygtail
from flaskwebgui import FlaskUI # import FlaskUI
from werkzeug.exceptions import abort
import sqlite3
import logging
import datetime
import getpass
import os
import json
import requests
import pypresence
import base64
from typing import List, Union
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import sys, io
from rpc import RPC

sys.stdout = io.StringIO()
sys.stderr = io.StringIO()

## Version ##

version = "0.0.1"

##

from encrypt_data import generate_keypair, load_private_key, detect_private_key, \
    save_private_key, encrypt_message_symmetrical, decrypt_message, generate_sym_key, load_sym_key, \
        detect_sym_key, detect_public_key, save_public_key, load_public_key
import os
import sys
import time
import pyfiglet
from client_functions import add_user_friends, check_token, get_all_users, get_sym_key, get_thoughts_for_user, login, log_out, log_in_to_server, get_account_info, remove_user_friends, reset_password, register_user, upload_keystore, get_user_friends
import sentry_sdk
from flask import Flask
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="https://c368c5790a4143f6b79bf6f6f06762c9@o4504878133018624.ingest.sentry.io/4504878148157440",
    integrations=[
        FlaskIntegration(),
    ],

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0
)

app = Flask(__name__)



argParser = argparse.ArgumentParser()
argParser.add_argument("-s", "--server", help="Dev or live server", type=str, default="live")
argParser.add_argument("-d", "--debug", help="Activate Debug mode", type=str, default="False")
args = argParser.parse_args()
if args.server == "dev":
    server_url = "https://74c6-213-219-142-51.eu.ngrok.io/"
else:
    server_url = "https://peerbrain.teckhawk.be/"  




@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'),404

@app.errorhandler(405)
def not_found_error(error):
    return render_template('405.html'),405

@app.route('/login/')
def login():
    if check_token(server_url):
        username, email = get_account_info(server_url)
        return redirect("/user/", code=302)
    else:
        return render_template('index.html')

@app.route('/')
def index():
    url = 'https://public.pixelsltd.dev/projects/peer-brain/version/'
    response = requests.get(url)
    if response.status_code == 200:
            data = response.json()
            if data['version'] != version:
                return render_template('update.html', version=data['version'], changelog=data['changelog'], download=data['Download'])
            else:
                if check_token(server_url):
                    username, email = get_account_info(server_url)
                    return redirect("/user/", code=302)
                else:
                    return render_template('index.html')
    
    
@app.route('/account/')
def account():
    if check_token(server_url):
        username, email = get_account_info(server_url)
        return render_template('account.html', user_account=username, user_account_email=email)
    else:
        return redirect("/", code=302)  

@app.route('/friends/')
def friends():
    if check_token(server_url):
        friends = get_user_friends(server_url)
        print(friends)
        return render_template('friend.html', friends=friends)
    else:
        return redirect("/", code=302)

@app.route('/password-confirm/<friend>')
def password_confirm(friend):
    if check_token(server_url):
        return render_template('enterpass.html', user=friend)
    else:
        return redirect("/", code=302)

@app.route('/profile/<friend>')
def show_profile(friend):
        password = request.args.get('password')
        base_64_encr_sym_key = get_sym_key(server_url, password, friend)
        encrypted_sym_key = base64.b64decode(base_64_encr_sym_key)
        for thought in get_thoughts_for_user(server_url, friend):
            print("-------------------------------------------------------")
            print(f"TITLE:  {thought['title']}")
            print()
            print(f"RATING:  { thought['rating']}")
            print()
            try:
                decrypted_message = decrypt_message(thought["content"].encode("utf-8"), encrypted_sym_key)
                if decrypted_message == "":
                    decrypted_message = "No message found"
                print(f"MESSAGE:  { decrypted_message}")
                output = (f"TITLE:  {thought['title']}", f"RATING:  { thought['rating']}", f"MESSAGE:  { decrypted_message}")
            except FileNotFoundError as err:
                print("Error decrypting message, you may need to generate your keys still!\nError:", err)
                no_thoughts = ('No thoughts found', '')
                return render_template('profile.html', Friend=friend , thoughts=no_thoughts)
            except ValueError as err:
                print("Please restart the programme to register your keys!\nError:", err)
                no_thoughts = ('No thoughts found', '')
                return render_template('profile.html', Friend=friend , thoughts=no_thoughts)
            break
        return render_template('profile.html', Friend=friend , thoughts=output)

@app.route('/unfriend/<friend>')
def unfriend(friend):
    if check_token(server_url):
        remove_user_friends(server_url, friend)
        unfriend = ('You are no longer friends with', friend)
        friends = get_user_friends(server_url)
        print(friends)
        return render_template('friend.html', friends=friends, unfriend=unfriend)
    else:
        return redirect("/", code=302)

@app.route('/addfriend/')
def addfriend():
    if check_token(server_url):
        return render_template('addfriend.html')
    else:
        return redirect("/", code=302)
    
@app.route('/addfriends/', methods=['POST'])
def addfriends():
    if request.method == 'POST':
        friend = request.form['friend']
        add_user_friends(server_url, friend)
        friends = get_user_friends(server_url)
        friendg = 'You are now friends with', friend
        print(friendg)
        return render_template('friend.html', addfriend=friendg, friends=friends)

@app.route('/resetpassword/')
def resetpassword():
    return render_template('reset.html')

@app.route('/password-reset/')
def password():
    return render_template('sent-reset.html')

@app.route('/user/')
def user():
    if check_token(server_url):
        username, email = get_account_info(server_url)
        return render_template('user.html', user_account=username, user_account_email=email)
    else:
        return redirect("/", code=302)

@app.route('/technical-menu/')
def technical():
    if check_token(server_url):
        username, email = get_account_info(server_url)
        return render_template('technical.html', Warning="Warning: This is a technical menu, only use if you know what you are doing!")
    else:
        return redirect("/", code=302)
    
app.route('/genkey/')
def genkey():
    if check_token(server_url):
        public_key, private_key = generate_keypair()
        save_private_key(private_key)
        save_public_key(public_key)
        symmetric_key = generate_sym_key()
        upload_result = upload_keystore(server_url, public_key, symmetric_key)
        print("------------------------")
        print(upload_result)
        print("------------------------")
        return render_template('technical.html', Warning="New keys generated!")
    else:
        return redirect("/", code=302)    

@app.route('/register/')
def register():
    return render_template('register.html')


@app.route('/registeruser/', methods=['POST'])
def reguser():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        register_user(server_url, username, email, password)
        return render_template('loading-loginreg.html')
        

@app.route('/login/', methods=['POST'])
def create():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        log_in_to_server(username, password, server_url)
        return render_template('loading-loginreg.html')
        


@app.route('/reset/', methods=['POST'])
def reset():
    if request.method == 'POST':
        username = request.form['username']
        reset_password(server_url, username)
        return redirect("/password-reset/", code=302)

@app.route('/logout/')
def logout():
    log_out()
    return redirect("/", code=302)


@app.errorhandler(500)
def internal_server_error(e):
    # note that we set the 500 status explicitly
    return render_template('500.html', event_id=sentry_sdk.last_event_id()), 500
 

if __name__ == "__main__":
  # If you are debugging you can do that in the browser:
  # app.run()
  # If you want to view the flaskwebgui window:

# If the request was successful, parse the JSON data

  FlaskUI(app=app, server="flask", width=800, height=600).run()