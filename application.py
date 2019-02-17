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
from word2number import w2n
import time, threading
import csv


app = Flask(__name__)

simple_geoip = SimpleGeoIP(app)

with open('droogs.csv', 'r') as f:
    reader = csv.reader(f)
    drug_list_list = list(reader)
    
drug_list = [item for sublist in drug_list_list for item in sublist]


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


    text_list = []

    for text in texts:
        # print('\n"{}"'.format(text.description))
        text_list.append(text.description)
    # text_list.pop(0)
    print(text_list)
    
    temp = listparser(text_list)
    seconds = checkpoint(text_list)
    # refillnum = refill_check(text_list)
    
    # print(refillnum)
    # if refillnum == "unknown":
    #     refillnum = 1
    pills = 5
    drug = drugmatcher(text_list)
    print(f"drug is: {drug}")
    # for i in range(refillnum):
    for i in range(pills):
        sender(f"Take your {drug}!")
        time.sleep(seconds)
        # sender("Refill your presciption")
        
    
   

    
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
        # print(label.description)
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
    message = message[:-2]


    
    # https://www.amazon.com/s?k=redbull+yellow&ref=nb_sb_noss_2
    
    amazonstring = ""
    for label in labels[0:2]:
        amazonstring = amazonstring + label.description + "+"
    amazonstring = amazonstring[:-1]
    amazonstring = amazonstring.replace(" ", "")
    
    strpart1 = "https://www.amazon.com/s?k="
    strpart2 = "&ref=nb_sb_noss_2"
    amazonurl = strpart1 + amazonstring + strpart2
    print(f"amazonurl: {amazonurl}")

    
    
    purchasemessage = f"{message}. Buy it here! {amazonurl}"
    
    
    
    
    




########## This comments out amazon purchase link ############
    # resp.message(purchasemessage)

        
    # return str(resp)  
    
    return(1)
    
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
    
    if not os.environ.get("to_num"):
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
    


def listparser(textlist):
    
    days = 0
    weeks = 0
    hours = 0
    freq = 0
    pillnum = 0

    for i in range(len(textlist)):
        
        if textlist[i].lower() == "every":
            if textlist[i+1].lower() =="day":
                days = 1
                freq = 1
            elif textlist[i+1].lower() =="week":
                weeks = 1
                freq = 1
            else:
                if textlist[i+2].lower() == "day" or textlist[i+2].lower() == "days":
                    days = 1
                    freq = textlist[i+1]
                if textlist[i+2].lower() == "week" or textlist[i+2].lower() == "weeks":
                    weeks = 1
                    freq = textlist[i+1]
                if textlist[i+2].lower() == "hour" or textlist[i+2].lower() == "hours":
                    hours = 1
                    freq = textlist[i+1]
                    
        if textlist[i].lower() == "take":
            pillnum = textlist[i+1]
    
    
    
    
    
    print("\n\n\n")
    print(f"pill number is: {pillnum}")
    print(f"days?: {days}")
    print(f"weeks?: {weeks}")
    print(f"hours?: {hours}")
    print(f"freq is {freq}")
    print("\n\n\n")

    
    
    
    return(1)
    
# def checkpoint(label):
#   for i in range(len(label)-1):
#   #for i in (label):
#       #if next is days get the w-number conver it to real number
#       if label[i+1] == 'days':
#           w_number = w2n.word_to_num(label[i])
#           print(w_number)
#           return w_number
#       #return False
       
def checkpoint(label):
   for i in range(len(label)-1):

       #if next is days get the w-number conver it to real number
       if label[i+1].lower() == 'days':
           i_days = w2n.word_to_num(label[i])
           return i_days
       if label[i+1].lower() == 'hours':
           i_hours = w2n.word_to_num(label[i])
           return i_hours
       if label[i].lower() == 'day':
           day = 1;
           return day;
       if label[i+1].lower() == 'day' and label[i].lower() == 'other':
           skip_day = 9999999999999999; ############# !!!!!!!!!!!!!!!!
           return skip_day;
           
def refill_check(label):
   for i in range(len(label)-1):
       #refills
       if label[i].lower() == 'no refill' or label[i].lower() == 'no refills' or label[i].lower() == 'no ref':
           refill = 0;
           return refill;
       if label[i].lower() == 'refill' or label[i].lower() == 'refills' or label[i].lower() == 'ref' or label[i].lower() == 'refil' :
           try:
               refill = w2n.word_to_num(label[i+1])
           except:
               refill = "unknown";
           return refill;
       
       
def sender(message):
    if not os.environ.get("TWILIO_AUTH_TOKEN"):
        raise RuntimeError("AUTH_TOKEN not set")
    auth_token=os.environ.get("TWILIO_AUTH_TOKEN")
    
    if not os.environ.get("TWILIO_ACCOUNT_SID"):
        raise RuntimeError("ACCOUNT_SID not set")
    account_sid=os.environ.get("TWILIO_ACCOUNT_SID")
    
    if not os.environ.get("twilio_from"):
        raise RuntimeError("from number not set")
    twilio_from=os.environ.get("twilio_from")
    
    if not os.environ.get("to_num"):
        raise RuntimeError("to number not set")
    to_num=os.environ.get("to_num")

    client = Client(account_sid, auth_token)
 
    message = client.messages \
        .create(
             body=message,
             from_=twilio_from,
             to=to_num
         )
    
    print(message.sid)

# pill = 0
# def pillspam():
#     # pillcount = pillcount + 1
#     # if pillcount == :
#     #     return(1)
#     sender("take your meds")   
#     threading.Timer(5, pillspam).start()
    
    
    
def drugmatcher(label):
    drugmatch = "meds"
    for word in label:
        if word.upper() in drug_list:
            drugmatch = word.title()
            break
    return(drugmatch)
            