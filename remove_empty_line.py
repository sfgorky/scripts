#!/usr/bin/env python
from __future__ import print_function

import string
import sys
import getopt
import codecs
import os.path

###############################################################################

import subprocess

'''
    \brief returns a charset associated with fname. if 'fname' does not exist,
            Returns empty string.
         
            Uses: 'file -I'
'''
def get_charset(fname):
    charset = ""
    if os.path.isfile(fname):
        p = subprocess.Popen([ 'file', '-I', fname],  stdout=subprocess.PIPE,
                                                      stderr=subprocess.PIPE)
        out, err = p.communicate()
        charset = out[ out.rfind("=")+1 : ]
    return charset


###############################################################################
def isprintable(s, codec='utf8'):
    try: 
        s.decode(codec)
    except UnicodeDecodeError: 
        return False
    else: 
        return True
    
###############################################################################
def print_hexa(str):
    ss = ""
    for s in str:
        ss += "{0:02x} ".format(ord(s))
    print(">>", ss, "<<")

###############################################################################
def trim_begining(s):
    if len(s)>0:
        if s[0] in ('\r', '\n'):
            s = s[1: ]
    return s
    

#The 'u' in front of the string values means the string has been represented as unicode

###############################################################################
# read the entire file, and remove the empty lines
def processFile(infile, outfile, codecpage="", verbose=False):

    # if outfile is empty, uses the input file.
    if not outfile:
        outfile = infile
    
    lst = [] 
    has_codec = codecpage and codecpage
    if verbose:
        print("Open file: '{0}', codecpage: {1}".format(infile, codecpage))
    if has_codec:
        src =  codecs.open(infile, "r", codecpage) 
    else:
        src = open(infile)
    if src:
        for src_line in src:
            str = src_line.rstrip()
            str = trim_begining(str)
            if len(str)>1:
                #print_hexa(str)
                #print(src_line.rstrip())
                #print("___\n")
                lst += [ str ] 
        pass
    pass
    # print(lst)

    ############################################################################
    # create the output file: end of file 
    if has_codec:
        with open(outfile, "w") as dest:
            for line in lst:
                print(line.encode("ascii", 'replace'), file=dest)
            pass
        pass
    else:
        with open(outfile, "w") as dest:
            for line in lst:
                print(line, file=dest)
            pass
        pass
    pass
    
###############################################################################

class Options:
    def __init__(self):
        self.fromText = ""
        self.toText = ""
        self.codec_page =  ""
    

###############################################################################

def read_command_line( ):
    options = Options( )
    apname = os.path.basename(sys.argv[0])
    argv =  sys.argv[1:]

    def print_help():
        print("")
        print("NAME")
        print("\t" + apname)
        print("")
        print("SYNOPSIS")
        print("\t" + apname + " -i <inFile> -o <outFile> [ --page=<inCodecPage> ] ")
        print("")
        print("OPTIONS:")
        print("\t-i    <text>     : from text")
        print("\t-o    <text>     : to text")
        print("\t-page <codepage> : decode page name")
        print("")
        print("DESCRIPTION")
        print("\tProcess input text file and remove empty lines.")
        print("\tThe put will be exported in 'ascii format'. The input page type (if unicode)")
        print("\twill be determined by the usage of 'file -I' command. You can entere the type")
        print("\tmanually by using '-page' parameter.")
        print("")
      
        print("Note: Should use file -I <filename> to find out the file page")
        print("      If codec page not given, it will use the value given by 'file -I inputFile")
        print("")

    try:
        opts, args = getopt.getopt(argv,"hi:o:p:", ["from=", "to=", "page="])
    except getopt.GetoptError:
        # print_help()
        sys.exit(2)

    if len(opts)==0:
        print_help()
        sys.exit(0)

    # print(opts)
    for opt, arg in opts:
        if opt == '-h':
            print_help()
            sys.exit()
        elif opt in ("-i", "--from"):
            options.fromText = arg
        elif opt in ("-o", "--to"):
            options.toText = arg
        elif opt in ("-p", "--page"):
            options.codec_page = arg
    return options

###############################################################################

if __name__== "__main__" :
    
    try:
        options = read_command_line( )
        ok = True
        if not options.fromText:
            ok = False
            print("Error: input file not given")
            sys.exit(1)

        if not os.path.isfile(options.fromText):
            print("Error: cannot find input file %0".format(options.fromText))
            sys.exit(1)

        if not options.codec_page:
            options.codec_page = get_charset(options.fromText)
        
        if ok:
            processFile(infile    = options.fromText,
                        outfile   = options.toText,
                        codecpage = options.codec_page)
                        
    except Exception, e:
        print('Error: ->', e.args[0])
        sys.exit(1)

    except:        
        #traceback.print_exc(file=sys.stdout)
        #e = sys.exc_info()        
        #print("Error at read_config.py: {0} {1}".format(str(e[0]), str(e[1])))
        sys.exit(1)


###############################################################################

