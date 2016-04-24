#! /usr/bin/python
import urllib2
import re

_queueFile = "data/queue_file.txt"
_answerFile = "data/answer_file.txt"

_links_re = re.compile('<a href="(.*)">Attractions in.+</a>')
_links_relevant_re = re.compile('<div style="margin-bottom: 10px;"><a href=".*">(.*)</a>')

def get_text(docurl):
    try:
        content = urllib2.urlopen("http://www.tripadvisor.com/" + docurl).read()
        return content
    except:
        print "Page not found for docname: " + docurl
        return ""

def get_links(text):
    return [url for (url) in _links_re.findall(text)]

def get_relevant_links(text):
    return [url for (url) in _links_relevant_re.findall(text)]

def saveState():
    fd_queue = file(_queueFile, "w")
    for i in docqueue:
        if i:
            print >> fd_queue, i

    fd_answer = file(_answerFile, "w")
    for i in answer:
        if i:
            print >> fd_answer, i

def loadState():
    fd_queue = file(_queueFile)
    for i in fd_queue:
        if i:
            docqueue.add(i)

    fd_answer = file(_answerFile)
    for i in fd_answer:
        if i:
            answer.add(i)

docqueue = set()

answer = set()

loadState()

print "Docqueue size ", len(docqueue)
print "Answer size ", len(answer)

cnt = 1
while(len(docqueue)!=0):
    print cnt
    docurl = docqueue.pop()

    text = get_text(docurl)
    internal_links = get_links(text)
    print "Internal links ", internal_links
    if len(internal_links) == 0:
        relevant_links = get_relevant_links(text)
        print "Relevant links ",  relevant_links
        answer.update(get_relevant_links(text))
    else:
        docqueue.update(internal_links)

    if cnt%100 == 0:
        print "Saving state."
        saveState()
    cnt += 1
