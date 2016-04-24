#! /usr/bin/python
# -*- coding: utf-8 -*-

import os
from os import path
import sys
from time import sleep
from textextraction import textExtraction
import config
import urllib2
import urllib


class MyURLopener(urllib.URLopener):
    version="Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.19) Gecko/20081202 Firefox (Debian-2.0.0.19-0etch1)"

urlopen=urllib2.urlopen

sys.stdin.close()



langs=config.langs.split(" ")
queueFile=path.join(config.workingDir, config.queueFile)
multidocFile=path.join(config.workingDir, config.multidocFile)
multidocDir=path.join(config.workingDir, config.multidocDir)
niceness=os.nice(config.niceness)
sleepAfterDownload=config.sleepAfterDownload


docname2docid={}
#docid2docname={}

nbMultidoc=0

docqueue=set()

def addDoc(docname):
    if not docname in docname2docid:
        newid=len(docid2docname)
        docname2docid[docname]=newid
        docid2docname[newid]=[docname]
    return docname2docid[docname]

def addMultiDoc(multidoc):
    global nbMultidoc
    
    multidocid=nbMultidoc
    nbMultidoc+=1


    for (lang, name), text in multidoc:
        
        resDir=path.join(multidocDir, "%08i"%multidocid)
        if not path.exists(resDir):
            os.mkdir(resDir)
        docFile=path.join(resDir, lang)
        
        fd=file(docFile, "w")
        print >> fd, text
        fd.close()
        docname2docid[(lang, name)]=multidocid


def updateDocTemp(internal_links):
    docqueue.update(set(internal_links))
    
def updateMultiDoc(interlanguage_links, multidoc):
    docqueue.difference_update(set(interlanguage_links))
    addMultiDoc(multidoc)

    
    
def loadState():
    global nbMultidoc
    fd_queue=file(queueFile)
    for i in fd_queue:
        i=i.strip().split("  ")
        print "Before ", i
        if len(i)==2:
            docqueue.add(tuple(i))
            print "After ", tuple(i)
    fd_queue.close()
        
    fd_multidoc=file(multidocFile)
    for i in fd_multidoc:
        i=i.strip().split("  ")
        if len(i)==3:
            docname=tuple(i[0:2])
            id=int(i[2])
            nbMultidoc=max(nbMultidoc,id)
            docname2docid[docname]=id

    nbMultidoc+=1
    print "# nbMultidoc=", nbMultidoc
        
    fd_multidoc.close()
    
def saveState():
    fd_queue=file(queueFile, "w")
    for i in docqueue:
        print >> fd_queue, "%s  %s"%i
    fd_queue.close()
        
    fd_multidoc=file(multidocFile, "w")
    for docname,id in docname2docid.iteritems():
        print >> fd_multidoc, "%s  %s  %s"%(docname[0],docname[1],id)
    fd_multidoc.close()    



def linksFilter(links):
    return [(lang,name) for (lang,name) in links if lang in langs and (not (lang,name) in docname2docid)]

def crawlOneDoc(docname):
    lang,name=docname
    #print "http://%s.wikipedia.org/wiki/%s"%docname
    print "Document name:", docname
    content=urlopen("http://%s.wikipedia.org/wiki/%s"%docname).read()
    (text, internal_links, interlanguage_links)=textExtraction(content, lang)

    
    return (text, linksFilter(internal_links), linksFilter(interlanguage_links))

def crawlOneMultiDoc(docname):
    res=[]
    print "#"*40
    print "#Crawling document (1/?) %s:%s"%docname
    content,internal_links,interlanguage_links=crawlOneDoc(docname)
    res.append((docname, content))
    internal_links=set(internal_links)
    sleep(sleepAfterDownload)
    
    for i,lang_link in enumerate(interlanguage_links, 2):
        if lang_link[0]!=docname[0] and lang_link[0] in langs:
            print "#Crawling document (%i/%i) %s:%s"%(i,len(interlanguage_links)+1,lang_link[0],lang_link[1])
            content,internal_links2,_=crawlOneDoc(lang_link)
            internal_links.update(set(internal_links2))
            res.append((lang_link, content))

            sleep(sleepAfterDownload)
    return res, internal_links,interlanguage_links
    

def endlessCrawler():
    i=0
    while(len(docqueue)!=0):
        docname=docqueue.pop()
        docqueue.add(docname)
        try:
            multidoc, internal_links,interlanguage_links=crawlOneMultiDoc(docname)
        except AttributeError:
            print "#Error while processing document %s:%s"%docname
            continue
        updateDocTemp(internal_links)
        updateMultiDoc(interlanguage_links, multidoc)
        docqueue.remove(docname)
        if (i%10==0):
            print "#(i=%i) Saving state"%i
            saveState()
        i+=1
        
print "#niceness set to %i"%niceness

print "#Loading saved state"
loadState()
try:
    endlessCrawler()
except KeyboardInterrupt:
    pass
print "#Saving state"
saveState()
