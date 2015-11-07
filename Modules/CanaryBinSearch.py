#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Non-API-Based
import requests
import configparser
from BeautifulSoup import BeautifulSoup
from Helpers import Parser
from Helpers import helpers

# Class will have the following properties:
# 1) name / description
# 2) main name called "ClassName"
# 3) execute function (calls everthing it neeeds)
# 4) places the findings into a queue

# This method will do the following:
# 1) Get raw HTML for lets say enron.com )
#    This is mainly do to the API not supporting code searched with out known repo or user
#    :(https://canary.pw/search/?q=earthlink.net&page=3)
# 2) Use beautiful soup to parse the results of the first (5) pages for <A HERF> tags that start with "/view/"
# 3) Ueses a list of URL's and places that raw HTML into a on value
# 4) Sends to parser for results

# Some considerations are the retunred results: max 100 it seems
# API may return a great array of results - This will be added later


class ClassName:

    def __init__(self, domain):
        self.name = "Searching Canary Paste Bin"
        self.description = "Search Canary for paste potential data dumps, this can take a bit but a great source"
        self.domain = domain
        config = configparser.ConfigParser()
        self.Html = ""
        try:
            config.read('Common/SimplyEmail.ini')
            self.Depth = int(config['CanaryPasteBin']['PageDepth'])
            self.Counter = int(config['CanaryPasteBin']['QueryStart'])
        except:
            print helpers.color("[*] Major Settings for Canary PasteBin Search are missing, EXITING!\n", warning=True)

    def execute(self):
        self.process()
        FinalOutput = self.get_emails()
        return FinalOutput

    def process(self):
        # Get all the Pastebin raw items
        # https://canary.pw/search/?q=earthlink.net&page=3
        UrlList = []
        while self.Counter <= self.Depth:
            try:
                url = "https://canary.pw/search/?q=" + str(self.domain) + "&page=" + \
                    str(self.Counter)
                r = requests.get(url, timeout=20)
                if r.status_code != 200:
                    break
            except Exception as e:
                error = "[!] Major issue with Canary Pastebin Search:" + str(e)
                print helpers.color(error, warning=True)
            RawHtml = r.content
            # Parse the results for our URLS)
            soup = BeautifulSoup(RawHtml)
            for a in soup.findAll('a', href=True):
                a = a['href']
                if a.startswith('/view'):
                    UrlList.append(a)
            self.Counter += 1
        # Now take all gathered URL's and gather the HTML content needed
        for Url in UrlList:
            try:
                Url = "https://canary.pw" + Url
                print Url
                # They can be massive!
                html = requests.get(Url, timeout=20)
                self.Html += html.content
            except Exception as e:
                error = "[!] Connection Timed out on Canary Pastebin Search:" + \
                    str(e)
                print helpers.color(error, warning=True)

    def get_emails(self):
        Parse = Parser.Parser(self.Html)
        Parse.genericClean()
        Parse.urlClean()
        FinalOutput = Parse.GrepFindEmails()
        return FinalOutput
