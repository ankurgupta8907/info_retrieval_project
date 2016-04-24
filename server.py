#!/usr/bin/python
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
import urllib2
import urllib
import json
from urlparse import urlparse, parse_qs
import re as _re

PORT_NUMBER = 8080

#This class will handles any incoming request from
#the browser 
class myHandler(BaseHTTPRequestHandler):

  def call_api(self, endpoint, parameters):
    url = 'https://api.aylien.com/api/v1/' + endpoint
    headers = {
      "Accept":                             "application/json",
      "Content-type":                       "application/x-www-form-urlencoded",
      "X-AYLIEN-TextAPI-Application-ID":    "e1622928",
      "X-AYLIEN-TextAPI-Application-Key":   "f0906758e39df57399106ac593bb86cc"
    }
    opener = urllib2.build_opener()
    request = urllib2.Request(url, urllib.urlencode(parameters), headers)
    response = opener.open(request);
    return json.loads(response.read())  
  
  #Handler for the GET requests
  def do_GET(self):
    query_components = parse_qs(urlparse(self.path).query)
    
    if "api" not in query_components:
      self.send_response(200)
      self.send_header('Content-type','text/html')
      self.end_headers()
      self.wfile.write('Hi')
      return

    elif query_components["api"][0] == "aylien":
        _bracket_re = _re.compile("\[.*\]")

        name = query_components["name"][0]
        parameters = {
                        "url": "https://en.wikipedia.org/wiki/" + name,
                        "sentences_number": 3, 
                    }
        response = self.call_api('summarize', parameters)
    
        summ_sent = ""
        for sen in response["sentences"]:
            summ_sent += sen

        summ_sent = _bracket_re.sub("", summ_sent)

        my_response = {}
        my_response["doc"] = name
        my_response["summary"] = summ_sent

        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.send_header('Access-Control-Allow-Origin', '*');
        self.end_headers()
   
        self.wfile.write(json.dumps(my_response))
        return

    elif query_components["api"][0] == "google":
        api_key = "AIzaSyD-PsSaz_MjQSreWXE6ZIdy9WbjC7lYdRQ"
        query = query_components["name"]
        limit = int(query_components["limit"][0])
        service_url = 'https://kgsearch.googleapis.com/v1/entities:search'
        params = {
          'query': query,
          'limit': limit,
          'indent': True,
          'key': api_key,
        }
        url = service_url + '?' + urllib.urlencode(params)
        response = json.loads(urllib.urlopen(url).read())
        for element in response['itemListElement']:
            print element['result']['name'] + ' (' + str(element['resultScore']) + ')'
        
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.send_header('Access-Control-Allow-Origin', '*');
        self.end_headers()
   
        self.wfile.write(json.dumps(response))
        return
    
    print(query_components["api"])
try:
  #Create a web server and define the handler to manage the
  #incoming request
  server = HTTPServer(('', PORT_NUMBER), myHandler)
  print 'Started httpserver on port ' , PORT_NUMBER
  
  #Wait forever for incoming htto requests
  server.serve_forever()

except KeyboardInterrupt:
  print '^C received, shutting down the web server'
  server.socket.close()
