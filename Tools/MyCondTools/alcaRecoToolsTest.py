import Tools.MyCondTools.tableWriter as tableWriter
import commands
import os
import datetime
from ROOT import *
from dbs.apis.dbsClient import DbsApi


def getDatasets(pd, epoch, version, tier):

    url="https://cmsweb.cern.ch/dbs/prod/global/DBSReader"
    api=DbsApi(url=url)

    primaryDatasets = api.listPrimaryDatasets(primary_ds_name = pd)
    for pit in primaryDatasets:
       print pit.get("primary_ds_name")
