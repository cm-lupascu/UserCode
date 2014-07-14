#!/usr/bin/env python

import os
import sys

from ConfigParser import ConfigParser

import Tools.MyCondTools.RunRegistryTools as RunRegistryTools
import Tools.MyCondTools.alcaRecoMonitoringToolsTest as alcaRecoMonitoringToolsTest
#from Tools.MyCondTools.RunValues import *



import shutil



from ROOT import *
from array import array

import datetime

import os,string,sys,commands,time
#import xmlrpclib


    
if __name__ == "__main__":

    # --------------------------------------------------------
    # --- Get the configuration from file
    
    configfile = ConfigParser()
    configfile.optionxform = str

    configfile.read('GT_branches/AlCaRecoMonitoring.cfg')
    webArea = configfile.get('Common','webArea')
    groups = configfile.get('Common','groups').split(",")
    refreshCache = bool(configfile.get('Common','refreshCache'))

    # list of datasets to be monitored
    alcarecoDatasets = []

    os.chdir(webArea)



    # 1 find all the alcarecos and their parents for each "group"
    for group in groups:
        if group == "":
            continue
        print "--------------------------------------------"
        print "--------------------------------------------"
        print "==== Group: " + group

        # read the configration for this "group"
        epoch = configfile.get(group, 'epoch')
        version = configfile.get(group, 'version')
        rawversion = configfile.get(group, 'rawversion')
        print "==== Epoch: " + epoch
        print "==== Version: " + version
        print "==== RawV: " + rawversion

        # look for ALCARECO dataserts matching this "group" in DBS
        jsonDatasetList = alcaRecoMonitoringToolsTest.AlcaRecoDatasetJson(group)
        datasets = alcaRecoMonitoringToolsTest.getDatasets("*",epoch, version, "ALCARECO")
        # for all datasets look for the parent
        for dataset in datasets:
            pd = dataset.split("/")[1]
            parenttier = "RECO"
            # exception
            if group == "Run2011A-v4":
                parenttier = "RAW"
            pdforhtml = pd
            details = alcaRecoMonitoringToolsTest.AlcaRecoDetails(dataset, pdforhtml, epoch, version)
            if pd == 'StreamExpressCosmics':
                continue
            jsonDatasetList.addDataset(dataset, details)
            if pd == 'StreamExpress':
                pd = 'ExpressPhysics'
                parenttier = "FEVT"
            if pd == 'StreamHIExpress':
                pd = 'HIExpressPhysics'
                parenttier = "FEVT"
            parent = alcaRecoMonitoringToolsTest.getDatasets(pd,epoch, version, parenttier)
            # filter out RECO datasets which are not the right ones
            parent = filter(alcaRecoMonitoringToolsTest.PDFilterOutPromptSkim, parent)
            if len(parent) == 0 or parent[0] == '':
                parent = alcaRecoMonitoringToolsTest.getDatasets(pd,epoch, rawversion,"RAW")
            print "--------------------------------------------"
            print "dataset: " + dataset
            print "parent: " + parent[0]
            alcarecoDatasets.append(alcaRecoMonitoringToolsTest.DBSAlCaRecoResults(dataset, parent[0]))
        jsonDatasetList.writeJsonFile()


    #2 get the statistics and draw the results
    cachedlisttype = "DUMMY"
    cachedlist = []
    

    print "Getting details for each dataset:"
    
    for dataset in alcarecoDatasets:
        print ""
        print "-----------"
        print "Dataset: " + dataset.name()
        lastCached = dataset.readCache() #FIXME
        print "  last cached run: " + str(lastCached)
        if lastCached == 1:
            minRunDBS = alcaRecoMonitoringToolsTest.dbsQueryMinRun(dataset.name())
            print " no cache found...get the first run from DBS: " + str(minRunDBS)
            lastCached = minRunDBS
            
        #lastCached = 160404
        if refreshCache:

            rrSet = ""
            # FIXME: this needs to be more general
            if "2010" in  dataset.name():
                rrSet = "Collisions10"
            elif "2011" in dataset.name():
                rrSet = "Collisions11"
            elif "2012" in dataset.name():
                rrSet = "Collisions12"
            elif "2013" in dataset.name():
                rrSet = "Collisions13"

            # cache the list from RR
            #if rrSet != cachedlisttype:
            cachedlisttype = rrSet
            #cachedlist = getRunList(1, rrSet)
            cachedlist = RunRegistryTools.getRunListRR3(lastCached, "Online", cachedlisttype)
            cachedlist.sort()
            runList = cachedlist         
            print "RR: " + rrSet + " # runs: " + str(len(runList))
            # print runList

            print "======== Cached list ==========="
            print cachedlist
            print "================================="
            # FIXME: max run (used to limit the size of the query)
            minRun = cachedlist[0]
            maxRun = minRun
            if len(cachedlist) > 1:
                while maxRun < cachedlist[1]:
                    maxRun = maxRun + 500
            else:
                maxRun = maxRun + 500
            print "min: " + str(minRun) + " max: " + str(maxRun)
            query = alcaRecoMonitoringToolsTest.dbsQuery(dataset.name(), minRun, maxRun)
            dataset.appendQuery(query)
            queryParent = alcaRecoMonitoringToolsTest.dbsQuery(dataset.parent(), minRun, maxRun)
            dataset.addParentQuery(queryParent)

                
            dataset.purgeList(runList)
           
           
            dataset.printAll()
            dataset.writeCache()

    #raw_input ("Enter to quit")
    sys.exit(0)
    
    

    
