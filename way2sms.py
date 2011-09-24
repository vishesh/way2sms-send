#!/usr/bin/env python

# 
# Script to send SMS via way2sms
# 
# @author Vishesh Yadav
# @license BSD License
#

#TODO: Phonebook
#TODO: Logs
#TODO: More abstract API so that can be ported to others
#TODO: Error checking and handling
#TODO: Various options on command line to work directly with configurations

import urllib
import urllib2
import cookielib
import ConfigParser
import re
import os
import sys

class SendSMS:
    def __init__(self):
        self.__loadCookie()
        self.__createUrlOpener()
    
    def __loadCookie(self):
        fcj = cookielib.MozillaCookieJar(os.path.expanduser("~/.way2sms.cookie"))
        try:
            fcj.load(ignore_discard=True)
        except:
            cookiejar = cookielib.CookieJar()
            self.__cookie_processor = urllib2.HTTPCookieProcessor(cookiejar)
        else:
            self.__cookie_processor = urllib2.HTTPCookieProcessor(fcj)
            
    def __createUrlOpener(self):
        self.__opener = urllib2.build_opener(self.__cookie_processor)

    def __findAndSetActionHash(self):
        url = "http://site1.way2sms.com/jsp/InstantSMS.jsp"
        response = self.__opener.open(url)
        
        pagetext = response.read()
        pattern = r'<input type="hidden" name="Action" id="Action" value="([\w]*)"'

        m = re.search(pattern, pagetext)
        if m is not None:
            self.__action_hash = m.group(1)
        else:
            raise Exception

    def login(self, username, password):
        url = "http://site1.way2sms.com/auth.cl"
        data = urllib.urlencode({
            'username': username,
            'password': password,
            'login': 'Login'
            })
        response = self.__opener.open(url, data);
        self.__findAndSetActionHash()

        fcj = cookielib.MozillaCookieJar(os.path.expanduser("~/.way2sms.cookie"))
        fcj.set_cookie(enumerate(self.__cookie_processor.cookiejar).next()[1])
        fcj.save(ignore_discard=True)

    def sendMessage(self, phonenum, message):
        url = "http://site1.way2sms.com/FirstServletsms"
        data = urllib.urlencode({
            'HiddenAction': 'instantsms',
            'Action': self.__action_hash,
            'chkall': 'on',
            'MobNo': phonenum,
            'textArea': message
            })
        response = self.__opener.open(url, data)

def GetAuthDetails():
    auth_config = ConfigParser.ConfigParser()
    if not auth_config.read(os.path.expanduser("~/.way2sms.auth")):
        raise Exception
    return { 'username': auth_config.get('auth', 'username'),
          'password': auth_config.get('auth', 'password') } 
        
x = SendSMS()

print "Please wait while we login to server..."
x.login(**GetAuthDetails())
print "Login complete!\n"

phonenum = raw_input("Enter phone number: ")

while True:
    try:
        message = raw_input(">>> ")
        if not message:
            break
        print len(message), "characters"
        x.sendMessage(phonenum, message)
    except EOFError:
        print "\nHappy Happy Joy Joy!"
        break


