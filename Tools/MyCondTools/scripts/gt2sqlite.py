#!/usr/bin/env python

import os
import sys
from ConfigParser import ConfigParser
from copy import copy
from optparse import OptionParser, Option, OptionValueError
#import coral
#from CondCore.TagCollection import Node,tagInventory,CommonUtils,entryComment
from operator import itemgetter
import Tools.MyCondTools.RunInfo as RunInfo


import commands
import calendar
import datetime

# tools for color printout
import Tools.MyCondTools.color_tools as colorTools
import Tools.MyCondTools.gt_tools as gtTools
import Tools.MyCondTools.odict as odict

#FIXME: placeholder
def checkExportedIov():
    """Should return true if all the IOVs in the tag to be migrated are also in the target tag"""

    
        # iovtable_sqlite = gtTools.IOVTable()
        # iovtable_sqlite.setFromListIOV(listiov_sqlite[1])
        

        # # list IOV for the target tag (cache the list of IOV by pclTag: in case has not changed there is no need to re-run listIOv)
        # iovtable_oracle = gtTools.IOVTable()
        # if not targetOracleTag in oracleTables:
        #     # IOV for this tag in ORACLE has not yet been cached -> will now list IOV
        #     listiov_oracle = gtTools.listIov(targetOracleConnect, targetOracleTag, config.passwdfile)
        #     print "      listing IOV..."
        #     if listiov_oracle[0] == 0:
        #         iovtable_oracle.setFromListIOV(listiov_oracle[1])
        #         oracleTables[targetOracleTag] = iovtable_oracle
        # else:
        #     # get the IOV from the cache dictionary
        #     print "      getting IOV list from cache..."
        #     iovtable_oracle = oracleTables[targetOracleTag]

        # for iov in iovtable_sqlite._iovList:
        #     iovOracle = gtTools.IOVEntry()
        #     if not iovtable_oracle.search(iov.since(), iovOracle):
        #             print "    " + colorTools.warning("Warning:") + " lumibased IOV not found in Oracle for since: " + str(iov.since())
        #             missingIOV = True

        # if missingIOV:
        #     print "      " + colorTools.warning("Warning:") + " not all IOVs found in Oracle!!!"
        # else:
        #     print "      All IOVs found in oracle: upload OK!"

        # rRep.uploadSucceeded = not missingIOV

    print 'OK'
    return True



if __name__     ==  "__main__":

    usage = "usage: %prog [options] <gtname> <destination> ..."
    description = "Migrate a GT, including all the tags to an sqlite file. WARNING: this can take quite some time...get a coffee and be patient!"

    # instantiate the parser
    parser = OptionParser(usage=usage, description=description)


    # ---------------------------------------------------------
    # --- set the command line options

    #parser.add_option("--dump", action="store_true",dest="dump",default=False, help="dump the entry in the GT")
    #parser.add_option("--account", action="store_true",dest="checkaccount",default=False, help="check also the account name")
    #parser.add_option("--ignore-suffix", action="append",dest="ignoredsuffixes",default=[], help="add an account suffix to the list of ignored suffixes (for archival accounts)")
    
    #parser.add_option("--frontier", action="store_true",dest="frontier",default=False, help="use frontier instead of oracle")
    
    #parser.add_option("-r", "--run-number", dest="runnumber",
    #                  help="run #: determines which IOV to dump. If not specified the last IOV + 1 will be used.",
    #                  type="int", metavar="<run #>")

    (options, args) = parser.parse_args()

    if(len(args) != 2):
        print "***Error: GT name and destination string not specified"
        print " usage: %prog [options] <gtname> <destination> ..."
        print " try --help for more details"
        sys.exit(1)
    print args
    
    # read a global configuration file
    cfgfile = ConfigParser()
    cfgfile.optionxform = str


    # FIXME: configure this
    CONFIGFILE = "GT_branches/Common.cfg"
    print 'Reading configuration file from ',CONFIGFILE
    cfgfile.read([ CONFIGFILE ])
    passwdfile             = cfgfile.get('Common','Passwd')
    gtconnstring           = cfgfile.get('Common','GTConnectString')

    runinfotag = 'runinfo_31X_hlt' # FIXME: get it from the cfg


    globaltag1 = args[0]
    sqlite_name = args[1]    
    # print "Compare "
    # print "      GT 1: " + globaltag1 + " with GT 2: " + globaltag2

    filename1 = globaltag1 + '.conf'


    # create the collection of tags
    tagCollection1 = gtTools.GTEntryCollection()

    # --------------------------------------------------------------------------
    # fill the collection
    if not gtTools.confFileFromDB(globaltag1, filename1, gtconnstring, passwdfile):
        print colorTools.error("*** Error" + " original GT conf file: " + filename1 + " doesn't exist!")
        sys.exit(5)

    gtTools.fillGTCollection(filename1, globaltag1, tagCollection1)



    print "    GT: " + globaltag1 + " has " + str(tagCollection1.size()) + " entries"

    # loop over all records and compare the tag names and the # of payloads
    index = 1
    total = len(tagCollection1._tagList)
    for entry1 in tagCollection1._tagList:

        print '[%s/%s]'%(str(index),str(total)),
        toBeExported = True
        
        # try to list the IOV for this tag in the target sqlite file
        listiov_sqlite_out = gtTools.listIov(sqlite_name, entry1.tagName(),'',silent=True)
        #listiov_sqlite_out = (0,0)

        if  listiov_sqlite_out[0] == 0:
            print 'Tag: %s, is already in the target sqlite_file, now checking IOVs...'%entry1.tagName(),
            if checkExportedIov():
                # in this case there is no need to export the tag
                toBeExported = False
        

        if toBeExported:
            # export the tag from the source account to the target sqlite file
            statandout = gtTools.exportIov("oracle://cms_orcon_adg/"+entry1.account(), entry1.tagName(),sqlite_name,passwdfile)
            print 'Exporting tag', entry1
            if  statandout[0] != 0:
                print "***Error exporting tag, quitting!"
                sys.exit(2)

        # now replace the connection string in the GT configuration
        newEntry = entry1
        newEntry._pfn = sqlite_name
        newEntry._account = ''
        newEntry._connstring = sqlite_name

        #tagCollection1.modifyEntryConnection(entry1.tagName(),sqlite_name)
        tagCollection1.replaceEntry(newEntry)
        index+=1

    
    # dump the GT configuration to a file
    newgtconffile = globaltag1+"_exported.conf"
    tagCollection1.dumpToConfFile(newgtconffile, globaltag1, "DUMMY", sqlite=sqlite_name)

    # actually create the GT in the sqlite file
    print '--- Create GT: %s in target sqlite %s' % (globaltag1, sqlite_name)
    execstring = 'createglobaltag %s %s' % (newgtconffile,globaltag1)
    evaloutands = commands.getstatusoutput(execstring)

    if evaloutands[0] != 0:
        print evaloutands[1]
        print "***Error creating the GT, quitting!"
        sys.exit(3)

    today = datetime.datetime.today()
    print evaloutands[1]
    print "GT " + globaltag1 + " created on: " + str(today)

