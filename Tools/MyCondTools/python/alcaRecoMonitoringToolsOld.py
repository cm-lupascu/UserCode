import Tools.MyCondTools.tableWriter as tableWriter
import commands
import os
import datetime
from ROOT import *

"""
Module providing utils for the monitoring of AlcaReco production

$Date: 2013/01/29 10:49:06 $
$Revision: 1.5 $
Author: G.Cerminara

"""

def PDNameFilter(pdName,match):
    if match in pdName:
        return True
    return False
    
def PDFilterOutPromptSkim(pdName):
    if not PDNameFilter(pdName, "PromptSkim"):
        return True
    return False


class AlcaRecoDetails:
    """
    Simple structure to stores the details about the AlcaReco dataset: epoch, pd, version and dataset name
    """
    def __init__(self, dataset, pd, epoch, version):
        
        self._datasetname = dataset
        self._epoch = epoch
        self._version = version
        self._pd = pd
        # FIXME: divide in Short and long name
        self._shortname = dataset.split('/')[2].split('-'+ self._version)[0].split( self._epoch + '-')[1]
        print self._shortname

    def dataset(self):
        return self._datasetname

    def epoch(self):
        return self._epoch

    def name(self):
        return self._shortname

    def pd(self):
        return self._pd


class WebPageIndex:
    """
    Generates the index page pointing to all the sub-pages for each datataking period
    (correspondig to a particular epoch/version fo the RAW dataset.

    The list of sub-pages is generated directly scanning the web area and is based on a precise namign convention.
    """
    def __init__(self):
        self._epochs = []
        self._versions = []
        self._filenames = []

    def scan(self, dir):
        """
        Scans the web area looking for sub-pages for the different data-taking periods.
        All the HTML pages are added.
        """
        dirlist = os.listdir(dir)
        for fname in dirlist:
            if ".html" in fname and fname != 'index.html' and not '~' in fname:
                self._filenames.append(fname)
                namesplit = fname.split('.')[0].split('-')
                print namesplit
                self._epochs.append(namesplit[0])
                if len(namesplit) == 3:
                    self._versions.append(namesplit[1] + "-" + namesplit[2])
                else:
                    self._versions.append(namesplit[1])

    def buildPage(self):
        """
        Actually writes the HTML page (index.html)
        """
        htmlpage = file('index.html',"w")
        htmlpage.write('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">\n')
        htmlpage.write('<html><head>\n')
        htmlpage.write('<link rel="stylesheet" type="text/css" href="./PromptCalibMonitoring.css">\n')
        htmlpage.write('<title>Monitoring of AlCaReco Production</title>\n')
        htmlpage.write('</head>\n')
        htmlpage.write('<body>\n')
        htmlpage.write('<center><h1>Monitoring of AlCaReco Production</h1></center>\n<hr>\n')
        htmlpage.write('<p>\n')
        htmlpage.write('<center><table width="40%"><tr><td><b>Data acquisition Era</b></td><td><b>Processing version<b></td><td><b>Link to plots</b></td></tr>\n')
        for index in range(0, len(self._filenames)):
            htmlpage.write('<tr><td>' + self._epochs[index] + '</td><td>' + self._versions[index] +
                           '</td><td><a href=./' + self._filenames[index] + '>plots</a></td></tr>\n')
        htmlpage.write('</table></center><hr>\n')
        htmlpage.write('<address>Gianluca Cerminara</address>\n')
        htmlpage.write('</body>\n')
        htmlpage.write('</html>\n')
        htmlpage.close()
        
class WebPageWriter:
    """
    Writes the HTML page for all the AlcaRecos of a given epoch/period.
    For each alcareco the plots and log files are shown. The alcareco are indexed by PD
    """
    
    def __init__(self, name, epoch, version):
        """
        set the parameters for the page
        """
        self._fineName = name + ".html"
        self._title = "pippo"
        self._pds = []
        self._datasets = dict()
        self._epoch = epoch
        self._version = version
        self._title = "AlcaReco Monitoring for " + self._epoch + " " + self._version 

        
    def addDataset(self, pd, alcarecodetails):
        """
        add the report for a given AlcaReco
        """
        if not pd in self._datasets:
            self._pds.append(pd)
            self._datasets[pd] = []
        self._datasets[pd].append(alcarecodetails)
        return

    def buildPage(self):
        """
        Actually write the HTML page
        """
        htmlpage = file(self._fineName,"w")
        htmlpage.write('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">\n')
        htmlpage.write('<html><head>\n')
        htmlpage.write('<link rel="stylesheet" type="text/css" href="./PromptCalibMonitoring.css">\n')
        htmlpage.write('<title>' + self._title + '</title>\n')
        htmlpage.write('</head>\n')
        htmlpage.write('<body>\n')
        htmlpage.write('<center><h1>' + self._title + '</h1></center>\n<hr>\n')
        htmlpage.write('<center>[<a href=./index.html>index</a>]</center><br>\n')
        htmlpage.write('<p>\n')

        self._pds.sort()
        
        for pd in self._pds:
            htmlpage.write('<b>' + pd + '</b>:\n')
            listofalcarecos = self._datasets[pd]
            for alcareco in listofalcarecos:
                anchor = "#" + pd +  alcareco.name()
                htmlpage.write(' <a href=' + anchor + '>' + alcareco.name() + '</a> \n')
            htmlpage.write('<br>\n')
        htmlpage.write('</p>\n')
        htmlpage.write('<p>The monitoring is based on DBS and is limited to runs defined as <i>Collision</i> in Run Registry.</p>\n')
        htmlpage.write('<p>Last update: ' + str(datetime.datetime.today()) + '</p>\n')
        for pd in self._pds: 
            htmlpage.write('<h3>' + pd + '</h3>\n')
            htmlpage.write('<table width="100%">\n')
            listofalcarecos = self._datasets[pd] 
            for alcareco in listofalcarecos:
                anchor = pd +  alcareco.name()
                effpng = pd + '-' + self._epoch + '-' + alcareco.name() + '-' + self._version + '-hEff.png'
                neventspng = pd + '-' + self._epoch + '-' + alcareco.name() + '-' + self._version + '-hNEvents.png'
                htmlpage.write('<tr><td><a name=' + anchor + '></a><b>' + alcareco.name() + '</b></td>\n')
                htmlpage.write('<td>' + alcareco.dataset() + '</td></tr>\n')
                htmlpage.write('<tr><td><h4>Number of events per run</h4></td>\n')
                htmlpage.write('<td><h4>Selection efficiency per run</h4></td></tr>\n')
                htmlpage.write('<tr><td><a href=./' + neventspng + '><img src="./' + neventspng + '" width="590"></a></td>\n')
                htmlpage.write('<td><a href=./' + effpng + '><img src="./' + effpng + '" width="590"></a></td></tr>\n')
                datafilename = pd + '-' + self._epoch + '-' + alcareco.name() + '-' + self._version + ".cache"
                htmlpage.write('<tr><td>Link to <a href=./' + datafilename + '>data</a> file used to build the plot.</td><td></td></tr>\n')
            htmlpage.write('</table>\n')
            htmlpage.write('<hr>\n')
            htmlpage.write('<center>[<a href=./' + self._fineName + '>back to the top</a>]</center>\n')
            
        htmlpage.write('<address>Gianluca Cerminara</address>\n')
        htmlpage.write('</body>\n')
        htmlpage.write('</html>\n')
        htmlpage.close()



def dbsQueryRunList(dataset, minRun = 1, maxRun = -1):
    """
    Query DBS to get the list of runs in a given dataset
    """
    dbs_cmd = 'dbs search --noheader --query="find run where dataset=' + dataset
    if minRun > 1:
        dbs_cmd += ' and run > ' + str(minRun)
    if maxRun != -1:
        dbs_cmd += ' and run < ' + str(maxRun)
        
    dbs_cmd += '"'
    #print dbs_cmd
    dbs_out = commands.getstatusoutput(dbs_cmd)
    return dbs_out

def dbsQueryMinRun(dataset):
    """
    Query DBS for the minimum run number in the dataset
    """
    dbs_cmd = 'dbs search --noheader --query="find min(run) where dataset=' + dataset
    dbs_cmd += '"'
    #print dbs_cmd
    dbs_out = commands.getstatusoutput(dbs_cmd)
    return dbs_out


def dbsQuery(dataset, minRun = 1, maxRun = -1):
    """
    Query DBS to ge the list of runs and the # of events for each run
    """
    dbs_cmd = 'dbs search --noheader --query="find run,sum(file.numevents) where dataset=' + dataset
    if minRun > 1:
        dbs_cmd += ' and run > ' + str(minRun)
    if maxRun != -1:
        dbs_cmd += ' and run < ' + str(maxRun)
        
    dbs_cmd += '"'
    #print dbs_cmd
    dbs_out = commands.getstatusoutput(dbs_cmd)
    return dbs_out


class DBSAlCaRecoRunInfo():
    """
    Stores the information for each run of a given dataset and computes the efficiencyof the selection.
    Can be filled directly from the DBS output
    """
    def __init__(self):
        self._runnumber = -1
        #self._nlumi = -1
        self._nevents = -1.
        self._nEventsParent = -1
        return
    
    def run(self):
        return self._runnumber

    #def nLumi(self):
    #    return self._nlumi

    def nEvents(self):
        return self._nevents

    def setNEventsParent(self, nevents):
        self._nEventsParent = nevents

    def nEventsParent(self):
        return self._nEventsParent


    #def nEventsPerLumi(self):
    #    return self._nevents/self._nlumi

    def setFromQuery(self, queryLine):
        values = queryLine.split()
        self.setValues(values)

    def setValues(self, values):
        self._runnumber = int(values[0])
        self._nevents = float(values[1])
        if len(values) == 3:
            self._nEventsParent = float(values[2])
        
    def selEfficiency(self):
        if self._nEventsParent == -1 or self._nEventsParent == 0.:
            return 0
        return self._nevents/self._nEventsParent

    def getList(self):
        theList = [str(self.run()), str(self.nEvents()), str(self.nEventsParent())]
        return theList



class DBSAlCaRecoResults():
    """
    Stores and manipulate all the information for a given dataset (AlcaReco)
     - It can be filled out of DBS output or out of a txt cache file.
     - It is also able to write the content to txt file for cache
     Internally stores a list of DBSAlCaRecoRunInfo 
    """
    
    def __init__(self, name, parent):
        """
        Takes as input the dataset name and the name of the parent dataset
        """
        self._datasetname = str(name)
        self._parent = str(parent)
        self._infoPerRun = []
        pd = name.split("/")[1]
        othername = name.split("/")[2]
        self._cachefilename = pd + '-' + othername
        self._lasCachedRun = 1
        return


    def name(self):
        """
        Access the dataset name
        """
        return self._datasetname



    def parent(self):
        """
        Access the parent dataset name
        """
        return self._parent

    def sort(self):
        """
        Sort the list of details by run
        """
        self._infoPerRun.sort(key=lambda rr: rr._runnumber)
        return

    def appendQuery(self, queryOut):
        """
        Add a new DBSAlCaRecoRunInfo directly from the DBS query output
        """
        lines = queryOut.split("\n")
        #print len(lines)
        for line in lines:
            #print line
            if line != "":
                alcaRun = DBSAlCaRecoRunInfo()
                alcaRun.setFromQuery(line)
                self._infoPerRun.append(alcaRun)

    def printAll(self):
        self.sort()
        for run in  self._infoPerRun:
            print "run #: " + str(run.run() ) + " # events: " + str(run.nEvents()) + " eff.: "  + str(run.selEfficiency())

    def size(self):
        """
        Access the size of the DBSAlCaRecoRunInfo list
        """
        return len(self._infoPerRun)
    
    def search(self, run):
        """
        Search for a particular run
        """
        self.sort()
        hi = self.size()
        lo = 0
        while lo < hi:
            mid = (lo+hi)//2
            midval = self._infoPerRun[mid].run()
            if midval < run:
                lo = mid+1
            elif midval > run:
                hi = mid
            else:
                return mid

        return -1

    def addParentQuery(self, query):
        """
        Add the # of events per run for the parent dataset starting directly from the DBS query
        """
        for line in query.split("\n"):
            if line != "":
                print line
                run = int(line.split()[0])
                nevents = float(line.split()[1])
                index = self.search(run)
                if index != -1:
                    rrep = self._infoPerRun[index].setNEventsParent(nevents)


    def purgeList(self, runs):
        """
        Purge the input list of run # from the list of DBSAlCaRecoRunInfo 
        """
        #print runs
        print "Prune run list:"
        #print "   - # collision runs: " + str(len(runs))
        print "   - # runs in the list (before): " + str(len(self._infoPerRun))
        runtoremove = []
        for rrep in self._infoPerRun:
            #print rrep.run()
            if not rrep.run() in runs and rrep.run() > self._lasCachedRun:
                #print "run: " + str(rrep.run()) + " is not a Collision run: remove!"
                runtoremove.append(rrep)
        for run in runtoremove:
            self._infoPerRun.remove(run)

        print "   - # runs to be removed: " + str(len(runtoremove))
        print "   - # runs in the list (after): " + str(len(self._infoPerRun))

    def writeCache(self):
        """
        Dump the full content to txt file (cache and log purposes)
        """
        cacheFileName = self._cachefilename + ".cache"
        print "Write cache file: " + cacheFileName
        tableForCache =[]
        tableForCache.append(["# run", "# events", "# events parent"])
        for rrep in self._infoPerRun:
            tableForCache.append(rrep.getList())
            
        cacheFile = file(cacheFileName,"w")
        tableWriter.pprint_table(cacheFile, tableForCache)
        cacheFile.close()
        return

    def readCache(self):
        """
        Reads the full list from a txt file
        """
        cacheFileName = self._cachefilename + ".cache"
        print "reading cache file: " + cacheFileName
        if os.path.exists(cacheFileName):
            cache = file(cacheFileName,"r")
            data = cache.readlines()
            for line in data:
                if line[0] != '#' and line != "":
                    items = line.split()
                    rrep = DBSAlCaRecoRunInfo()
                    rrep.setValues(items)
                    self._infoPerRun.append(rrep)
            cache.close()      
            if len(self._infoPerRun) != 0:
                self._lasCachedRun = self._infoPerRun[len(self._infoPerRun)-1].run()
                return self._infoPerRun[len(self._infoPerRun)-1].run()
        else:
            print "Error: no file found"
            # FIXME: throw exception
        return 1
        

    def buildHistoNEvents(self):
        """
        Produce the summary histograms of # of events using pyRoot
        """
        nRuns = self.size()
        hNEvents = TH1F(self._cachefilename + "-hNEvents","# events",nRuns, 0, nRuns);
        binN = 1
        for rrep in self._infoPerRun:
            #print rrep.nEvents()
            # print rrep.run()
            hNEvents.SetBinContent(binN, rrep.nEvents())
            hNEvents.GetXaxis().SetBinLabel(binN, str(rrep.run()))
            binN += 1
        print "plot events, # of bins: " + str(binN)
        hNEvents.GetXaxis().SetTitle("run #")
        hNEvents.GetXaxis().SetTitleOffset(1.6)
        hNEvents.GetYaxis().SetTitle("# events")
        hNEvents.SetFillColor(kRed-9)
        hNEvents.LabelsOption("v","X")
        return hNEvents


    def buildHistoEff(self):
        """
        Produce the summary histograms of the selection efficiency using pyRoot
        """
        nRuns = self.size()
        hEff = TH1F(self._cachefilename + "-hEff","# events",nRuns, 0, nRuns);
        binN = 1
        for rrep in self._infoPerRun:
            hEff.SetBinContent(binN, rrep.selEfficiency())
            hEff.GetXaxis().SetBinLabel(binN, str(rrep.run()))
            binN += 1
        hEff.GetXaxis().SetTitle("run #")
        hEff.GetXaxis().SetTitleOffset(1.6)
        hEff.GetYaxis().SetTitle("Sel. eff.")
        hEff.SetFillColor(kBlue-1)
        hEff.LabelsOption("v","X")
        return hEff

def getDatasets(pd, epoch, version, tier):
    """
    Query DBS to find all the datasets for a given PD/Epoch/version/datatier set
    """
    dbs_cmd = 'dbs search --noheader --query="find dataset where dataset=/' + pd + '/' + epoch + '-*' + version + '/' + tier +'"'
    print dbs_cmd
    dbs_out = commands.getstatusoutput(dbs_cmd)
    listofgroups = dbs_out[1].split("\n")
    listforret = []
    for dataset in listofgroups:
        if dataset == "":
            continue
        print dataset
        versionpart = dataset.split("/")[2]
        components = versionpart.split("-")
        if len(components) <= 3:
            listforret.append(dataset)
        else:
            theepoch = components[0]
            # new version for WMA dataser names
            theversion = components[len(components)-1]
            # FIXME: dont' remember why it was like this
            # theversion = components[len(components)-2] + "-" +  components[len(components)-1]
            #print theversion
            if theversion == version:
                listforret.append(dataset)
    return listforret




import json

class AlcaRecoDatasetJson:
    def __init__(self, name):
        self._name = name
        self._datasetMap = {}

    def addDataset(self, dataset, details):
        self._datasetMap[dataset] = {}
        self._datasetMap[dataset]["dataset"] = details._datasetname
        self._datasetMap[dataset]["epoch"] = details._epoch
        self._datasetMap[dataset]["version"] = details._version
        self._datasetMap[dataset]["pd"] = details._pd
        print dataset
        
    def writeJsonFile(self):
        filename =  self._name + ".json"
        # get a string with JSON encoding the list
        #dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else None
        dump = json.dumps(self._datasetMap)
        file = open(filename, 'w')
        file.write(dump + "\n")
        file.close()

    def readJsonFile(self):
        filename = self._name + ".json"
        jsonData = open(filename)
        self._datasetMap = json.load(jsonData)
        jsonData.close()

    def getDatasetDetails(self, dataset):
        dataMap = self._datasetMap[dataset]
        details = AlcaRecoDetails(dataMap["dataset"], dataMap["pd"], dataMap["epoch"], dataMap["version"])
        return details

    def getDatasets(self):
        return self._datasetMap.keys()
