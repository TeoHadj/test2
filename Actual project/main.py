import requests
from flask import Flask

app = Flask(__name__)
app.secret_key = 'put-the-fries-in-the-bag'
CLIENT_ID = ''
CLIENT_SECRET = ''
REDIRECT_URI = 'http://127.0.0.1:8000/callback'