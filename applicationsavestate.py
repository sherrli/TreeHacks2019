from flask import Flask, redirect, render_template, request, url_for, jsonify
import os
from flask_simple_geoip import SimpleGeoIP
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from helpers import lookup
# from tweetsearch import get_tweets
import io
# Imports the Google Cloud client library
from google.cloud import vision
from google.cloud.vision import types
import base64
import urllib.request
import requests
import shutil


app = Flask(__name__)

simple_geoip = SimpleGeoIP(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/smalltrails")
def smalltrails():
    return render_template("smalltrails.html")

@app.route("/diseases")
def diseases():
    return render_template("diseases.html")
    
    
@app.route("/twilio", methods=['GET', 'POST'])
def twilio():

    # body = request.values.get('Body', None)

    # # Start our TwiML response
    # resp = MessagingResponse()

    # # Determine the right reply for this message
    # if body == 'hello':
    #     resp.message("Hi!")
    # elif body == 'bye':
    #     resp.message("Goodbye")
    # else:
    #     locations = get_tweets(body, count = 100)
    #     loc_string = str(locations)
    #     greeting = f"the most recent tweets for '{body}' are from: "
    #     message = greeting + loc_string
    #     resp.message(message)
        
    # return str(resp)    

    mediaurl = request.values.get('MediaUrl0', None)
    
    r = requests.get(mediaurl, stream=True, headers={'User-agent': 'Mozilla/5.0'})
    if r.status_code == 200:
        with open("img.jpeg", 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)
    
    
    # Instantiates a client
    client = vision.ImageAnnotatorClient()
    
    # The name of the image file to annotate
    file_name = os.path.join(
        os.path.dirname(__file__),
        'img.jpeg')
    
    # Loads the image into memory
    with io.open(file_name, 'rb') as image_file:
        content = image_file.read()
    
    image = types.Image(content=content)
    
    
    response = client.text_detection(image=image)
    texts = response.text_annotations
    print('Texts:')

    for text in texts:
        print('\n"{}"'.format(text.description))

    
    image = vision.types.Image(content=content)

    response = client.logo_detection(image=image)
    logos = response.logo_annotations
    print('Logos:')

    for logo in logos:
        print(logo.description)
    
    
    response = client.label_detection(image=image)
    labels = response.label_annotations
    
    label_list = []
    print('Labels:')
    for label in labels:
        print(label.description)
        label_list.append(label.description)
        
    # Start our TwiML response
    resp = MessagingResponse()

    # Determine the right reply for this message
    labelstring = str(label_list)
    greeting = "This looks like: "
    # message = greeting + labelstring
    message = greeting
    for label in labels:
        message = message + label.description + ", "

    resp.message(message)
        
    return str(resp)    
    
    
@app.route("/userlocation")
def userlocation():
    geoip_data = simple_geoip.get_geoip_data()
    latitute = geoip_data["location"]["lat"]
    longitude = geoip_data["location"]["lng"]
    city = geoip_data["location"]["city"]


    if not os.environ.get("TWILIO_AUTH_TOKEN"):
        raise RuntimeError("AUTH_TOKEN not set")
    auth_token=os.environ.get("TWILIO_AUTH_TOKEN")
    
    if not os.environ.get("TWILIO_ACCOUNT_SID"):
        raise RuntimeError("ACCOUNT_SID not set")
    account_sid=os.environ.get("TWILIO_ACCOUNT_SID")
    
    if not os.environ.get("twilio_from"):
        raise RuntimeError("from number not set")
    twilio_from=os.environ.get("twilio_from")
    
    if not os.environ.get("TWILIO_ACCOUNT_SID"):
        raise RuntimeError("to number not set")
    to_num=os.environ.get("to_num")

    client = Client(account_sid, auth_token)
    
    # temp = "test"
    # tempstring = f"This is the ship that made the Kessel {temp} Run in fourteen parsecs?"
    
    message = client.messages \
        .create(
             body=f"You are at {city}",
            #  body=tempstring,
             from_=twilio_from,
             to=to_num
         )
    
    print(message.sid)
    
    
    return render_template("userlocation.html", lat=latitute, lon=longitude)
    
    
@app.route("/news")
def news():
    """Look up articles for geo."""

    # ensure parameters are present
    # geo = request.args.get("geo")
    geo = '95060'
    if not geo:
        raise RuntimeError("missing geo")

    # lookup articles and store them as JSON array
    article_list = lookup(geo)

    # TODO
    print(article_list)
    news = jsonify(article_list)    
    print(news)
    # return render_template("index.html")
    return article_list

    
@app.route('/shutdown')
def shutdown():
    shutdown_server()
    return 'Server shutting down...'


if __name__ == "__main__":

    app.secret_key = 'LOL MONEY'
    app.run(
        debug=True,
        host='0.0.0.0',
        port=8081
    )
    
