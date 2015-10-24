#!/usr/bin/env python
"""

"""
from __future__ import print_function

import os
import shutil
import traceback
import sys
import glob
import fileinput
import re
import getopt

CPP_EXTENSION = ["*.cpp", "*.c", "*.cc", "*.h" ]

###############################################################################

# Replace on a given file, the 'string 'fromText' by the string 'toText'. The 
# code will match the exact word.
def replace(fname, fromText, toText, to_stdout=True):
    fromkey = r"\b{0}\b".format(fromText)
    tokey   = "{0}".format(toText)
    inplace = True
    if to_stdout:
        inplace = False
    for line in fileinput.input(fname, inplace=inplace):
        #print(line.replace(fromText, toText), end='')
        new_line = re.sub(fromkey, tokey, line)
        print(new_line, end='')

###############################################################################

# @param path path where to apply the change. default to "."
# @param extension_list list of patterns to apply the file chnages.
# @param file_list extra list of files to be processed
def search_replace(fromText, toText, path=".", extension_list=[], file_list=[]):
    if len(fromText) == 0 or len(toText) == 0:
        return

    flist = []
    # grab all the file names
    for extension in extension_list :
        flist += glob.glob(path +  "/" + extension)

    flist += file_list
    
    to_stdout = False
    
    # process all the files.
    for filename in flist:
        if os.path.isfile(filename):
            replace(filename, fromText, toText, to_stdout=to_stdout)
        else:
            print("error: file {0} does not exist.".format(filename))
    
###############################################################################

class Options:
    def __init__(self):
        self.fromText = ""
        self.toText = ""
        self.fileType = ""
        self.includePath = "."
        self.outdir = "."
        self.file_list = []

###############################################################################

def read_command_line( ):
    options = Options( )
    apname = sys.argv[0]
    argv =  sys.argv[1:]

    def print_help():
        print(apname + " ")
        print("parameters:")
        print("    -c            : process all cpp files (*.cpp *.h *.cc *.c)")
        print("    -i    <fname> : input filename")
        print("    -f    <text>  : from text")
        print("    -t    <text>  : to text")
        print("    -I    <include path> ")
    
    try:
        opts, args = getopt.getopt(argv,"hcf:t:i:I:", ["from=", "to=", "cpp="])

    except getopt.GetoptError:
        # print_help()
        sys.exit(2)
        

    if len(opts)==0:
        print_help()
        sys.exit()
    
    for opt, arg in opts:
        if opt == '-h':
            print_help()
            sys.exit()
        if opt in ("-f", "--from"):
            options.fromText = arg
        if opt in ("-t", "--to"):
            options.toText = arg
        if opt in ("-c", "--cpp"):
            options.fileType = "cpp"
        if opt == "-I":
            options.includePath = arg
        if opt == "-i":
            options.file_list = [ arg ]

    return options

###############################################################################

if __name__== "__main__" :
    try:
        options = read_command_line( )
        extension_list = []

        if options.fileType == "cpp":
            extension_list = CPP_EXTENSION
        
        ok = True
        if len(options.fromText) == 0:
            ok = False
            print("error: from text not given")
        if len(options.toText) == 0:
            ok = False
            print("error: 'to' text not given")
        
        if ok:
            search_replace(fromText = options.fromText,
                           toText   = options.toText,
                           path     = options.includePath,
                           extension_list = extension_list,
                           file_list = options.file_list)

    except Exception, e:
        print('Error:', e.args[0])
        sys.exit(1)

    except:        
        #traceback.print_exc(file=sys.stdout)
        #e = sys.exc_info()        
        #print("Error at read_config.py: {0} {1}".format(str(e[0]), str(e[1])))
        sys.exit(1)



