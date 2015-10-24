#!/usr/bin/env python
"""
Application to back up souce code.

Command line parameters:
 -c           : Clears the backup directory (remove old backups, leave last one
 -r           : Recursive, on all sub-directories.
 -i <text>    : Info text, which is written to the manifesto directory
 -d <dirname> : Directory to backup. Use '.' to signify the current dir
 --repository : Prints the current repository name
 --list       : The list all the entries on the repository")
--diff  <idx> : diffs the current directory againt the same in the database, 
                index idx (uses diff)

Environment variable:
     BACKUP_ROOT the main location where the backup will be done.
"""

from __future__ import print_function

import datetime
import time
import fnmatch
import os
import shutil
import traceback
import sys
import glob
import fileinput
import re
import getopt

CPP_EXTENSION = ["*.cpp", "*.c", "*.cc", "*.h" ]


def get_repository( ):
    rootdir = os.getenv("BACKUP_ROOT")
    if not rootdir or len(rootdir) == 0:
        rootdir = "/Users/daniel/Desktop/mypack/source/backup"
    return rootdir

###############################################################################

def copy(src, dst):
    if os.path.isdir(dst):
        dst = os.path.join(dst, os.path.basename(src))
    shutil.copyfile(src, dst)

###############################################################################

def rmdir(dir):
    if os.path.isdir(dir):
        shutil.rmtree(dir)

###############################################################################

def mvdir(fromdir, todir):
    if os.path.isdir(fromdir):
        shutil.move(fromdir, todir)


###############################################################################

def get_size(p):
    from functools import partial
    prepend = partial(os.path.join, p)
    size = sum([(os.path.getsize(f) if os.path.isfile(f) else getFolderSize(f)) for f in map(prepend, os.listdir(p))])
    s  = size / (1024*1024*1.0)
    return float("%.2f" % s)

###############################################################################

def list_repository( ):
    rep = get_repository( )
    dirlist = glob.glob(rep+"/*")
    for d in dirlist:
        if os.path.exists(d):
            print(os.path.basename(d))

###############################################################################

def next_backup_name(rootdir, nameroot):
    matchkey = "{0}\\.[0-9]{{2}}".format(nameroot)
    lst =  glob.glob(rootdir + os.sep + nameroot + ".*")
    lst = [ l for l in lst if re.match(matchkey, os.path.basename(l))  ]

    if len(lst) == 0:
        return nameroot + ".01"
    else:
        lst = sorted(lst)
        name = lst[-1]
        dot_pos = name.rfind(".")

        rootname = name[ : dot_pos ]
        index    = name[ dot_pos+1 : ]
        index    = int(index)+1
        # next index, in str
        index    = "%02d" % index
        return nameroot + "." + index

###############################################################################

def match_filter(fname, filter):
    for fl in filter:
        if fnmatch.fnmatch(fname, fl):
            return True
    return False

############################################################################### 

def diff_against(dir, idx):
    if len(dir) == 0:
        print("error: source dir is not given")
        return 
    if idx < 1:
        print("error: index is not given.")
        return
    dir = os.path.realpath(dir)
    rootdir = get_repository( )
    nameroot = os.path.basename(dir)

    d1 = dir
    d2 = rootdir + "/" + nameroot + "." + "%02d" % idx

    ok = True
    if not os.path.exists(d1):
        print("error: path '{0}' does not exist".format(d1))
        ok = False
    if not os.path.exists(d2):
        print("error: path '{0}' does not exist".format(d2))
        ok = False

    if ok:
        os.system("diff -u {0} {1}".format(d1, d2))

###############################################################################

def backup(dir, info="", recursive=False, filter=[ "*.o", "*.obj" ], clear = False ):
    if(len(dir) == 0):
        print("error: source dir is not given")
        return
    if not os.path.exists(dir): 
        print("error: cannot find source directory: {0}".format(dir))
        return 
    dir = os.path.realpath(dir)

    rootdir = get_repository( )
    nameroot = os.path.basename(dir)
    
    if clear:
        # clear history, and rename the last one as 01
        lst = glob.glob(rootdir + os.sep + nameroot + ".*")
        if len(lst) <= 1: 
            return 

        lst = sorted(lst)
        # the last one is the 'good one'
        # delete all others
        good = lst[-1]
        lst = lst[0: len(lst)-1]

        for dir in lst:
            rmdir(dir)

        mvdir(good, rootdir + os.sep + nameroot + ".01")
        return 
    ###########################################################################

    backup_name = next_backup_name(rootdir, nameroot)

    print("backup name: {0}".format(backup_name))

    fromdir = dir
    todir   = rootdir + os.sep + backup_name + os.sep

    # do the actual copy
    os.mkdir(todir)

    # filter the list to copy
    filelist = []
    for fname in glob.glob(dir + os.sep + "*.*"):
        # filter - do not copy 
        if not match_filter(fname, filter):
            filelist += [ fname ]

    # Copy the files
    for f in filelist:
        copy(f, todir)
    # look on the backup directory 

    print("dest:{0}, {1} files, {2} Mb".format(backup_name, len(filelist), get_size(todir)))
    with open(todir + os.sep + ".backup", "w") as f:
        print("backup at: {0}".format(time.strftime("%Y/%m/%d @ %H:%M:%S")), file=f)
        print("info: {0}".format(info),                                     file=f)



###############################################################################

class Options:
    def __init__(self):
        self.clear = False
        self.recursive = False
        self.info = ""
        self.dir = ""
        self.idx = -1

        self.print_repository = False
        self.list = False
        self.diff = False

###############################################################################

def read_command_line( ):
    options = Options( )
    apname = sys.argv[0]
    argv =  sys.argv[1:]

    def print_help():
        print(apname + " ")
        print("parameters:")
        print("    -c              : clear the backup directory (remove old backups, leave last one)")
        print("    -r              : recursive")
        print("    -i    <text>    : info text")
        print("    -d    <dirname> : dir to backup")
        print("    --repository    : prints the current repository")
        print("    --list          : list all the entries on the repository")
        print("    --diff  <idx>   : diff this directory againt the same in the database, index idx")
        print("")
        print("env. variable:")
        print("    BACKUP_ROOT={0}".format(get_repository()))

    try:
        opts, args = getopt.getopt(argv,"hcri:d:", ["dir=", "info=", "repository", "list", "diff="])

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
        elif opt in ("-i", "--info"):
            options.info = arg
        elif opt in ("-d", "--dir"):
            options.dir= arg
        elif opt in ("--repository"):
            options.print_repository = True
        elif opt in ("--list"):
            options.list = True
        elif opt in ("-r"):
            options.recursive = True
        elif opt in ("-c"):
            options.clear = True
        elif opt in ("--diff"):
            options.idx = int(arg)
            options.diff = True
    return options

###############################################################################

if __name__== "__main__" :
    try:
        options = read_command_line( )
        extension_list = []
        ok = True
        if ok:
            if options.print_repository:
                print(get_repository( ))
            elif options.list:
                list_repository( )
            elif options.diff:
                diff_against(options.dir, options.idx)
            else:
                backup(recursive = options.recursive,
                       info      = options.info,
                       dir       = options.dir,
                       filter    = [ "*.o", "*.obj" ],
                       clear     = options.clear
                    )

    except Exception, e:
        print('Error:', e.args[0])
        sys.exit(1)

    except:        
        #traceback.print_exc(file=sys.stdout)
        #e = sys.exc_info()        
        #print("Error at read_config.py: {0} {1}".format(str(e[0]), str(e[1])))
        sys.exit(1)


###############################################################################




