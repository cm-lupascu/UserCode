#!/usr/bin/env python

import os, sys, re, time

import random
from threading import Thread
try:
    from Configuration.PyReleaseValidation.WorkFlow import WorkFlow
except ImportError:
    print "ops..old API!"

from runTheMatrix import *


def modifyCommandForGT(command, gtName, isLocal):
    if command == None:
        return command


    command = command.replace('EVENTS: 2000000', 'EVENTS: 200')
    #print "COMMAND: " + command

    releasearea = os.environ["CMSSW_BASE"]
    username = os.environ["USER"]
    usernameinit = username[0]
    if 'CMSSW_3_6' in  releasearea  or 'CMSSW_3_5' in  releasearea :
        command = command.replace('auto:mc',gtName+"::All")
        command = command.replace('auto:startup',gtName+"::All")
        command = command.replace('auto:craft08',gtName+"::All")
        command = command.replace('auto:craft09',gtName+"::All")
        command = command.replace('auto:com10',gtName+"::All")
        command = command.replace('auto:starthi',gtName+"::All")

        if isLocal and "cmsDriver" in command:
            command = command + " --customise  Configuration/StandardSequences/customGT_" + gtName + ".py"

    else:
        conditionOpt = gtName + "::All"
        if isLocal:
            conditionOpt += ",sqlite_file:/afs/cern.ch/user/" + usernameinit + "/" + username + "/public/Alca/GlobalTag/" + gtName + ".db"
        command = command.replace('auto:mc',conditionOpt)
        command = command.replace('auto:startup',conditionOpt)
        command = command.replace('auto:craft08',conditionOpt)
        command = command.replace('auto:craft09',conditionOpt)
        command = command.replace('auto:com10',conditionOpt)
        command = command.replace('auto:starthi',conditionOpt)
        

    return command



def duplicateWorkflowForGTTest(matrixreader, wfid, newwfid, gtName, isLocal=False):
    print "# of workflows in the matrix: " + str(len(matrixreader.workFlows))

    for wf in matrixreader.workFlows:
        if float(wfid) == float(wf.numId):
            print "Duplicate workflow: " + wf.nameId + " for GT: " + gtName
            if isLocal == False:
                newWfname = gtName + '_FRONTIER+' + wf.nameId
            else:
                newWfname = gtName + '_LOCAL+' + wf.nameId
            if hasattr(wf, 'input'):
                # this is the new version of the API (> 43X)
                step2addition = ""
                if wfid == '40':
                    # don't genererate a sample in the acse of the HI workflow
                    step2addition = " --himix  --process HIMIX --filein   /store/relval/CMSSW_3_9_7/RelValPyquen_ZeemumuJets_pt10_2760GeV/GEN-SIM-DIGI-RAW-HLTDEBUG/START39_V7HI-v1/0054/102FF831-9B0F-E011-A3E9-003048678BC6.root"
                    
                matrixreader.workFlows.append(WorkFlow(str(newwfid), newWfname, modifyCommandForGT(wf.cmdStep1,gtName, isLocal), modifyCommandForGT(wf.cmdStep2,gtName, isLocal) + step2addition, modifyCommandForGT(wf.cmdStep3,gtName, isLocal), modifyCommandForGT(wf.cmdStep4,gtName, isLocal), wf.input))
            else:
                # old versin of the API
                matrixreader.workFlows.append(WorkFlow(str(newwfid), newWfname, modifyCommandForGT(wf.cmdStep1,gtName, isLocal), modifyCommandForGT(wf.cmdStep2,gtName, isLocal), modifyCommandForGT(wf.cmdStep3,gtName, isLocal), modifyCommandForGT(wf.cmdStep4,gtName, isLocal)))
                                              
                                              


def runGTSelectionNew(gts, gtmap, isLocal, nThreads=4, original=False, show=False, useInput=None) :

    stdList = ['5.2', # SingleMu10 FastSim
               '7',   # Cosmics+RECOCOS+ALCACOS
               '8',   # BeamHalo+RECOCOS+ALCABH
               '25',  # TTbar+RECO2+ALCATT2  STARTUP
               ]
    hiStatList = [
                  '121',   # TTbar_Tauola
                  '123.3', # TTBar FastSim
                   ]

    mrd = MatrixReader()
    mrd.prepare(useInput)

    testList = []
    index = 10000
    for gt in gts:
        # print "about to duplicate: " + gt
        wfidtodup = gtmap[gt]
        # add the workflows for the test of the GT (local)
        if wfidtodup == 40:
            index = 40
        duplicateWorkflowForGTTest(mrd, wfidtodup, index, gt, isLocal) 
        if original:
            testList.append(wfidtodup)
        else:
            testList.append(index)
        index = index + 1

    if len(testList) == 0 :
        print "No process selected"
        return 0

    ret = 0
    if show:
        mrd.show([float(x) for x in testList])
        print 'selected items:', testList
    else:
        mRunnerHi = MatrixRunner(mrd.workFlows, nThreads)
        ret = mRunnerHi.runTests(testList)

    return ret


def runGTSelection(gts, gtmap, isLocal, nThreads=4, original=False, show=False) :

    stdList = ['5.2', # SingleMu10 FastSim
               '7',   # Cosmics+RECOCOS+ALCACOS
               '8',   # BeamHalo+RECOCOS+ALCABH
               '25',  # TTbar+RECO2+ALCATT2  STARTUP
               ]
    hiStatList = [
                  '121',   # TTbar_Tauola
                  '123.3', # TTBar FastSim
                   ]

    mrd = MatrixReader()
    files = ['cmsDriver_standard_hlt.txt', 'cmsDriver_highstats_hlt.txt']
    offset = 0
    for matrixFile in files:
        try:
            mrd.readMatrix(matrixFile, offset=offset)
#            mrd.readMatrix(matrixFile)
        except Exception, e:
            print "ERROR reading file:", matrixFile, str(e)
        offset += 100

    try:
        mrd.createWorkFlows()
    except Exception, e:
        print "ERROR creating workflows :", str(e)


    testList = []
    index = 1000
    for gt in gts:
        # print "about to duplicate: " + gt
        wfidtodup = gtmap[gt]
        # add the workflows for the test of the GT (local)
        duplicateWorkflowForGTTest(mrd, wfidtodup, index, gt, isLocal) 
        if original:
            testList.append(wfidtodup)
        else:
            testList.append(index)
        index = index + 1

    if len(testList) == 0 :
        print "No process selected"
        return 0

    ret = 0
    if show:
        mrd.show([float(x) for x in testList])
        print 'selected items:', testList
    else:
        mRunnerHi = MatrixRunner(mrd.workFlows, nThreads)
        ret = mRunnerHi.runTests(testList)

    return ret


        
# ================================================================================
from ConfigParser import ConfigParser

if __name__ == '__main__':


    from optparse import OptionParser

    
    # set the command line options
    parser = OptionParser()
    parser.add_option("--query", action="store_true",dest="show")
    parser.add_option("--local", action="store_true",dest="local",default=False)
    parser.add_option("--original", action="store_true",dest="original")

    parser.add_option("-i","--useInput", dest="useInputStr",
                     help="recycle input", type="str", metavar="<workflows>")
    
    #parser.add_option("-r", "--release", dest="release",
    #                 help="CMSSW release", type="str", metavar="<release>")
     
     
    (options, args) = parser.parse_args()
    #print "OPTIONS: ", options
    #print "ARGS: ", args
    
    #print options.useInputStr
    useInput = options.useInputStr.split(',')
    #print useInput
    
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

    print globaltagsandWfIds

    # arguments: list of GTS, might be all
    gts = []
    if 'all' in args:
        gts = globaltagsandWfIds.keys()
    else:
        gts = args
    
    print gts
    #sys.exit(0)



    np=4 # default: four threads
    releasearea = os.environ["CMSSW_BASE"]

    if 'CMSSW_3_6' in  releasearea or 'CMSSW_3_7' in  releasearea :
        ret = runGTSelection(gts, globaltagsandWfIds, options.local, np, options.original, options.show)
    else:
        ret = runGTSelectionNew(gts, globaltagsandWfIds, options.local, np, options.original, options.show, useInput)
    #sys.exit(ret)
