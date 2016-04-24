#! /usr/bin/python

import os
from os import path
import urllib2
from textextraction import textExtraction
import threading
import sys

base_dir = "../wikidata/"
output_dir = sys.argv[3]
input_file = sys.argv[1]

def saveState(cityFile, text):
    print "Saving the city file %s" % cityFile
    fd = file(cityFile, "w")
    print >> fd, text


def getData(lines, dir):
    cnt = 0
    success = 0
    for cityName in lines:
        if not cityName:
            continue
        print cnt
        print cityName
        cityFile = path.join(dir, cityName)
        try:
            if not path.isfile(cityFile):
                content = urlopen("http://en.wikipedia.org/wiki/%s"%cityName).read()
                (text, internal_links, interlanguage_links) = textExtraction(content, "en")
                saveState(cityFile, text)
            success += 1
        except:
            print "#Error while processing document for city: %s"%cityName

        cnt += 1

    print "Success ", success
    print "Total count ", cnt


def runThread(lines, threadCnt, citiesDir, threads):
    print threadCnt
    dir = path.join(citiesDir, str(threadCnt))
    if not path.exists(dir):
        os.mkdir(dir)
    this_thread = threading.Thread(target = getData, args = (lines, dir, ))
    this_thread.start()
    threads.append(this_thread)


citiesDir = path.join(base_dir, output_dir)
if not path.exists(citiesDir):
    os.mkdir(citiesDir)

urlopen = urllib2.urlopen
lines = [line.rstrip('\n') for line in open(path.join(base_dir, input_file))]

num = 0
threadCnt = 0
threads = []

each_thread_load = int(sys.argv[2])

while num < len(lines):
    threadCnt += 1
    runThread(lines[num:num+each_thread_load], threadCnt, citiesDir, threads)
    num += each_thread_load

print "Waiting.."

for thread in threads:
    thread.join()

print "Complete."
