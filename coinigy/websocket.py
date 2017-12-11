import os
import json
import logging
from socketclusterclient import Socketcluster


logger = logging.getLogger(__name__)


api_credentials = {
    'apiKey': os.getenv('COININGY_USERNAME'),
    'apiSecret': os.getenv('COININGY_APISECRET')
}


def pull_tickers(socket):
    channel_code = 'TRADE-BTRX--BCC--USD'
    socket.subscribe(channel_code)

    def channelmessage(key, data):                
        print ("\n\n\nGot data "+json.dumps(data, sort_keys=True)+" from channel "+key)

    socket.onchannel(channel_code, channelmessage)
    
    def ack(eventname, error, data):
        print ("\n\n\nGot ack data and eventname is " + eventname)    
    
    socket.emitack("exchanges",None, ack)  
    socket.emitack("channels", "OK", ack)  


def onconnect(socket):
    logging.info("on connect got called")

def ondisconnect(socket):
    logging.info("on disconnect got called")

def onConnectError(socket, error):
    logging.info("On connect error got called")

def onSetAuthentication(socket, token):
    logging.info("Token received " + token)
    socket.setAuthtoken(token)

def onAuthentication(socket, isauthenticated):
    logging.info("Authenticated is " + str(isauthenticated))
    def ack(eventname, error, data):
        print ("token is "+ json.dumps(data, sort_keys=True))
        pull_tickers(socket);

    socket.emitack("auth", api_credentials, ack)


def listen():
    socket = Socketcluster.socket("wss://sc-02.coinigy.com/socketcluster/")
    socket.setBasicListener(onconnect, ondisconnect, onConnectError)
    socket.setAuthenticationListener(onSetAuthentication, onAuthentication)
    socket.setreconnection(False)
    socket.connect()
