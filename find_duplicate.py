#!/usr/bin/env python

from __future__ import print_function


# dupFinder.py
import os, sys
import hashlib
import fnmatch, re
import sys, getopt


def insensitive_glob(pattern):
    def either(c):
        return '[%s%s]'%(c.lower(),c.upper()) if c.isalpha() else c
    return glob.glob(''.join(map(either,pattern)))

##############################################################################

def getExtension(fname):
    s = os.path.splitext(fname)[1]
    if len(s) == 0:
    	return s
    return s[1:]

##############################################################################

def getFileSize(fname):
    if os.path.exists(fname):
        return os.path.getsize(fname)
    return 0

##############################################################################

def findDup(parentFolder, fileFilter="", ignore_empty=True):
    """ Dups in format {hash:[names]}
    
        fileFilter: filter to the files t o be consiered
    """

    filterFile = False
    if len(fileFilter) > 0:
        filterFile = True
        regex = fnmatch.translate(fileFilter)
        reobj = re.compile(regex)

    dups = {}
    for dirName, subdirs, fileList in os.walk(parentFolder):
        # print('Scanning %s...' % dirName)
        for filename in fileList:
            # Get the path to the file
            path = os.path.join(dirName, filename)
        
            process = True
            if filterFile and reobj.match(path) == None:
                process = False
 
            if process:
                filesize = getFileSize(path)
                if ignore_empty and filesize==0:
                    process = False

            if process:         
                # Calculate hash
                file_hash = hashfile(path)
                # Add or append the file path
                if file_hash in dups:
                    dups[file_hash].append(path)
                else:
                    dups[file_hash] = [path]
            ##################################################################

    return dups
 
############################################################################## 
# Joins two dictionaries
def joinDicts(dict1, dict2):
    for key in dict2.keys():
        if key in dict1:
            dict1[key] = dict1[key] + dict2[key]
        else:
            dict1[key] = dict2[key]
 
##############################################################################
 
def hashfile(path, blocksize = 65536):
    afile = open(path, 'rb')
    hasher = hashlib.md5()
    buf = afile.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    afile.close()
    return hasher.hexdigest()

##############################################################################
  
def printResults(dict1):
    results = list(filter(lambda x: len(x) > 1, dict1.values()))
    if len(results) > 0:
        print('# Duplicate list:')
        print('######')
        for result in results:
            for subresult in result:
                print('%s' % subresult)
            print('####')
 
    else:
        print('No duplicate files found.')
 
##############################################################################

class Options:
    def __init__(self):
        self.dirlist = []
        self.filter = ""

##############################################################################

def process_parameter(argv):
    option = Options( )
    try:
        opts, args = getopt.getopt(argv,"hd:f:",["dir=","filter="])
    except getopt.GetoptError:
        print("dupfinder -d <dirname> -f <filter>")
        sys.exit(2)

    # print(opts, args)
    for opt, arg in opts:
        if opt == '-h':
            print("dumpfinder -d <dirname> -f <filter>")
            sys.exit()
        elif opt in ("-d", "--dir"):
            option.dirlist.append(arg)
        elif opt in ("-f", "--filter"):
            option.filter = arg
    return option

##############################################################################

if __name__ == '__main__':
    if len(sys.argv) > 1:

        option = process_parameter(sys.argv[1:])

        filematch = option.filter
        folders   = option.dirlist

        # print("folders: {0}".format(folders))
        # print("filter:  {0}".format(filematch))

        #######################################################################
        dups = {}
        for i in folders:
            # Iterate the folders given
            if os.path.exists(i):
                # Find the duplicated files and append them to the dups
                joinDicts(dups, findDup(i, filematch))
            else:
                print('%s is not a valid path, please verify' % i)
                sys.exit()
        printResults(dups)
  


