import os
import sys
from ConfigParser import ConfigParser
from copy import copy
from optparse import OptionParser, Option, OptionValueError
#import coral
#from CondCore.TagCollection import Node,tagInventory,CommonUtils,entryComment
from operator import itemgetter
#import datetime
from datetime import datetime
try:
    from CondCore.Utilities.timeUnitHelper import *
except ImportError:
    print "CondCore.Utilities.timeUnitHelper not found"


# tools for color printout
from color_tools import *

import commands

def stripws(myinput):
    result=('').join(myinput.split(' '))
    result=('').join(result.split('\n'))
    return result
def convertCommaInsideBraket(metadatastr, replacementText):
    if metadatastr.find(replacementText) != -1:
        print "Error, TEMPORARY_REPLACEMENT_TEXT found in the string, edit the code and change the string used in the parser."
        os.exit(1)
    newmetadatastr = ''
    insideBraket = False
    for element in metadatastr:
        toSave = element
        if insideBraket:
            if element == ">":
                insideBraket = False
            elif element == ",":
                toSave = replacementText
        elif element == "<":
            insideBraket = True
        newmetadatastr += toSave
    # print "newmetadatastr = ", newmetadatastr
    return newmetadatastr
def converttagdata(value):
    mytagdata={}
    startbrack=value.find('{')
    endbrack=value.find('}')
    metadatastr=value[startbrack+1:endbrack]
    mytagdata['tagname']=value[0:startbrack]
    replacementText="TEMPORARY_REPLACEMENT_TEXT"
    newmetadatastr = convertCommaInsideBraket(metadatastr, replacementText)
    metadatalist=newmetadatastr.split(',')
    for rawPair in metadatalist:
        pair = rawPair.replace(replacementText, ',')
        mydata=pair.split('=',1)
        mytagdata[mydata[0]]=mydata[1]
    return mytagdata
# def converttagdata(value):
#     mytagdata={}
#     startbrack=value.find('{')
#     endbrack=value.find('}')
#     metadatastr=value[startbrack+1:endbrack]
#     mytagdata['tagname']=value[0:startbrack]
#     metadatalist=metadatastr.split(',')
#     print "medadatalist =", metadatalist
#     for pair in metadatalist:
#         print "pair =", pair
#         mydata=pair.split('=',1)
#         mytagdata[mydata[0]]=mydata[1]
#     return mytagdata
def converttagcollection(value):
    cleanvalue=stripws(value)
    mytagcollection=[]
    taglist=cleanvalue.split(';')
    for tagdata in taglist:
        mytagcollection.append(converttagdata(tagdata))
    return mytagcollection
def check_tagdata(option, opt, value):
    try:
        return converttagcollection(value)
    except ValueError:
        raise OptionValueError(
            "option %s: invalid tagdata: %r" % (opt, value))

def convertnodedata(mynodevalue):
    mynodedata={}
#    datastr=('').join(value.split(' '))
    startbrack=mynodevalue.find('{')
    endbrack=mynodevalue.find('}')
    metagdatastr=mynodevalue[startbrack+1:endbrack]
    mynodedata['nodelabel']=mynodevalue[0:startbrack]
    metadatalist=metagdatastr.split(',')
    for pair in metadatalist:
        mydata=pair.split('=',1)
        mynodedata[mydata[0]]=mydata[1]
    #print 'mynodedata'
    return mynodedata

def convertnodecollection(value):
    cleanvalue=stripws(value)
    mynodecollection=[]
    nodelist=cleanvalue.split(';')
    for nodedata in nodelist:
        mynodecollection.append(convertnodedata(nodedata))
    return mynodecollection



# python wrappers of cmscon commands
def exportIov(connect, tag, destination, passwd=""):
    exportIovCommand = 'export TNS_ADMIN=/afs/cern.ch/cms/DB/conddb; cmscond_export_iov -s %s -t %s -d %s' % (connect, tag, destination)
    #exportIovCommand = 'echo "export TNS_ADMIN=/afs/cern.ch/cms/DB/conddb; cmscond_export_iov -s %s -t %s -d %s"' % (connect, tag, destination)
    if passwd != 'None' and passwd != '':
        exportIovCommand += ' -P ' + passwd
    #print exportIovCommand
    statusAndOutput = commands.getstatusoutput(exportIovCommand)
    if statusAndOutput[0] != 0:
        print warning("Warning") + ": exportIov for tag: " + tag + " failed!"
        print exportIovCommand
        print statusAndOutput[1]

    return statusAndOutput

def listIov(connect, tag, passwd):
    """
    Interface to cmscond_list_iov command
    """

    listiovCommand = 'export TNS_ADMIN=/afs/cern.ch/cms/DB/conddb; cmscond_list_iov -c ' + connect + '  -t ' + tag
    # listiovCommand = 'setenv TNS_ADMIN /afs/cern.ch/cms/DB/conddb; cmscond_list_iov -c ' + connect + '  -t ' + tag
    # listiovCommand = 'cmscond_list_iov -c ' + connect + '  -t ' + tag
    if passwd != 'None' and passwd != '':
        listiovCommand = listiovCommand + ' -P ' + passwd
    statusAndOutput = commands.getstatusoutput(listiovCommand)
    if statusAndOutput[0] != 0:
        print warning("Warning") + ": listiov for tag: " + tag + " failed!"
        print listiovCommand
        print statusAndOutput[1]

    return statusAndOutput




def duplicateIovTag(connect, tag, newtag, passwd):
    """
    Interface to cmscond_load_iov. It lists the IOV and than load the txt file taking care of the cooking.
    NOTE: check carefully before using
    """
    statusAndOutput = listIov(connect,tag,passwd)

    if statusAndOutput[0] != 0:
        return statusAndOutput
    
    splitOutput = statusAndOutput[1].split("\n")
    #print splitOutput

    iovLoadFileName = '/tmp/'+ newtag + ".txt"
    iovLoadFile = open(iovLoadFileName, 'w')
    index = 0
    for line in splitOutput:
        if index == 0:
            iovLoadFile.write('Tag '+ newtag + '\n')            
        else:
            iovLoadFile.write(line+'\n')
        index = index + 1
    iovLoadFile.close()
    
    loadiovCommand = 'cmscond_load_iov -c ' + connect + ' ' + iovLoadFileName
    if passwd != 'None':
        loadiovCommand = loadiovCommand + ' -P ' + passwd

    loadiovStatusAndOutput = commands.getstatusoutput(loadiovCommand)
    if loadiovStatusAndOutput[0] != 0:
        print warning("Warning") + "  loadiov for tag: " + newtag + " failed!\n\n"
        print loadiovStatusAndOutput[1]
        return loadiovStatusAndOutput

    return loadiovStatusAndOutput

    
def duplicateIov(connect, tag, run, passwd):
    """
    Interface to cmscond_duplicate_iov command.
    """
    duplicateiovCommand = "cmscond_duplicate_iov -c " + connect + '  -t ' + tag + ' -f ' + run + ' -s ' + run
    if passwd != 'None':
        duplicateiovCommand = duplicateiovCommand + ' -P ' + passwd

    duplicateiovStatusAndOutput =  commands.getstatusoutput(duplicateiovCommand)
    if duplicateiovStatusAndOutput[0] != 0:
          print warning("Warning") + " duplicate iov for tag: " + tag + " and run " + run + " failed!\n\n"
          print duplicateiovStatusAndOutput[1]

    return duplicateiovStatusAndOutput
          
def truncateIov(connect, tag, passwd):
    """
    Interface to cmscond_truncate_iov command
    """
    truncateiovCommand = "cmscond_truncate_iov -c " + connect + '  -t ' + tag 
    if passwd != 'None':
        truncateiovCommand = truncateiovCommand + ' -P ' + passwd

    truncateiovStatusAndOutput =  commands.getstatusoutput(truncateiovCommand)
    if truncateiovStatusAndOutput[0] != 0:
          print warning("Warning") + " truncate iov for tag: " + tag + " failed!\n\n"
          print truncateiovStatusAndOutput[1]

    return truncateiovStatusAndOutput
          



def tagtreeList(globaltag, gtconnect, authpath):
    """
    Interface to cmscond_tagtree_list command
    """
    command = "export TNS_ADMIN=/afs/cern.ch/cms/DB/conddb; cmscond_tagtree_list -c " + gtconnect + " -T " + globaltag
    if authpath != "" and authpath != None:
         command += " -P " + authpath
    statusandoutput = commands.getstatusoutput(command)
    return statusandoutput


def gtExists(globaltag, gtconnect, authpath):
    """
    Given the GT name and connection string it checks for the existance of the GT table
    """
    statusandoutput = tagtreeList(globaltag, gtconnect, authpath)
    #print statusandoutput[1]
    if 'does not exist' in statusandoutput[1] or "identifier is too long" in statusandoutput[1]:
        return False
    return True

class GTEntry:
    """
    Object representing every single entry of the GT configuration file. In practice each GTEntry corresponds to an IOV tag.
    """
    def __init__(self):
        self._leafnode = ''
        self._parent = ''
        self._tag = ''
        self._object = ''
        self._pfn = ''
        self._account = ''
        self._record = ''
        self._connstring = ''
        self._label = ''
        # Update type: -1 unknown, 0 manual, 1 O2O
        self._updateType = -1
        return

    def record(self):
        """
        Return the record
        """
        return self._record

    def account(self):
        """
        Return the account
        """
        return self._account

    def setUpdateType(self, typeCode):
        """
        Set the tag type according to o2o or manual categorization.
        FIXME: this should be improved to the latest categorization by Marco...
        """
        if typeCode == "o2o":
            self._updateType = 1
        elif typeCode == "manual":
            self._updateType = 0
        else:
            self._updateType = -1

    def updateType(self):
        """
        Access the tag category (o2o or manual)
        """
        return self._updateType

    def tagName(self):
        """
        Return the tag name
        """
        return self._tag

    def __eq__(self, other):
        """
        Check for identity of the most important parameters 
        """
        return  self._leafnode == other._leafnode and self._parent == other._parent and self._tag == other._tag and self._object == other._object and self._pfn == other._pfn and self._account == other._account and self._record == other._record and self._connstring == other._connstring and self._label == other._label 


    def __str__(self):
        """
        Prints some minimal info about the tag
        """
        return 'tag: \'' + self._tag + "\' " + str(self.rcdID())

    def setFromTagInventoryLine(self, line):
        """
        Fill the properties directly from each entry in the 'TagInventory' section of the GT conf. file
        """
        self._tag = line['tagname']
        self._account = 'CMS_COND'+str(line['pfn']).split('/CMS_COND')[1]
        self._object = line['objectname']
        self._pfn = line['pfn']
        self._record = line['recordname']
        self._connstring = (line['pfn']).split('/CMS_COND')[0]
        if line.has_key('labelname'):
            self._label = line['labelname']
        return

    def setFromTagTreeLine(self, line):
        """
        Fill the properties directly from each entry in the 'TagTree' section of the GT conf. file
        """
        # check this is the right tag
        if line.has_key('tagname') is False:
            raise ValueError, "***Error: \'tagname\' is not specified for leaf node "+line['nodelabel']

        if line['tagname'] != self._tag:
            raise ValueError, "***Error: leaf: " + line['nodelabel'] + " is not for tag "+ self._tag

        self._leafnode = line['nodelabel']
        
        if not line.has_key('parent'):
            raise KeyError,'***Error: no parent parameter for'+line['nodelabel']
        self._parent = line['parent']
        return

    def setFromCfgLine(self, line):
        newrecorddata = stripws(line[1])
        newrecordcollection = convertnodedata(newrecorddata)
        self._tag = line[0]
        self._parent = 'Calibration'
        self._connstring =newrecordcollection['connect']
        self._account = newrecordcollection['account']
        self._object = newrecordcollection['objectname']
        self._record = newrecordcollection['recordname']
        self._leafnode = newrecordcollection['nodelabel']
        if newrecordcollection.has_key('labelname'):
            self._label = newrecordcollection['labelname']
        else :
            self._label = ''
        self._pfn = newrecordcollection['connect']+'/'+newrecordcollection['account']

        return

    def getCfgFormat(self):
        """ return the string in the same format used in the cfg file to add a new record to the GT """
        cfgstring = self._leafnode + '{recordname=' + self._record + ',connect=' + self._connstring + ',account=' + self._account + ',objectname=' + self._object
        if not self._label == '':
            cfgstring = cfgstring + ',labelname=' + self._label
        cfgstring = cfgstring + '}'
        return cfgstring

    def printTag(self):
        print 'Tag: ' + self._tag
        return

    def getTagInvetoryLine(self):
        outline = str
        if self._label != '':
            outline = ' '+self._tag+'{pfn='+self.pfn()+',objectname='+self._object+',recordname='+self._record+',labelname='+self._label+'}'
        else:
            outline=' '+self._tag+'{pfn='+self.pfn()+',objectname='+self._object+',recordname='+self._record+'}'
        return outline

    def getTagTreeLine(self):
        outline=' '+ self._leafnode+'{parent='+ self._parent+',tagname='+ self._tag+',pfn='+ self.pfn()+'}'
        return outline

    def rcdID(self):
        """
        Retunrs a RcdId object 
        """
        return RcdID([self._record,self._label])

    def setConnect(self, newconn):
        self._connstring = newconn
        self._pfn = self._connstring+'/'+ self._account
        return

    def setAccount(self, account):
        self._account = account
        self._pfn = self._connstring+'/'+ self._account
        return

    def setTagName(self, newtag):
        self._tag = newtag
        return

    def setEntry(self, tagname, parent, connect, account, object, record, leaf, label):
        self._tag = tagname
        self._parent = parent
        self._connstring = connect
        self._account = account
        self._object = object
        self._record = record
        self._leafnode = leaf
        self._label = label
        self._pfn = connect+'/'+record

        return

    
    def getOraclePfn(self, online):
        """
        Converts the frontier connection strin to the oracle one
        """
        if online == False:
            if self._connstring == 'frontier://FrontierPrep':
                oracleConn =  'oracle://cms_orcoff_prep'
            elif self._connstring == 'frontier://FrontierInt':
                oracleConn =  'oracle://cms_orcoff_int'
            elif self._connstring == 'frontier://FrontierArc':
                # no change is needed since it is anyhow frozen
                oracleConn =  'frontier://FrontierArc'
            else:
                # oracleConn =  'oracle://cms_orcoff_prod'
                oracleConn =  'oracle://cms_orcon_adg'

        elif online == True:
            if self._connstring == 'frontier://FrontierProd':
                # oracleConn =  'oracle://cms_orcon_prod'
                oracleConn =  'oracle://cms_orcon_adg'
            elif self._connstring == 'frontier://FrontierPrep':
                oracleConn =  'oracle://cms_orcoff_prep'

        return oracleConn + '/' + self._account

    def isInPrepAccount(self):
        """
        Check if the tag is in a Prep account
        """
        if self._connstring == 'frontier://FrontierPrep' or self._connstring == 'frontier://FrontierInt' :
            return True
        return False

    def isOnlineConnect(self):
        """
        Check for online like connection strings
        """
        if self._connstring == 'frontier://(proxyurl=http://localhost:3128)(serverurl=http://localhost:8000/FrontierOnProd)(serverurl=http://localhost:8000/FrontierOnProd)(retrieve-ziplevel=0)(failovertoserver=no)':
            return True
        return False

    def pfn(self):
        """
        Returns the full pfn (connection + account) string
        """
        if '.db' in self._connstring:
            return self._connstring
        return  self._connstring + "/" + self._account


class RcdID(tuple):
    """
    Tuple of Record + label used to index the GTEntries in the GT
    """
    def __new__(cls, *args, **kw):
        return tuple.__new__(cls, *args, **kw)

    def __str__(self):
        return "rcd: \'" + tuple.__getitem__(self,0) + "\' label: \'" + tuple.__getitem__(self,1) + "\'"




class IOVEntry:
    def __init__(self, timetype = "runnumber"):
        self._since = -1
        self._till = -1
        self._payloadToken = ""
        self._timeType = timetype


    def setSince(self, newSince):
        self._since = newSince

    def setTill(self, newTill):
        self._till = newTill

    def setToken(self, newToken):
        self._payloadToken = newToken

    def setTimeType(self, newTimeType):
        self._timeType = newTimeType
    

    def setFromListIOV(self, line, timetype = "runnumber"):
        listofentries = line.split()
        # print "listofentries =", listofentries
        if self._timeType == 'timestamp':
            self._since = int(listofentries[0])
            self._till = int(listofentries[3])
            if self._till != 18446744073709551615:
                self._payloadToken = listofentries[6]
            else:
                self._payloadToken = listofentries[5]
        elif self._timeType == 'lumiid':
            self._since = int(listofentries[0])
            self._till = int(listofentries[3])
            self._payloadToken = listofentries[6]
        else:
            # print "since =", listofentries[0]
            # print "till =", listofentries[1]
            # print "payloadToken =", listofentries[2]
            self._since = int(listofentries[0])
            self._till = int(listofentries[1])
            self._payloadToken = listofentries[2]
            
        return

    def __str__(self):
        if self._timeType == "runnumber":
            return str(self._since) + '\t' + str(self._till) + '\t' + self._payloadToken
        elif self._timeType == "lumiid":
            return str(self._since) + ' (' + str(self.sinceRL()[0]) + ":" + str(self.sinceRL()[1]) + ')\t'+str(self._till)+ ' (' + str(self.tillRL()[0]) + ":" + str(self.tillRL()[1]) + ')\t'+self._payloadToken
        elif self._timeType == "timestamp":
            if self._till != 18446744073709551615:
                till = timeStamptoDate(self._till)
            else:
                till = 'inf'
            return str(self._since) + ' (' + str(timeStamptoDate(self._since)) + ')\t'+str(self._till)+ ' (' + till + ')\t'+self._payloadToken

    def sinceDate(self):
        return datetime.strptime(timeStamptoDate(self._since),"%a %b %d %H:%M:%S  %Y")

    def tillDate(self):
        return datetime.strptime(timeStamptoDate(self._till),"%a %b %d %H:%M:%S  %Y")

    def since(self):
        return self._since

    def till(self):
        return self._till

    def token(self):
        return self._payloadToken

    def timeType(self):
        return self._timeType

    
    def sinceRL(self):
        return self.unpackLumiid(self.since())

    def tillRL(self):
        return self.unpackLumiid(self.till())

    def sinceR(self):
        if self._timeType == "runnumber":
            return self._since
        elif self._timeType == "lumiid":
            return self.sinceRL()[0]

    def tillR(self):
        if self._timeType == "runnumber":
            return self._till
        elif self._timeType == "lumiid":
            return self.tillRL()[0]

        
    def unpackLumiid(self, lumiid):
        kLowMask = 0XFFFFFFFF
        run = lumiid >> 32
        lumi = lumiid & kLowMask
        return (run, lumi)


#      ===========================================================
#      Tag: XMLFILE_Geometry_44YV1_Ideal_mc
#              ===========================================================
#              TimeType: runnumber
#                      Since         Till          Payload token  Payload Class
#                              ------------  ------------  -------------  ----------------
#                                                 1    4294967295  0007-0000000A          FileBlob

#                                                         Total # of payload objects: 1
                                                        


class IOVTable:
    def __init__(self):
        self._iovList = []
        self._tagName = ""
        self._timeType = ""
        self._containerName = ""
        return

    def timeType(self):
        return self._timeType

    def containerName(self):
        return self._containerName

    def addIOVEntry(self, entry):
        # print "Add IOV : " + str(entry)
        self._iovList.append(entry)

    def timeType(self):
        return self._timeType
    

    def setFromListIOV(self, listiovOutput):
        listiovlines  = listiovOutput.split('\n')
        nLines = len(listiovlines)
        for line in listiovlines:
            if "=========" in line or "------------" in line:
                continue
            linewords = line.split()
            if len(linewords) != 0:
                #print line
                if 'Tag' in linewords[0]:
                    self._tagName = linewords[1]
                elif 'TimeType' in linewords[0]:
                    self._timeType = linewords[1]
                elif 'PayloadContainerName' in linewords[0]:
                    self._containerName = linewords[1]

                    
        #print self._tagName
        for line in range(6, nLines-1):
            # print "listiovlines =", listiovlines[line]
            # if "Since" in listiovlines[line] or "------------" in listiovlines[line] or listiovlines[line] == "":
            if "Since" in listiovlines[line] or "------------" in listiovlines[line] or listiovlines[line] == "" or "TimeType" in listiovlines[line]:
                continue
            # print "after continue listiovlines =", listiovlines[line]
            ioventry = IOVEntry(self._timeType)
            if self._containerName == "":
                items = listiovlines[line].split()
                self._containerName = items[len(items)-1]
            ioventry.setFromListIOV(listiovlines[line])
            self.addIOVEntry(ioventry)


    def checkConsitency(self, tagType):
        if tagType == "mc":
            if len(self._iovList) != 1:
                print warning("***Warning") + " MC tag: " + self._tagName + " contains: " + str(len(self._iovList)) + " IOVs"
            else:
                if self._iovList[0].since() != 1 or self._iovList[0].till() != 4294967295:
                    print warning("***Warning") + " MC tag: " + self._tagName + " has IOV: " + str(self._iovList[0])
        elif tagType == "data":
            if self._iovList[0].sinceR() != 1 or self._iovList[len(self._iovList) - 1].tillR() != 4294967295:
                print warning("***Warning") + " data tag: " + self._tagName + " is not covering the whole range 1 - inf"
                #self.printList()
                return
            if len(self._iovList) != 1:
                for index in range(0, len(self._iovList)-1):
                    if (self._iovList[index+1].sinceR() - self._iovList[index].tillR()) > 1:
                        print warning("***Warning") + " data tag: " + self._tagName + " has an hole in the IOVs:"
                        print self._iovList[index]
                        print self._iovList[index+1]
                        #self.printList()
                        return

    def printList(self):
        print "Tag " + self._tagName
        print "TimeType " + self._timeType
        print "PayloadContainerName " + self._containerName
        print "since    till    payloadToken"
        for iov in self._iovList:
            print iov
        print "Total # of payload objects: " + str(len(self._iovList))
        return
    
        
    def lastIOV(self):
        return  self._iovList[len(self._iovList)-1]

    def size(self):
        return len(self._iovList)

    def search(self, since, iov):
        hi = self.size()
        lo = 0
        while lo < hi:
            mid = (lo+hi)//2
            midval = self._iovList[mid]
            if midval.since() < since:
                lo = mid+1
            elif midval.since() > since:
                hi = mid
            else:
                #iov = midval
                iov.setSince(midval.since())
                iov.setTill(midval.till())
                iov.setToken(midval.token())
                iov.setTimeType(midval.timeType())
                #print midval
                return True
        return False


class GTEntryCollection:
    """This is a collection of globalTag entries ('GTEntries') and as such it represents an entire global tag.
    It contains all the needed information and can be used to read a GT and loop over it.
    See in gtCompare.py for an example on how to use it."""
    def __init__(self):
        # the actual list of GTEntries
        self._tagList = []
        # mapping by tag: this is a dictionary of the actual idexes of _tagList organized by 'tag'
        self._tagByTag = dict()
        # mapping by record-label: this is a dictionary of the actual indexes of _tagList organized by 'rcdId'
        self._tagByRcdAndLabelId = dict()
        # keeps track of the order in the conf file
        # FIXME: this is useless. I would actually change the whole phylosophy ordering all the entries by account before the .conf file is written....
        self._tagOrder = []
        # bookmarks account to create indexes for new insertions
        self._previousaccount = str()
        # maps the last position for each account to be used for new insertions
        self._accountindexes = dict()
        # global subfix for all accounts
        self._glbAccSubfix = ''
        # list of tags in the prep-account
        self._tagsInPrep = []
        # list of new/modified tags
        self._newTags = []
        self._node = ''
        self._root = ''
        self._parent = ''
        return

    def size(self):
        """
        Returns the size (= # of entries) of the GT
        """
        return len(self._tagOrder)
    
    def nodedata(self):
        """
        Returns the 'node' atribute of the TAGTREE. This is currently fixed for all GTs.
        """
        return  self._node

    def root(self):
        """
        Returns the 'root' atribute of the TAGTREE. This is currently fixed for all GTs
        """
        return self._root

    def parent(self):
        """
        Returns the 'parent' atribute of the TAGTREE. This is currently fixed for all GTs.
        """
        return self._parent

    def setNodedata(self, node):
        """
        Set the 'node' atribute of the TAGTREE. This is currently fixed for all GTs.
        """
        self._node = node

    def setRoot(self, root):
        """
        Set the 'root' atribute of the TAGTREE. This is currently fixed for all GTs
        """
        self._root = root

    def setParent(self, parent):
        """
        Set the 'parent' atribute of the TAGTREE. This is currently fixed for all GTs.
        """
        self._parent = parent
    
    def addEntry(self, tag):
        """
        Insert a new GTEntry in the collection.
        The ENTRY is not added if the same tag or the same RcdId are already in the GT.
        """
        # check that the tagname and/or the rcdId are not yet in the collection
        if tag._tag in self._tagByTag or tag.rcdID() in self._tagByRcdAndLabelId:
            print error("***Error"),"adding entry:", tag
            othertagid = -1
            if tag._tag in self._tagByTag:
                othertagid = self._tagByTag[tag._tag]
            else:
                othertagid = self._tagByRcdAndLabelId[tag.rcdID()]
                
            print "     same tag or Record for: ",self._tagList[othertagid]
            print ""
            raise ValueError, "***Error: entry has same tag or RcdId than another one in the collection!" 

        # Actually add the GTEntry to the _tagList
        self._tagList.append(tag)
        # Save the index to use it in the various dictionaries to retrieve the entry by tag/by Rcdid and to preserve the order
        index = len(self._tagList) - 1
        self._tagByTag[tag._tag] = index
        self._tagByRcdAndLabelId[tag.rcdID()] = index
        self._tagOrder.append(index)
        # keep the list of tags in the prep-accounts
        if tag.isInPrepAccount():
            self._tagsInPrep.append(index)
        # try to order by account. FIXME: can probably be removed to simplify
        # self._newTags.append(index)
        # check where to append the new records
        if tag._account != self._previousaccount:
            # print "Prev account: " + self._previousaccount
            if not self._previousaccount in self._accountindexes:
                if index != 1:
                    self._accountindexes[self._previousaccount] = index - 1
                    # print "Account: " + self._previousaccount + " index: " + str(index - 1)
            self._previousaccount = tag._account

        return

    def getByTag(self, tag):
        """
        Returns the 'GTEntry' matching the 'tag' name in input
        """
        return self._tagList[self._tagByTag[tag]]

    def getByRcdID(self, id):
        """
        Returns the 'GTEntry' matching the RcdId in input
        """
        return self._tagList[self._tagByRcdAndLabelId[id]]

    def hasTag(self, tag):
        return tag in self._tagByTag

    def hasRcdID(self, anid):
        return anid in self._tagByRcdAndLabelId

    def modifyEntryTag(self, oldtag, newtag):
        if self.hasTag(oldtag):
            if newtag in  self._tagByTag:
                raise ValueError, "***Error: replacing tag " + oldtag + " with tag: " + newtag + "already in the collection!" 
            index = self._tagByTag[oldtag]
            self.getByTag(oldtag)._tag = newtag
            print "   " + oldtag + ": " + newtag
            self._tagByTag[newtag] = index
            if not index in self._newTags:
                # print "oldtag = " + oldtag + ", newtag = " + newtag + ", index =", index
                self._newTags.append(index)
        else:
            print error("*** Warning") + " tag: " + oldtag + " not found!"
        return

    def modifyEntryConnection(self, tag, connection):
        if self.hasTag(tag):
            index = self._tagByTag[tag]
            if connection == 'frontier://FrontierPrep' and not self.getByTag(tag).isInPrepAccount():
                self._tagsInPrep.append(index)

            if  connection != 'frontier://FrontierPrep' and self.getByTag(tag).isInPrepAccount():
                self._tagsInPrep.remove(index)

            if not index in self._newTags:
                # print "newtag = " + tag + ", index =", index
                self._newTags.append(index)
            self.getByTag(tag).setConnect(connection)
            print "   " + tag + ": " + connection
                
        else:
            print error("*** Warning") + " tag: " + tag + " not found!"
        return

    def modifyEntryAccount(self, tag, account):
        if self.hasTag(tag):
            self.getByTag(tag).setAccount(account)
            index = self._tagByTag[tag]

            if not index in self._newTags:
                # print "modifyEntry: newtag = " + tag + ", index =", index
                self._newTags.append(index)
            print "   " + tag + ": " + account
        else:
            print error("*** Warning") + " tag: " + tag + " not found!"

        return

    def replaceEntry(self, entry):
        if self.hasRcdID(entry.rcdID()) == False:
            raise ValueError, "***Error: replaceEntry called for " + str(entry.rcdID()) + " not in the collection"
        # FIXME: check that the tag is not already the same as in the tag collection
        if entry == self.getByRcdID(entry.rcdID()):
            # print "tag: " + entry._tag + " already in!"
            return
        print "  ", self.getByRcdID(entry.rcdID())._tag+ ": ", entry._tag
        index = self._tagByRcdAndLabelId[entry.rcdID()]
        # get the leaf name from the previous one
        entry._leafnode = self._tagList[index]._leafnode
        entry._parent = self._tagList[index]._parent

        if entry.isInPrepAccount() and not self._tagList[index].isInPrepAccount():
            self._tagsInPrep.append(index)

        if not entry.isInPrepAccount() and self._tagList[index].isInPrepAccount():
            self._tagsInPrep.remove(index)

        # reassing this entry
        self._tagList[index] = entry
        self._tagByTag[entry._tag] = index

        if not index in self._newTags:
            # print "replaceEntry tag = " + entry._tag + ", index =", index
            self._newTags.append(index)

        
        return

    def insertEntry(self, entry):
        """
        Given a 'GTEntry' it will add it to the collection if the rcdId is new or replace the needed attributes if the RcdId already exists.
        """
        # check if the RcdId is already in the GT
        if self.hasRcdID(entry.rcdID()) == True:
            # only replace selected attributes
            self.replaceEntry(entry)
        else:
            # this is a brand new RcdId: needs to be added to the _tagList
            index = len(self._tagList)
            # print "tagList: " + str(index)
            if entry._account in self._accountindexes:
                # append to the other tags of thsi account
                index = self._accountindexes[entry._account]
                # print "Account: "+ entry._account + " Index: " + str(index)
                # print "Account" + str(index)
            self._tagList.append(entry)
            listindx = len(self._tagList) - 1
            self._tagByTag[entry._tag] = listindx
            self._tagByRcdAndLabelId[entry.rcdID()] = listindx
            self._tagOrder.insert(index+1, listindx)

            if entry.isInPrepAccount():
                # self._tagsInPrep.append(index)
                self._tagsInPrep.append(listindx)

            # print "index =", index
            # print "listindx =", listindx
            # self._newTags.append(index)
            self._newTags.append(listindx)
            print "   new entry -> " + str(entry) + ", index = " + str(index)
            # rearrange (=increment) the other account indexes if > index
            for accIndex in sorted(self._accountindexes.items(), key=itemgetter(1)):
                if accIndex[1] >= index:
                    self._accountindexes[accIndex[0]] = accIndex[1]+1
                    # print "           -> account: " + accIndex[0] + " moved to : " + str(self._accountindexes[accIndex[0]])
        return

    def removeEntry(self, rcdId):
        if self.hasRcdID(rcdId) == False:
            print warning("*** Warning:") + " rm entry: " +  str(rcdId) + " not in the collection!"
            return
        print "   " + str(rcdId)
        listindx = self._tagByRcdAndLabelId[rcdId]
        index = self._tagOrder.index(listindx)
        self._tagOrder.remove(listindx)
        # rearrange (=decrement) the other account indexes if > index
        for accIndex in sorted(self._accountindexes.items(), key=itemgetter(1)):
            if accIndex[1] >= index:
                self._accountindexes[accIndex[0]] = accIndex[1]-1
        #remove it from the list of tags in prep account
        if listindx in self._tagsInPrep:
            self._tagsInPrep.remove(listindx)
                
        return

    def addAccountSubfix(self, subfix):
        print "Appending account subfix: " + subfix
        for entry in self._tagList:
            entry.setAccount(entry._account + subfix)

        # FIXME: should fix self._accountindexes
        # for oldtag, newtag in replacetags.iteritems():
        # tagCollection.modifyEntryTag(oldtag, newtag)
        return

    
    def glbConnectReplace(self, newconnect):
        print "Force new connect: " + newconnect
        for entry in self._tagList:
            entry.setConnect(newconnect)
        return

    def printTagsInPrep(self):
        if len(self._tagsInPrep) != 0:
            print "***Warning: the following " + str(len(self._tagsInPrep)) + " tags are read form preparation or integration account:"
        for idx in self._tagsInPrep:
            tag = self._tagList[idx] 
            print "   tag:", tag.tagName()," obj: ",tag._object," account: ",tag._account
            
    
    def tagsInPrep(self):
        if len(self._tagsInPrep) != 0:
            return True

    def dumpToConfFile(self, newconffile, newgt, gtaccount,sqlite=''):
        # --------------------------------------------------------------------------
        # Write the new conf file
        node = self.nodedata()
        root = self.parent()
        globparent = self.root()

        # open output conf file
        conf=open(newconffile,'w')
        conf.write('[COMMON]\n')
        print sqlite
        if sqlite == '':
            conf.write('connect=sqlite_file:' + newgt + '.db\n')
        else:
            conf.write('connect=' + sqlite + '\n')
        #conf.write('#connect=oracle://cms_orcoff_int2r/'+ACCOUNT+'\n')
        conf.write('#connect=oracle://cms_orcon_prod/'+gtaccount+'\n')
        conf.write('\n')
        conf.write('[TAGINVENTORY]\n')
        conf.write('tagdata=\n')
        for tagidx in range(0,len(self._tagOrder)):
            outline = self._tagList[self._tagOrder[tagidx]].getTagInvetoryLine()
            if tagidx != len(self._tagOrder) - 1:
                outline=outline+';'
            outline=outline+'\n'
            conf.write(outline)

        conf.write("\n")

        conf.write('[TAGTREE '+newgt+']\n')

        conf.write('root='+root+'\n')
        conf.write('nodedata='+node+'{parent='+globparent+'}\n')
        conf.write('leafdata=\n')
        #counter = 0
        for tagidx in range(0,len(self._tagOrder)):
            outline = self._tagList[self._tagOrder[tagidx]].getTagTreeLine()
            #counter = counter + 1
            if tagidx != len(self._tagOrder) - 1:
                outline=outline+';'
            outline=outline+'\n'
            conf.write(outline)

        conf.close()





class GTDocGenerator:
    def __init__(self, gtName, oldGT, scope, release, changelog):
        self._listTagLink = '%LINKTOGTLIST%/?GlobalTag=' + gtName
        self._gt = gtName
        self._oldGt = oldGT
        self._scope = scope
        self._release = release
        self._change = changelog
        self._isForProd = True
        
    def isForProd(self, isForProd):
        self._isForProd = isForProd

    def wikiString(self):
        wikiString =  '| [[' + self._listTagLink + '][' + self._gt + ']] | %GREEN%' + self._release + '%ENDCOLOR%'
        if self._isForProd == False:
            wikiString = wikiString + ' %RED%(Not for prod.[[[#NOTENotProd][1]]])%ENDCOLOR%'
        wikiString = wikiString + ' | ' + self._scope  + ' | As !' + self._oldGt + ' with the following updates:' + self._change + '. |\n'
        return wikiString

    def printWikiDoc(self):
        if not os.path.exists('doc/'):
            print " directory \"doc\" doesn't exist: creating it"
            os.mkdir('doc/')
        docfilename = 'doc/' + self._gt + '.wiki'
        docfile = open(docfilename,'w')
        docstring = self.wikiString()
        docfile.write(docstring)
        docfile.close()

#     def printWikiDoc(self, fileName):
#         if not os.path.exists('doc/' + fileMame):
#             print " directory \"doc\" doesn't exist: creating it"
#             os.mkdir('doc/')
#         docfilename = 'doc/' + fileName

#         fileread = open(docfilename,'r')
#         temp = fileread.read()
#         fileread.close()
#         docfile = open(docfilename,'w')
#         docstring = self.wikiString()
#         docfile.write(docstring)
#         docfile.write(temp)
#         docfile.close()
#         cvsCommit(docfilename, self._gt)


    def addChange(self, change):
        if not change in self._change:
            self._change = self._change + '<br> - ' + change

    def snapshotValidity(self, date, lastrun = -1):
        self._scope = self._scope + "<br>%RED%(Snapshot not valid for runs > "
        if lastrun != -1:
            self._scope = self._scope + str(lastrun) + " [= " + str(date) + "]"
        else:
            self._scope = self._scope + str(date)
        self._scope = self._scope + ")%ENDCOLOR%[[[#NOTESnapValid][2]]]"

    def addToBranchList(self, branch):
        fileName = "GT_branches/GTDoc/Class.list"
        cvsUpdate(fileName)
        temp = ""
        if  os.path.exists(fileName):
            fileToRead = file(fileName, 'r')
            temp = fileToRead.read()
            fileToRead.close()

        if not self._gt + ":" in temp:
            fileToWrite = file(fileName, 'a')
            fileToWrite.write(self._gt + ": " + branch + "\n")
            fileToWrite.close()
            cvsCommit(fileName, self._gt)

def confFileFromDB(gt, gtConfFileName, gtConnString, authpath):
    # check if the original conf file exists
    if not os.path.isfile(gtConfFileName):
        # get the conf file from DB
        print "Getting the conf file for GT: " + gt + " from DB....be patinet!"
        dbtoconf_cfg = ConfigParser()
        dbtoconf_cfg.optionxform = str
        dbtoconf_cfg.add_section("Common")
        dbtoconf_cfg.set("Common","Account","CMS_COND_31X_GLOBALTAG")
        #dbtoconf_cfg.set("Common","Conn_string_gtag","frontier://cmsfrontier:8000/FrontierProd/CMS_COND_31X_GLOBALTAG")
        dbtoconf_cfg.set("Common","Conn_string_gtag",gtConnString)
        dbtoconf_cfg.set("Common","AuthPath",authpath)
        dbtoconf_cfg.set("Common","Globtag",gt)
        dbtoconf_cfg.set("Common","Confoutput",gtConfFileName)
        dbtoconf_file = open("dbtoconf.cfg", 'wb')
        dbtoconf_cfg.write(dbtoconf_file)
        dbtoconf_file.close()

        #dbtoconf_cmd = 'eval `scram runtime -csh`; dbtoconf.py'
        dbtoconf_cmd = 'dbtoconf.py'

        statusAndOutput = commands.getstatusoutput(dbtoconf_cmd)
        if statusAndOutput[0] != 0:
            print statusAndOutput[1]

        # check again
        if not os.path.isfile(gtConfFileName):
            return False

    return True


def fillGTCollection(gtConfFileName, gtName, gtEntryCollection):

    # parse the config file and fill the collection
    configparser=ConfigParser()
    configparser.read(gtConfFileName)
    data=stripws(configparser.get("TAGINVENTORY",'tagdata'))
    tagcollection=converttagcollection(data)

    # parse the tag inventory
    if len(tagcollection)!=0:
        for item in tagcollection:
            # create the tag object and populate it
            tag = GTEntry()
            tag.setFromTagInventoryLine(item)
            # set the update category if present
            if configparser.has_option('UpdateType', tag.tagName()):
                tag.setUpdateType(configparser.get('UpdateType', tag.tagName()))
            gtEntryCollection.addEntry(tag)

    # --------------------------------------------------------------------------
    # parse the tag tree
    treesection=' '.join(['TAGTREE', gtName])

    nodecollection = []
    if configparser.has_option(treesection, 'nodedata'):
        nodedata=stripws(configparser.get(treesection,'nodedata'))
        nodecollection=convertnodedata(nodedata)

    # FIXME not dinamically read from 
    gtEntryCollection.setNodedata('Calibration')
    gtEntryCollection.setParent('All')
    root=stripws(configparser.get(treesection,'root'))
    gtEntryCollection.setRoot(root)
    if configparser.has_option(treesection, 'leafdata'):
        leafdata=stripws(configparser.get(treesection,'leafdata'))
        leafcollection=convertnodecollection(leafdata)
    if len(leafcollection)!=0:
        for leafdata in leafcollection:
            # print 'again ',myleaf.nodelabel
            if leafdata.has_key('tagname') is False:
                raise ValueError, "tagname is not specified for the leaf node "+leafdata['nodelabel']
            tag = gtEntryCollection.getByTag(leafdata['tagname'])
            tag.setFromTagTreeLine(leafdata)


def cvsUpdate(filename):
    #print "cvs update " + filename
    # cvs update 
    outandstat = commands.getstatusoutput("cvs update -A " + filename)
    if outandstat[0] != 0:
        print outandstat[1]

def cvsCommit(filename, comment):
    #print "cvs commit " + filename
    outandstat = commands.getstatusoutput('cvs commit -m "' + comment + '" ' + filename)
    if outandstat[0] != 0:
        print outandstat[1]


# given a release cycle like 38X extracts the single digits
def getReleaseDigits(cycle):
    #print release
    firstDigi = cycle[0]
    secondDigi = cycle[1:].rstrip('X')
    digits = []
    digits.append(firstDigi)
    digits.append(secondDigi)
    #print digits
    return digits

# get the list of releases (and correspondig AFS directory) installed through scram list
# relType can be all - pre - final - nightly - patch
def getReleaseList(swScramArch, relType = 'all'):
    releases = []

    scram_cmd = 'export SCRAM_ARCH=' + swScramArch + '; scram list -c CMSSW'
    scram_out = commands.getstatusoutput(scram_cmd)

    for line in scram_out[1].splitlines():
        #print "Linea: " + line
        onerel = line.split()[1]
        oneDir = line.split()[2]

        relAndArea = onerel, oneDir

        if 'all' in relType:
            releases.append(relAndArea)
            continue
        if 'pre' in relType and 'pre' in onerel:
            releases.append(relAndArea)
            continue
        if 'final' in relType and not 'pre' in onerel and not "_X_" in onerel and not 'patch' in onerel:
            releases.append(relAndArea)
            continue
        if 'patch' in relType and 'patch' in onerel:
            releases.append(relAndArea)
            continue
        if 'nightly' in relType and "_X_" in onerel:
            releases.append(relAndArea)
            continue
    return releases


# given a list of releaseases extracts the last one in a given cycle
def getLastRelease(releases, cycle):
    digits = getReleaseDigits(cycle)

    match = 'CMSSW_' + digits[0] + '_' + digits[1] + '_'


    maxDate = datetime(1979,10,06,9,0,0)
    maxThirdDigits = -1
    maxPreDigits = -1
    maxPatchDigits = -1
    maxRel = None, None
            
    for relAndArea in releases:
        onerel = relAndArea[0]
        if match in onerel and not "ONLINE" in onerel:
            # nigtly builds
            if "_X_" in onerel:
                #print 'Nightly: ' + onerel
                datestring = onerel.split("_X_")[1]
                datedigits = datestring.split('-')
                nightlyDate = datetime(int(datedigits[0]),int(datedigits[1]),int(datedigits[2]),int(datedigits[3].lstrip('0').rstrip('00')),0,0)
                if nightlyDate > maxDate:
                    maxDate = nightlyDate
                    maxRel = relAndArea

            # pre releases, reelases and patches
            # final releases, prerelease and patches
            else:
                digis = onerel.split('_')
                thirdDigits = int(digis[3])
                #print thirdDigits
                if thirdDigits >= maxThirdDigits:
                    if thirdDigits > maxThirdDigits:
                        maxThirdDigits = thirdDigits
                        maxPatchDigits = -1
                        maxPreDigits = -1
                    if not "pre" in  onerel:
                        if 'patch' in onerel:
                            patchDigits = int(digis[4].lstrip('patch'))
                            if patchDigits > maxPatchDigits:
                                maxPatchDigitsRel = patchDigits
                                maxRel = relAndArea
                        else:
                            maxRel = relAndArea
                    else:
                        if len(digis[4].lstrip('pre')) > 2:
                            continue
                        preDigits = int(digis[4].lstrip('pre'))
                        if preDigits > maxPreDigits:
                            maxPreDigits = preDigits
                            maxRel = relAndArea
    return maxRel



# look for plugin definitions in the so libraries ad fills a dictionary
# of lists of records where the key is the object
def getObjectsAndRecords(swScramArch, release):
    from collections import defaultdict

    objectRecords = defaultdict(list)
    libDir = release[1] + "/lib/" + swScramArch + "/"
    libraries =  os.listdir(libDir)
    for lib in libraries:
        if "pluginCondCore" in lib and "Plugins.so" in lib:
            #print libDir + lib
            # run nm to get the DataProxy plugin name
            nm_cmd = "nm -C " + libDir + lib + '| grep "vtable for DataProxy<" '
            nm_out = commands.getstatusoutput(nm_cmd)
            if nm_out[0] == 0:
                # parse the output
                dataproxies = nm_out[1].split('\n')
                for dataproxy in dataproxies:
                    preamble = dataproxy.split("DataProxy")
                    rcd = (dataproxy.lstrip(preamble[0] + "DataProxy").lstrip("<")).split()[0].rstrip(",")
                    if rcd == "DTKeyedConfigListRcd" or rcd == "DTKeyedConfigContainerRcd":
                        print dataproxy
                    objectName = dataproxy.split(rcd + ", ")[1].rstrip(">").rstrip(" ")

#                     if objectName == "EcalCondObjectContainer<float":
#                         objectName = "EcalFloatCondObjectContainer"
#                     elif objectName == "ESCondObjectContainer<ESPedestal":
#                         objectName = "ESPedestal"
#                     elif objectName == "ESCondObjectContainer<ESChannelStatusCode":
#                         objectName = "ESChannelStatus"
#                     elif objectName == "ESCondObjectContainer<EcalMGPAGainRatio":
#                         objectName = "EcalGainRatios"
#                     elif objectName == "ESCondObjectContainer<EcalTPGPedestal":
#                         objectName = "EcalTPGPedestals"
#                     elif objectName == "ESCondObjectContainer<EcalTPGPedestal":
#                         objectName = "EcalChannelStatus"

#                     elif objectName == "PhysicsTools::Calibration::Histogram3D<double":
#                         objectName = "PhysicsTools::Calibration::HistogramD3D"

                    #elif 

                    objectRecords[objectName].append(rcd)
                #print nm_out[1]
    return objectRecords
