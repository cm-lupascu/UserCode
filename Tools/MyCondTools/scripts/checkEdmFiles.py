#!/usr/bin/env python
import os
import sys
from optparse import OptionParser
import commands
from stat import *
from ConfigParser import ConfigParser
from Tools.MyCondTools.color_tools import *

from datetime import date
from datetime import datetime

import shutil


if __name__     ==  "__main__":
    
    # set the command line options
    parser = OptionParser()
    
    #    parser.add_option("-t", "--globaltag", dest="gt",
    #                      help="Global-Tag", type="str", metavar="<globaltag>")
    #     parser.add_option("-r", "--release", dest="release",
    #                       help="CMSSW release", type="str", metavar="<release>")
    #parser.add_option("--local", action="store_true",dest="local",default=False)

    (options, args) = parser.parse_args()
    #print "OPTIONS: ", options
    #print "ARGS: ", args


    # check that the dir does not yet exist
    releasearea = ''
    try:
        print "Looking for CMSSW environment....",
        releasearea = os.environ["CMSSW_BASE"]
    except:
        print "no release area found"
        sys.exit(1)
    print "done"
    
    topdirname = releasearea + "/src/"

    os.chdir(topdirname)

    
    CONFIGFILE = 'gtValid.cfg'

    if not os.path.isfile(CONFIGFILE):
        print error("*** Error:") + " cfg file: " + CONFIGFILE + " doesn't exist!"
        sys.exit(1)


    diffconfig = ConfigParser()
    diffconfig.optionxform = str

    print 'Reading configuration file from ',CONFIGFILE
    diffconfig.read(CONFIGFILE)


    globaltagsandWfIds = dict()
    if diffconfig.has_section('Tags'):
        globaltagsandWfIds = dict(diffconfig.items('Tags'))

    gts = globaltagsandWfIds.keys()

    
    fileList = os.listdir(topdirname)
    for dirname in fileList:
        if os.path.isdir(dirname) == True:
            for gt in gts:
                if gt in dirname:
                    # list the root files in the directory
                    print "GT: " + blue(gt) + " relval: " + globaltagsandWfIds[gt]
                    rootfiles = os.listdir(topdirname + "/" + dirname)
                    for rootfile in rootfiles:
                        #print rootfile
                        if "root" in rootfile or rootfile == "reco.root" or rootfile == "raw.root":
                            #print rootfile
                            command = "edmEventSize -v " + dirname + "/" + rootfile
                            outandstat = commands.getstatusoutput(command)
                            nEvents = 0
                            # print rootfile
                            if outandstat[0] != 0:
                                if "DQM" in rootfile:
                                    continue 
                                elif not "contains no Events" in outandstat[1]: 
                                    print outandstat[1]
                                    sys.exit(1)
                            else:
                                nEvents = int((outandstat[1].split("\n")[1]).split()[3])
                                
                            # get the file size
                            size = os.path.getsize(dirname + "/" + rootfile)
                            
                            print "    " + rootfile + "\t\t\t # events: " + str(nEvents) + "\t\t\t size: " + str(size)
                            
                            
    sys.exit(0)






    
    
