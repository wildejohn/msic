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
import psycopg2

def getCookie():
    # login
    url = "https://ebiz.specialized.com/bb/SBCBBcpLogin.jsp"
    data = {
            'custnbr' : str(os.environ.get('CUSTOMER_NUMBER')),
            'username' : str(os.environ.get('USERNAME')),
            'password' : str(os.environ.get('PASSWORD'))
            }
    response = requests.post(url, data = data)
    if (response.history[0].status_code == 302):
        cookie=response.history[0].cookies['GOLD']
        return cookie
    else:
        print("error logging in")
        print(str(datetime.datetime.now()))
        sys.exit()

def getConnection():
    parse.uses_netloc.append("postgres")
    db_url = parse.urlparse(os.environ["DATABASE_URL"])
    conn = psycopg2.connect( database=db_url.path[1:], user=db_url.username, password=db_url.password, host=db_url.hostname, port=db_url.port)
    return conn

def getLastResults():
    conn = getConnection()
    # load last set of results from DB
    cur = conn.cursor()
    cur.execute("SELECT * FROM bikes1 order by id desc limit 1;")
    conn.commit()
    x=cur.fetchone()[1]
    conn.close()
    oldset=pickle.loads(x)
    return oldset

def getNewResults():
    # url that lists all blems
    url = "http://ibd.specialized.com/bb/SBCBBBlemsPicker.jsp"
    # set the headers like we are a browser,
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    jar = requests.cookies.RequestsCookieJar()
    jar.set('GOLD', getCookie(), domain='', path='')

    # download all the blems
    response = requests.get(url, headers=headers, cookies=jar, allow_redirects=False)
    #import pdb; pdb.set_trace()
    if response.status_code != 200:
        print("error making request")
        print(str(datetime.datetime.now()))
        sys.exit()

    # parse the downloaded data and pull out just the names
    # this will stop working if the site structure changes
    soup = BeautifulSoup(response.text, "lxml")
    bikes = soup("td","price") 
    newset=set(map((lambda x: x.text), bikes))
    return newset

def sendEmail(setdiff):
    print(str(setdiff))

    msg = EmailMessage()
    msg.set_content("\n".join(setdiff))

    email = str(os.environ.get('EMAIL'))
    pword = str(os.environ.get('PWORD'))
    msg['Subject'] = 'new stuff'
    msg['From'] = email
    msg['To'] = ['christianwparker@yahoo.com', 'johnwilde@gmail.com']

    # setup the email server,
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    # add my account login name and password,
    server.login(email, pword)

    # Send the message via our own SMTP server.
    server.send_message(msg)
    server.quit()
    return

def saveResults(newset):
    pickled=pickle.dumps(newset)
    conn = getConnection()
    cur = conn.cursor()
    cur.execute("INSERT INTO bikes1 (result) VALUES (%s)",[psycopg2.Binary(pickled)])
    conn.commit()
    cur.close()
    conn.close()
    return

if __name__ == "__main__":
    # uncomment to debug
    #import pdb; pdb.set_trace()
    oldset = getLastResults()
    print("oldset length:", len(oldset))

    newset = getNewResults()
    print("newset length:", len(newset))

    saveResults(newset)

    # find items that were not there last time we checked
    setdiff=newset-oldset

    # send an email if there are any new items
    if len(setdiff) > 0 and len(setdiff) < 100:
        sendEmail(setdiff)

    # print time so we know script is running
    print("success:", str(datetime.datetime.now()))
