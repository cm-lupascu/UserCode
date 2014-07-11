#!/usr/bin/env python
import os
import Tools.MyCondTools.monitoring_config as config



# FIXME: this is not used coherently in the code....
writeToWeb             = True


class WebPageWriter:
    def __init__(self):
        self._fineName ="/index.html"
        self._title = "Monitoring of Prompt Calibration Loop"
        self._version = "3.0"
        self._nRunsInPlot = 100
        self._workflows = []
        self._reports = []

        self._statusCode = -1
        self._statusMsg = ""
        self._statusImg = "../common/img/warning.png"
        self._backEndUpdate = datetime.datetime
        self._udateAge = datetime.timedelta


    def addWorkflow(self, workflow, tagReport):
        self._workflows.append(workflow)
        self._reports.append(tagReport)

    def setBackendUpdateDate(self, date):
        self._backEndUpdate = date
        
    def setNRunsShown(self, nRuns):
        self._nRunsInPlot = nRuns


    def setOldUpdateWarning(self, age):
        self._udateAge = age
        
        
    def statusSummary(self, code, message):
        self._statusCode = code
        self._statusMsg = message
        if self._statusCode == 0:
            self._statusImg = "../common/imgs/ok.png"
            self._statusMsg = '<b>OK: </b> ' + self._statusMsg
        elif self._statusCode <= 10:
            self._statusImg = "../common/imgs/warning.png"
            self._statusMsg = '<b>WARNING: </b> ' + self._statusMsg
        else:
            self._statusImg = "../common/imgs/error.png"
            self._statusMsg = '<b>ERROR: </b> ' + self._statusMsg
            

    def buildPage(self, directory):
        htmlpage = file(directory + self._fineName,"w")

        #--- Write the HTML header
        htmlpage.write('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">\n')
        htmlpage.write('<html><head>\n')
        htmlpage.write('<link rel="stylesheet" type="text/css" href="../common/PromptCalibMonitoring.css">\n')
        htmlpage.write('<META HTTP-EQUIV="REFRESH" CONTENT="3600">\n')
        htmlpage.write('<title>' + self._title + '</title>\n')
        htmlpage.write('</head>\n')

        #--- Start the body
        htmlpage.write('<body>\n')
        htmlpage.write('<center><h1>' + self._title + '</h1></center>\n<hr>\n')
        #htmlpage.write('<center>[<a href=./index.html>index</a>]</center><br>\n')
        htmlpage.write('<p>\n')


        #--- Itroduction Paragraph
        htmlpage.write('<p>This page shows <b>monitoring</b> and <b>statistics</b> about the prompt-calibration loop running @ Tier0.</p>\n')
        htmlpage.write('<p>The following plots show the latency of the production step in hours. The dashed black line is the current average value. The monitoring is limited to the last ' + str(self._nRunsInPlot) + ' <i>collision</i> runs (based on Run-Registry).</p>\n')        
        htmlpage.write('<p>The workflows currently monitored are:</p>\n')

        #--- main menu for the choice of the workflow
        htmlpage.write('<center>')
        for wkflow in self._workflows:
            htmlpage.write('[<a href=#' + wkflow + '>' + wkflow + '</a>]')
        htmlpage.write('</center><br>\n')

        #--- global status table: display the global status from JSON and, in case of need, a warning about the update frequency 
        htmlpage.write('<table width="100%">\n')
        htmlpage.write('<tr><td><h3>Status summary of last 48h</h3></td></tr>\n')
        htmlpage.write('<tr><td><table><tr><td><img src="' + self._statusImg + '" width="20"></td><td>' \
                       + self._statusMsg + '</td><td>(Last update on: ' + str(self._backEndUpdate) + ')</td></tr></table></td></tr>\n')

        # FIXME: broken
        if self._udateAge >  datetime.timedelta(hours=2,minutes=0):
            htmlpage.write('<tr><td><img src="../common/imgs/warning.png" width="20"><b>WARNING:</b> last update is more than ' + str(self._udateAge) + ' hours old</td></tr>\n')
        htmlpage.write('</table>\n')


        ## --- build tables for each workflow
        for index in range(0, len(self._workflows)):
            wkflow = self._workflows[index]
            report = self._reports[index]
            
            plotName = 'cHisto_' + wkflow + '.png'
            logFileName = 'log_' + wkflow + '.txt'


            outstat = report.getProperty('status')
            msg = report.getProperty('statusMsg')

            # FIXME: the location of the various figures should be parametrized
            img = "../common/imgs/ok.png"
            runs = report.getProperty('runs')
            
            if outstat != 0 and outstat < 1000:
                img = "../common/imgs/warning.png"
            elif outstat != 0 and outstat >= 1000:
                img = "../common/imgs/error.png"

            


            # --- Status Table
            htmlpage.write('<h3>' + wkflow + '</h3><a name=' + wkflow + '></a>\n')
            htmlpage.write('<table width="100%">\n')
            htmlpage.write('<tr><td><h4>Status of last 48h:</h4></td></tr>\n')
            htmlpage.write('<tr><td><table><tr><td><img src="' + img + '" width="20"></td><td>' + msg + '</td></tr></table></td></tr>\n')

            if len(runs) != 0:
                htmlpage.write('<tr><td><table>\n')
                htmlpage.write('<tr><th>run</th><th>status</th></tr>\n')
                for run in runs: 
                    # read the status for thi run from JSON
                    valueAndStat = report.getProperty(str(run))
                    outstatrun = valueAndStat[0]
                    outstatmsgrun = valueAndStat[1]
                    img = "../common/imgs/ok.png"
                    if outstatrun < 1000:
                        # this is a warning
                        img = "../common/imgs/warning.png"
                    elif  outstatrun >= 1000:
                        # this is an error
                        img = "../common/imgs/error.png"

                    # FIXME: this should not be hardoced
                    if valueAndStat[0] == 1004:
                        # FIXME: the dates need to come from the RunReport through the new engine
                        outstatmsgrun += ' (<a href="https://cms-conddb-prod.cern.ch/logs/dropBox/searchUserLog?beginDate=2013-01-25&fileName=Run' + run + '@' + wkflow + '&endDate=2013-03-04&metadata=&fileHash=&userText=&username=cmsprod&backend=&statusCode=Any">Drop-Box Log</a>)' 
                    htmlpage.write('<tr><td><a href=https://cmswbm.web.cern.ch/cmswbm/cmsdb/servlet/RunSummary?RUN=' + run + '>' + run + '</a></td>')
                    htmlpage.write('<td><img src="' + img + '" width="20"></td><td>' + outstatmsgrun + '</td>')
                    htmlpage.write('</tr>\n')
                    
                htmlpage.write('</table></td></tr>\n')

            htmlpage.write('<tr><td><h4>Run states and latencies</h4></td></tr>\n')
            htmlpage.write('<tr><td><img src="./' + plotName + '" width="1200"></td></tr>\n')
            htmlpage.write('</table>\n')

            htmlpage.write('<p>Full logs can be accessed here: <a href=./' + logFileName + '>logs</a></p>\n')

            htmlpage.write('<hr>\n')
            htmlpage.write('<center>[<a href=./' + self._fineName + '>back to the top</a>]</center>\n')

        htmlpage.write('<address>Gianluca Cerminara</address>\n')
        htmlpage.write('<p>Page generated on: ' + str(datetime.datetime.today()) + '</p>\n')
        htmlpage.write('</body>\n')
        htmlpage.write('</html>\n')
        htmlpage.close()










import Tools.MyCondTools.pclMonitoringTools as pclMonitoringTools
import Tools.MyCondTools.tier0WMADasInterface as tier0DasInterface
import Tools.MyCondTools.monitorStatus as monitorStatus
import Tools.MyCondTools.RunInfo as RunInfo

import ROOT
import array
import os
import datetime

#from ROOT import *
def producePlots(pclTag, runReports, nRunsToPlot, maxtimeEnd, maxtimeBegin, averageTimeFromEnd, averageTimeFromBegin, lastPromptRecoRun):

    # --- set how many runs should be plotter
    nToFill = int(len(runReports))
    if nRunsToPlot != -1:
        nToFill = nRunsToPlot
    
    # --- set the style 
    # draw the plots
    ROOT.gStyle.SetOptStat(0) 
    ROOT.gStyle.SetPadBorderMode(0) 
    ROOT.gStyle.SetCanvasBorderMode(0) 
    ROOT.gStyle.SetPadColor(0);
    ROOT.gStyle.SetCanvasColor(0);
    ROOT.gStyle.SetOptTitle(0)
    ROOT.gStyle.SetPadBottomMargin(0.13)
    ROOT.gStyle.SetTitleXOffset(1.6)
    ROOT.gStyle.SetTitleOffset(1.6,"X")


    # --- book the histos
    newlegend = ROOT.TLegend(0.8,0.8,1,1)


    
    # --------------------------------------------------------------------------
    # histograms for delay monitoring
    hJobTimeFromEnd = ROOT.TH1F(pclTag + "_hJobTimeFromEnd","job delay (h) from the end-of-run",nToFill,0,nToFill)
    hJobTimeFromEnd.SetMarkerStyle(20)
    # FIXME: color
    # FIXME: add to legend
    
    hUploadTimeFromEnd = ROOT.TH1F(pclTag + "_hUploadTimeFromEnd","upload delay (h) from the end-of-run",nToFill,0,nToFill)
    hUploadTimeFromEnd.SetMarkerStyle(20)
    # FIXME: color
    # FIXME: add to legend

    hUploadTimeFromStart = ROOT.TH1F(pclTag + "_hUploadTimeFromStart","upload delay (h) from the start-of-run",nToFill,0,nToFill)
    hUploadTimeFromStart.SetMarkerStyle(20)
    # FIXME: color
    # FIXME: add to legend

    # ---------------------------------------------------------------------------
    # histograms for status monitoring



    hOk = ROOT.TH1F(pclTag + "_hOk", "OK", nToFill,0,nToFill)
    hOk.SetFillColor(408)
    hOk.SetFillColor(408)
    newlegend.AddEntry(hOk, "Ok","F")

    hUploadFailed = ROOT.TH1F(pclTag + "_hUploadFailed", "UploadFailed", nToFill,0,nToFill)
    hUploadFailed.SetFillColor(871)
    hUploadFailed.SetFillColor(871)
    newlegend.AddEntry(hUploadFailed, "UploadFailed","F")

    hNoUpload = ROOT.TH1F(pclTag + "_hNoUpload", "NoUpload", nToFill,0,nToFill)
    hNoUpload.SetFillColor(611)
    hNoUpload.SetFillColor(611)
    newlegend.AddEntry(hNoUpload, "NoUpload","F")

    hNoPayload = ROOT.TH1F(pclTag + "_hNoPayload", "NoPayload", nToFill,0,nToFill)
    hNoPayload.SetFillColor(500)
    hNoPayload.SetFillColor(500)
    newlegend.AddEntry(hNoPayload, "NoPayload","F")

    hMultiple = ROOT.TH1F(pclTag + "_hMultiple", "Multiple", nToFill,0,nToFill)
    hMultiple.SetFillColor(410)
    hMultiple.SetFillColor(410)
    newlegend.AddEntry(hMultiple, "Multiple","F")
    
    hNotRun = ROOT.TH1F(pclTag + "_hNotRun", "NotRun", nToFill,0,nToFill)
    hNotRun.SetFillColor(422)
    hNotRun.SetFillColor(422)
    newlegend.AddEntry(hNotRun, "NotRun","F")


    # superimpose the average
    lineAverageFromEnd = ROOT.TLine(0, averageTimeFromEnd, nToFill, averageTimeFromEnd)
    lineAverageFromEnd.SetLineColor(1)
    lineAverageFromEnd.SetLineWidth(2)
    lineAverageFromEnd.SetLineStyle(2)
    newlegend.AddEntry(lineAverageFromEnd,"average", "L")
        
    lineAverageFromBegin = ROOT.TLine(0, averageTimeFromBegin, nToFill, averageTimeFromBegin)
    lineAverageFromBegin.SetLineColor(1)
    lineAverageFromBegin.SetLineWidth(2)
    lineAverageFromBegin.SetLineStyle(2)

    # --- fill the histos
    index = 1
    indexLastT0Run = 1
    maxtimeEnd = maxtimeEnd * 1.05
    maxtimeBegin = maxtimeBegin * 1.05


    minId = 0
    if nRunsToPlot != -1 and nRunsToPlot < len(runReports):
        minId = len(runReports) - nRunsToPlot


    for id in range(minId, len(runReports)):
        report = runReports[id]

        if int(report.runNumber) < int(lastPromptRecoRun):
            indexLastT0Run = index

        # fill the latency plots
        hJobTimeFromEnd.SetBinContent(index, report.latencyJobFromEnd)
        hUploadTimeFromEnd.SetBinContent(index, report.latencyUploadFromEnd)
        hUploadTimeFromStart.SetBinContent(index, report.latencyUploadFromStart)


        # set bin label
        hOk.GetXaxis().SetBinLabel(index, str(report.runNumber))

        # set the various states filling the appropriate histogram


        if not report.pclRun:
            hNotRun.SetBinContent(index, maxtimeEnd)
        elif not report.hasPayload:
            hNoPayload.SetBinContent(index, maxtimeEnd)
        elif not report.hasUpload:
            hNoUpload.SetBinContent(index, maxtimeEnd)
        elif not report.uploadSucceeded:
            hUploadFailed.SetBinContent(index, maxtimeEnd)
        elif report.uploadSucceeded:
            hOk.SetBinContent(index, maxtimeEnd)

        if report.multipleFiles:
            hMultiple.SetBinContent(index, maxtimeEnd)

            #     hNotRun  -> not pclRun()
            #     hMultiple -> isPclRunMultipleTimes()
            #     hNoPayload -> 
            #     hNoUpload -> not uploadDone()
            #     hUploadFailed -> uploadDone() and not uploadSucceeded()
            #     hOk -> uploadSucceeded()

        index += 1
        


    lineLastPromptRecoEnd = ROOT.TLine(indexLastT0Run, 0, indexLastT0Run, maxtimeEnd)
    lineLastPromptRecoEnd.SetLineColor(2)
    lineLastPromptRecoEnd.SetLineWidth(3)
    lineLastPromptRecoEnd.SetLineStyle(2)
    newlegend.AddEntry(lineLastPromptRecoEnd, "Prompt-reco status", "L")


    lineLastPromptRecoBegin = ROOT.TLine(indexLastT0Run, 0, indexLastT0Run, maxtimeBegin)
    lineLastPromptRecoBegin.SetLineColor(2)
    lineLastPromptRecoBegin.SetLineWidth(3)
    lineLastPromptRecoBegin.SetLineStyle(2)


    # --- draw the histos
    c4 = ROOT.TCanvas("cTimeFromEndN1","cTimeFromEndN1",1200,600)
    hOk.GetYaxis().SetRangeUser(0,maxtimeEnd)
    hOk.Draw("")
    hOk.GetXaxis().SetTitle("run #")
    hOk.GetXaxis().SetTitleOffset(1.6)
    hOk.GetYaxis().SetTitle("delay (hours)")
    hOk.LabelsOption("v","X")

    hUploadFailed.Draw("same")
    hNoUpload.Draw("same")
    hNoPayload.Draw("same")
    hNotRun.Draw("same")

    lineAverageFromEnd.Draw("same")
    lineLastPromptRecoEnd.Draw("same")

    hJobTimeFromEnd.Draw("P,SAME")
    hUploadTimeFromEnd.Draw("P,SAME")
    hUploadTimeFromStart.Draw("P,SAME")
    newlegend.Draw("same")
    plotName = 'cHisto_' + pclTag + '.png'
    if writeToWeb:
        plot_path = os.path.join(config.webArea, plotName)
        c4.Print(plot_path)


    return plotName
    

if __name__ == "__main__":


    htmlwriter = WebPageWriter()




    tier0Das = tier0DasInterface.Tier0DasInterface(config.tier0DasSrc) 
    lastPromptRecoRun = 1
    try:
        lastPromptRecoRun = tier0Das.firstConditionSafeRun()
        print "Tier0 DAS last run released for PROMPT:       ", lastPromptRecoRun
        #print "Tier0 DAS first run safe for condition update:", tier0Das.firstConditionSafeRun()
    except Exception as error:
        print '*** Error: Tier0-DAS query has failed'
        print error


    # read the status JSON for the various pclTags
    pclTagsJson = pclMonitoringTools.PCLTagsJson('pclMonitor')
    pclTagsJson.readJsonFile(config.webArea)
    
    
    for pclTag in config.pclTasks:

        print "Read cache for tag: " + pclTag
        
        # get the run reports from the file
        logFileName = '/log_' + pclTag + '.txt'

        allCachedRuns = pclMonitoringTools.readCache(config.webArea + logFileName)
        cachedRuns = allCachedRuns[0]
        runReports = allCachedRuns[1]
        runReports.sort(key=lambda rr: rr.runNumber)

        # NOTE: if Tier0 is off than the lastPromptRecoRun is automatically bigger than the lat cached run but unfortunately Tier0DAS returns None
        # This is just a workaround
        lastPromptRecoRun = cachedRuns[len(cachedRuns)-1]+1

        # FIXME: move this to configuration
        nToFill = 100

        nRuns = int(len(runReports))

        minId = 0
        if nToFill != -1 and nToFill < nRuns:
            minId = nRuns - nToFill
        else:
            nToFill = nRuns


        # find some numbers needed to better format the plot
        avgJobFromEnd = 0
        nJobRun = 0
        avgUploadFromEnd = 0
        avgUploadFromStart = 0
        maxDelayFromStart = -1
        nUploads = 0
        for id in range(minId, len(runReports)):
            rRep = runReports[id]

            #print "Run: " + str(rRep.runNumber)
            if rRep.pclRun:
                avgJobFromEnd += rRep.latencyJobFromEnd
                nJobRun +=1
                if rRep.hasUpload:
                    nUploads += 1
                    avgUploadFromEnd += rRep.latencyUploadFromEnd
                    avgUploadFromStart += rRep.latencyUploadFromStart
                    if rRep.latencyUploadFromStart > maxDelayFromStart:
                        maxDelayFromStart = rRep.latencyUploadFromStart

        # avgJobFromEnd = avgJobFromEnd/nJobRun
        # avgUploadFromEnd = avgUploadFromEnd/nUploads
        # avgUploadFromStart = avgUploadFromStart/nUploads

        # FIXME: review the parameters
        plotName = producePlots(pclTag,\
                                runReports,\
                                nToFill,\
                                maxDelayFromStart,\
                                maxDelayFromStart,\
                                avgUploadFromEnd,\
                                avgUploadFromStart,\
                                lastPromptRecoRun)


        pclTagReport = pclTagsJson.getTagReport(pclTag)
        
        htmlwriter.addWorkflow(pclTag, pclTagReport)
        



    


    print '--- last run # in prompt reco: ' + str(lastPromptRecoRun)    






    status = monitorStatus.MonitorStatus('read')
    status.readJsonFile(config.webArea + "status.json")
    
    htmlwriter.setNRunsShown(nToFill)
    htmlwriter.setBackendUpdateDate(status.getField('update'))
    htmlwriter.statusSummary(status.getField('status'),status.getField('msg'))
    #update = datetime.datetime
    update = RunInfo.getDate(status.getField('update'))
    deltatfromend = datetime.datetime.today() - update
#    deltatfromendH = deltatfromend.days*24. + deltatfromend.seconds/(60.*60.)
    #print deltatfromendH
    htmlwriter.setOldUpdateWarning(deltatfromend)




    htmlwriter.buildPage(config.webArea)
