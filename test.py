import requests
import datetime
import pickle
import os
import sys
from bs4 import BeautifulSoup
from email.message import EmailMessage
import time
import smtplib
from urllib import parse

def getCookie():
    # login
    url = "http://www.molliestones.com/WeeklyAd/Store/2/"
    response = requests.post(url, data = {})
    if (response.status_code == 200):
        cookie=response.cookies['S_2579_CORE']
        return cookie
    else:
        print("error logging in")
        print(str(datetime.datetime.now()))
        sys.exit()


def getNewResults():
    # url that lists all blems
    url = "http://www.molliestones.com/Weeklyad/brands/Tab"
    # set the headers like we are a browser,
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    jar = requests.cookies.RequestsCookieJar()
    jar.set('S_2579_CORE', getCookie(), domain='', path='')

    # download all the blems
    response = requests.get(url, headers=headers, cookies=jar, allow_redirects=False)
    if response.status_code != 200:
        print("error making request")
        print(str(datetime.datetime.now()))
        sys.exit()

    # parse the downloaded data and pull out just the names
    # this will stop working if the site structure changes
    soup = BeautifulSoup(response.text, "lxml")
   # return soup.get_text().find('Dazs') > 0
    return soup.get_text().find('Alexander') > 0

def sendEmail():
    print("Sending email")

    msg = EmailMessage()
    msg.set_content("\n".join(setdiff))

    email = str(os.environ.get('EMAIL'))
    pword = str(os.environ.get('PWORD'))
    msg['Subject'] = 'its on sale'
    msg['From'] = email
    msg['To'] = ['johnwilde@gmail.com']

    # setup the email server,
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    # add my account login name and password,
    server.login(email, pword)

    # Send the message via our own SMTP server.
    server.send_message(msg)
    server.quit()
    return


if __name__ == "__main__":
    # uncomment to debug
    #import pdb; pdb.set_trace()
    onSale = getNewResults()

    # send an email if there are any new items
    if onSale:
        sendEmail()

    # print time so we know script is running
    print("success:", str(datetime.datetime.now()))
