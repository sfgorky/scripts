#!/usr/bin/env python

###############################################################################
# -*- coding: utf-8 -*-
"""
Created on Wed May 20 17:12:32 2015

@author: daniel
"""
from __future__ import print_function

import glob
import os
import traceback
import sys
import getopt

###############################################################################

def remove_extension(s):
    return s[ : s.rfind(".")]

###############################################################################

def my_glob(pattern, case_insensitive=False):
    def either(c):
        return '[%s%s]'%(c.lower(),c.upper()) if c.isalpha() else c
    if case_insensitive:
        return glob.glob(''.join(map(either,pattern)))
    else:
        return glob.glob(pattern)

###############################################################################

def find_common(lst):
    """ Scan the input list and find the 'common' string in all elements.
        return string
    """
    def common_start(sa, sb):
        """ returns the longest common substring from the beginning of sa and sb """
        def _iter():
            for a, b in zip(sa, sb):
                if a == b:
                    yield a
                else:
                    return
        return ''.join(_iter())
    ###########################################################################
    # Identify the common part
    nb = len(lst)
    common = ""
    if nb>0:
        common = lst[0]
        for i in xrange(1, nb):
            common = common_start(common, lst[i])
    return common


###############################################################################

def sort_list(lst):
    """
        Sort a list of filenames, considering that they have the form:
            <dirname>/<filename>##.<extension>
      """
    sorted(lst)
    return lst

    def getKey(item):
        return int(item[2])

    def getName(item):
        if len(item[0]) == 0:
            return "./{0}".format(item[1])
        else:
            return "{0}/{1}".format(item[0], item[1])


    new_lst = [ os.path.split(i) for i in lst ]
    
    # identify common part, to be able to add the 'number' to be sorted
    common = find_common( [ item[1] for item in new_lst ] )
    nb = len(common)
    removed_lst = [ (s[0], s[1], remove_extension( s[1] )[nb: ]) for s in new_lst ]

    removed_lst = sorted(removed_lst, key=getKey)

    # construct the list back
    lst = [ getName(s) for s in removed_lst ]
    return lst

###############################################################################

def rename(lst, target_prepend="", verbose=False):
    """ Rename list of filenames. The new names will be constructed with 
        a number.
        new files will be given as:
            <target_prepend><#>.<extension>

        lst: list of files

    """
    if len(lst) == 0: return

    nb = len(lst)

    new_names=[ "{0:02d}".format(i) for i in xrange(1, nb+1) ]
    for old, new in zip(lst, new_names):
        dirname = os.path.split(old)[0]
        if len(dirname)==0:
            new_name="{0}{1}.jpg".format(target_prepend, new)
        else:
            new_name="{0}/{1}{2}.jpg".format(dirname, target_prepend, new)
        if verbose:
            print("rename('{0}' '{1}')".format(old, new_name))
        else:
            # print(old, new_name)
            if 1 and old != new_name:
                os.rename(old, new_name)

###############################################################################

class MyIOException(Exception):
    pass

###############################################################################

class Options:
    def __init__(self):
        self.thisdir = "."
        self.prefix = ""
        self.filter = "*.jpg"
        self.hierarchical_walk = False
        self.verbose = False
        self.cluster = False
        
###############################################################################

def print_help( ):
    print("rename_files -h -e <extension> -d <dirname> -w -p <prefix> -f <filter>")
    print("    -d: the root directory name")
    print("    -w: walk the hierarchy and apply to all directories (default: false)") 
    print("    -p: prefix to be added to the constructed name")
    print("    -f: extension to be filtered (default: *.jpg)")
    print("    -v: verbose mode: do nothing, but write data.")
    print("    -c: run cluster algorithm, and rename files in groups")

###############################################################################

def read_command_line( ):
    options = Options( )
    argv =  sys.argv[1:]
    try:
        opts, args = getopt.getopt(argv,"hcvs:d:p:wf:")
    except getopt.GetoptError:
        print_help()
        sys.exit(0)
        
    if len(opts)==0:
        print_help()
        sys.exit(0)

    for opt, arg in opts:
        if opt == '-h':
            print_help()
            sys.exit()
        if opt == '-v':
            options.verbose = True
        if opt == '-d':
            options.thisdir = arg
        if opt == '-p':
            options.prefix = arg
        if opt == '-w':
            options.hierarchical_walk = True
        if opt == '-c':
            options.cluster = True
    return options

###############################################################################

def levenshteinDistance(s1,s2):
    if len(s1) > len(s2):
        s1,s2 = s2,s1
    distances = range(len(s1) + 1)
    for index2,char2 in enumerate(s2):
        newDistances = [index2+1]
        for index1,char1 in enumerate(s1):
            if char1 == char2:
                newDistances.append(distances[index1])
            else:
                newDistances.append(1 + min((distances[index1],
                                             distances[index1+1],
                                             newDistances[-1])))
        distances = newDistances
    return distances[-1]

###############################################################################

# short function. Returns true, if 2 entries are not in the same cluster
def not_in_same_cluster(a, b):
    if (len(a) == len(b) and len(a)>3):
        return True
    return False

###############################################################################

def in_number_cluster(a):
    s = remove_extension(a)    
    if len(s) <=3 and s.isdigit():
        return True
    return False

###############################################################################

def create_cluster(lst, min_dist=2, not_in_same_cluster=not_in_same_cluster, dist_func=levenshteinDistance):
    """ Create data cluster by coputing the distance between the elements.
        Elements on each cluster will have the given minimum distance.
        
        Returns:
            list< cluster_lst, not_in_cluster>
            cluster_lst: list of clusters. Each cluster is a list of elements.
            not_in_cluster: elements that do not fit in any cluster
    """    
    nb = len(lst)
    cluster_lst = []
    number_cluster = []
    not_in_cluster = []
    mat = {} 

    for i,s1 in zip(range(0, nb), lst):
        if in_number_cluster(s1):
            number_cluster += [ s1 ]
            mat[i, i] = -1
        else:
            mat[i, i] = 0
            for j,s2 in zip(range(i+1, nb), lst[i+1:]):
                if not_in_same_cluster(s1, s2):
                    dist = dist_func(s1, s2)
                else:
                    dist = 999
                mat[i, j] = dist
        
    for i in xrange(0, nb):
        # processing index i
        if mat[i, i] >= 0:
            cluster = [ lst[i] ]
            for j in xrange(i+1, nb):
                idx = mat[i, j]
                if idx <= min_dist:
                    # j is in the same cluster as i
                    cluster += [ lst[ j ] ]
                    mat[j, j] = -1
            cluster_lst += [ cluster ]

    # process number cluster!
    if len(number_cluster) > 0:
        int_lst = [ int(remove_extension(s)) for s in number_cluster ]
        int_lst.sort()
        number_cluster = [ "{0}.jpg".format(i) for i in int_lst ]


    return ( cluster_lst, number_cluster, not_in_cluster )

###############################################################################

##############################################################################

def rename_files(dirname, verbose=True, cluster=False, target_prepend="", file_filter="*.jpg", hierarchical=False):

    case_insensitive=True

    ###########################################################################

    os.chdir(dirname)
    current_dir = os.getcwd()

    if hierarchical:
        for root, dirs, files in os.walk(dirname, topdown=True, onerror=None, followlinks=False):
            
            os.chdir("{0}/{1}".format(current_dir, root))

            lst = my_glob("{0}".format(file_filter), case_insensitive=case_insensitive)
            if cluster:
                cluster_lst, number_cluster, not_in_cluster = create_cluster(lst)
                if verbose:
                    print("{0:20s}: nb: {1:2d}, nb_cluster:{2}, nb_out_cluster:{3}"
                        .format(root, len(lst), len(cluster_lst), len(not_in_cluster)))
                else:
                    # process the number only cluster
                    if len(number_cluster)>0:
                        rename(number_cluster, target_prepend, verbose=verbose)
                    # process the other clusters --- TBD

            else:
                if verbose:
                    print("nb: {0}".format(len(lst)))
                else:
                    lst = sort_lst(lst)
                    rename(lst, target_prepend, verbose=verbose)
            os.chdir("{0}".format(current_dir))
    else:
        lst = my_glob(file_filter, case_insensitive=case_insensitive)
        lst = sort_list(lst)
 
        if verbose:
            print("list: {0}".format(" ".join(lst)))
        rename(lst, target_prepend, verbose=verbose)

    os.chdir(current_dir)

###############################################################################

if __name__ == "__main__":
    try:
        options = Options() 
        options = read_command_line( )
        # options.verbose = True
        if rename_files( dirname=options.thisdir, 
                         cluster=options.cluster,
                         verbose=options.verbose,
                         target_prepend=options.prefix, 
                         file_filter=options.filter, 
                         hierarchical=options.hierarchical_walk):
            sys.exit(0)
        sys.exit(1)

    except MyIOException, e:
        print('Error:', e.args[0])
        sys.exit(1)
        
    except Exception:
        traceback.print_exc(file=sys.stdout)
        e = sys.exc_info()
        print("Error at ade_state_translator.py\n{0}\n{1}".format(str(e[0]), str(e[1])))
        sys.exit(1)



