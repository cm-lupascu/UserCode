import json
import sys, urllib2
import time
import ast
#from xml.dom import minidom

"""
Module providing an interface to common queries to Tier0-DAS

$Date: 2013/01/22 13:50:33 $
$Revision: 1.1 $
Author: G.Cerminara

"""


class Tier0DasInterface:
    """
    Class handling common Tier0-DAS queries and connected utilities
    """
    def __init__(self, url = 'https://cmsweb.cern.ch/t0wmadatasvc/prod/'):
        """
        Need base url for Tier0-DAS as input
        """
        #self._t0DasBaseUrl = "http://gowdy-wttest.cern.ch:8304/tier0/"
        self._t0DasBaseUrl = url
        self._debug = False
        self._retry = 0
        self._maxretry = 5

    def getData(self, src, tout=5, proxy=None):
        """
        Get the JSON file for a give query specified via the Tier0-DAS url.
        Timeout can be set via paramter.
        """
        # actually get the json file from the given url of the T0-Das service
        # and returns the data

        try:
            if proxy:
                print "setting proxy"
                opener = urllib2.build_opener(urllib2.HTTPHandler(),
                                              urllib2.HTTPSHandler(),
                                              urllib2.ProxyHandler({'http':proxy, 'https':proxy}))
                urllib2.install_opener(opener)
            req = urllib2.Request(src)
            req.add_header("User-Agent",
                           "PCLMonitor/1.0 python/%d.%d.%d" % sys.version_info[:3])
            req.add_header("Accept","application/json")
            jsonCall = urllib2.urlopen(req, timeout = tout)
            url = jsonCall.geturl()
        except urllib2.HTTPError,  error:
            #print error.url
            errStr = "Cannot retrieve Tier-0 DAS data from URL \"" + error.url + "\""
            if proxy:
                errStr += " using proxy \"" + proxy + "\""
            print errStr
            print error
            raise urllib2.HTTPError("FIXME: handle exceptions")
        except urllib2.URLError,  error:
            if self._retry < self._maxretry:
                print 'Try # ' + str(self._retry) + " connection to Tier-0 DAS timed-out"
                self._retry += 1
                newtout = tout*self._retry
                time.sleep(3*self._retry)
                return self.getData(src,newtout,proxy)
            else:
                errStr = "Cannot retrieve Tier-0 DAS data from URL \"" + src + "\""
                if proxy:
                    errStr += " using proxy \"" + proxy + "\""
                self._retry = 0
                print errStr
                print error
                raise urllib2.URLError('TimeOut reading ' + src)

        except:
            raise
        else:
            if self._debug:
                print url
            jsonInfo = jsonCall.info()
            if self._debug:
                print jsonInfo
            jsonText = jsonCall.read()
            data = json.loads(jsonText)
            if self._debug:
                print "data:", data
            return data

    def getResultList(self, json):
        """
        Extractt the result list out of the JSON file
        """
        resultList = []
        #FIXME try
        resultList = json['result']

        #print self.getValues(json, 'result')
        return resultList

    def getValues(self, json, key, selection=''):
        """
        Extract the value corrisponding to a given key from a JSON file. It is also possible to apply further selections.
        """
        # lookup for a key in a json file applying possible selections
        data = []
        check = 0
        if selection != '':
            check = 1
            (k, v) = selection

        for o in json:
            #print o
            try:
                if check == 1:
                    if (o[k] == v):
                        data.append(o[key])
                else:
                    data.append(o[key])
            except KeyError as error:
                print "[Tier0DasInterface::getValues] key: " + key + " not found in json file"
                print error
                raise
            except:
                print "[Tier0DasInterface::getValues] unknown error"
                raise
                #pass
        #print data
        return data

    def lastPromptRun(self):
        """
        Query to get the last run released for prompt
        """
        url = self._t0DasBaseUrl + "reco_config"
        try:
            json = self.getData(url)
            results = self.getResultList(json)
            workflowlist = ast.literal_eval(results[0])
            maxRun = -1
            for workflow in workflowlist:
                run = workflow['run']
                if int(run) > maxRun:
                    maxRun = run
            return maxRun
        except:
            print "[Tier0DasInterface::lastPromptRun] error"
            raise
            return 0

    def firstConditionSafeRun(self):
        """
        Query to ge the run for which the Tier0 system considers safe the update to the conditions
        """
        url = self._t0DasBaseUrl + "firstconditionsaferun"
        try:
            json = self.getData(url)
            results = self.getResultList(json)
            return results[0]
        except Exception as details:
            print "[Tier0DasInterface::firstConditionSafeRun] error", details
            raise
        return 0

    def promptGlobalTag(self, dataset):
        """
        Query the GT currently used by prompt = GT used by the last run released for prompt.
        """
        url = self._t0DasBaseUrl + "reco_config"
        #print "url =", url
        try:
            json = self.getData(url)
            results = self.getResultList(json)
            workflowlist = ast.literal_eval(results[0])
            gt = "UNKNOWN"
            for workflow in workflowlist:
                if workflow['primary_dataset'] == dataset:
                    gt = workflow['global_tag']
            # FIXME: do we realluy need to raise?
            if gt == "UNKNOWN":
                raise KeyError
            return gt
        except:
            print "[Tier0DasInterface::promptGlobalTag] error"
            raise
            return None


if __name__ == "__main__":
    test = Tier0DasInterface()

    if True:
        try:
            print "Tier0 DAS last run released for PROMPT:       ", test.lastPromptRun()
        except Exception as error:
            print 'Error 1'
            print error

    if True:
        try:
            run = test.firstConditionSafeRun()
            print "Tier0 DAS first run safe for condition update:", run
        except Exception as error:
            print 'Error 2'
            print error

    if True:
        try:
            dataset = 'MinimumBias'
            print "Tier0 DAS GT for dataset: " + dataset + " :", test.promptGlobalTag(dataset)
        except Exception as error:
            print 'Error 3'
            print error
