#!/usr/bin/env python
import os
import sys,time
from dbs.apis.dbsClient import DbsApi
from time import gmtime
from ConfigParser import ConfigParser

configfile = ConfigParser()
configfile.optionxform = str
configfile.read('GT_branches/AlCaRecoMonitoring.cfg')
url="https://cmsweb.cern.ch/dbs/prod/global/DBSReader"
api=DbsApi(url=url)

def blockDump(**kwargs):
    return api.blockDump(**kwargs)
    
def help(**kwargs):
    return api.help(**kwargs)
 
def listAcquisitionEras(**kwargs):
   return api.listAcquisitionEras(**kwargs)
   
def listAcquisitionEras_CI(**kwargs):
    return api.listAcquisitionEras_ci(**kwargs)
    
def listDatasets(**kwargs):
    return api.listDatasets(**kwargs)

def listAPIDocumentation():
    return api.listApiDocumentation()
    
def listBlockChildren(**kwargs):
    return api.listBlockChildren(**kwargs)
    
def listBlockOrigin(**kwargs):
    return api.listBlockOrigin(**kwargs)
    
def listBlockParents(**kwargs):
    return api.listBlockParents(**kwargs)
    
def listBlockSummaries(**kwargs):
    return api.listBlockSummaries(**kwargs)
    
def listBlocks(**kwargs):
    return api.listBlocks(**kwargs)
    
def listDataTiers(**kwargs):
    return api.listDataTiers(**kwargs)
    
def listDataTypes(**kwargs):
    return api.listDataTypes(**kwargs)
    
def listDatasetAccessTypes(**kwargs):
    return api.listDatasetAccessTypes(**kwargs)
    
def listDatasetArray (**kwargs):
    return api.listDatasetArray(**kwargs)
    
def listDatasetChildren(**kwargs):
    return api.listDatasetChildren(**kwargs)
    
def listDatasetParents(**kwargs):
    return api.listDatasetParents(**kwargs) 
    
def listFileChildren(*args, **kwargs):
    return api.listFileChildren(*args, **kwargs)
    
def listFileLumis(**kwargs):
    return api.listFileLumis(**kwargs)
    
def listFileParents(*args, **kwargs):
    return api.listFileParents(*args, **kwargs)
    
def listFileSummaries(**kwargs):
    return api.listFileSummaries(**kwargs)
    
def listFiles(**kwargs):
    return api.listFiles(**kwargs)
    
def listOutputConfigs(**kwargs):
    return api.listOutputConfigs(**kwargs)
    
def listPhysicsGroups(**kwargs):
    return api.listPhysicsGroups(**kwargs)
    
def listPrimaryDSTypes(**kwargs):
    return api.listPrimaryDSTypes(**kwargs)    
    
def listPrimaryDatasets(**kwargs):
    return api.listPrimaryDatasets(**kwargs)
    
def listProcessingEras(**kwargs):
    return api.listProcessingEras(**kwargs)
    
def listReleaseVersions(**kwargs):
    return api.listReleaseVersions(**kwargs) 
    
def listRunSummaries(**kwargs):
    return api.listRunSummaries(**kwargs)
    
def listRuns(**kwargs):
    return api.listRuns(**kwargs)
    
def removeMigration(migrationObj):
    return api.removeMigration(migrationObj)
    
def requestContentLength():
    return api.requestContentLength
    
def requestTimingInfo():
    return api.requestTimingInfo
    
def serverinfo():
    return api.serverinfo()
          
def statusMigration(**kwargs):
    return api.statusMigration(**kwargs)
    
def submitMigration(migrationObj):
    return api.submitMigration(migrationObj)
                 
def updateAcqEraEndDate(**kwargs):
    return api.updateAcqEraEndDate(**kwargs)

def updateBlockSiteName(**kwargs):
    return api.updateBlockSiteName(**kwargs)
    
def updateBlockStatus(**kwargs):
    return api.updateBlockStatus(**kwargs)
    
def updateDatasetType(**kwargs):
    return api.updateDatasetType(**kwargs) 
    
def updateFileStatus(*args, **kwargs):  
    return api.updateFIleStatus(*args, **kwargs)
    
            
      
def main():
    webArea = configfile.get('Common','webArea')
    groups = configfile.get('Common','groups').split(",")
    refreshCache = bool(configfile.get('Common','refreshCache'))
    epoch = "HIRun2013A"
    version = "v1"
    tier = "ALCARECO"
  
    datasetList=listDatasets(acquisition_era_name=epoch, data_tier_name = tier)
    
    
    # List all aquisition eras
    print "======== Aquisition Eras ===="
    aqEras = listAquisitionEras()  
    for item in aqEras:
       print item
    
    # List data tiers
    print "=======Data tiers ===="
    dataTiers = listDataTiers()
    for item in dataTiers:
        print item.get('data_tier_name')
        
    # List data types
    print "======= Data types ======"
    dataTypes = listDataTypes()
    for item in dataTypes:
        print item.get('data_type')
       
     # List dataset access types    
    print "====== Dataset Access types ======"
    dataAccessTypes = listDatasetAccessTypes()
    for item in dataAccessTypes:
        print item.get('dataset_access_type')    
    
    
    # List Dataset Children -> prints no children? TODO
    print " ====== Dataset Children ====== "
    datasetChildren = listDatasetChildren(dataset = datasetList[0].get('dataset'))
    for item in datasetChildren:
        print item
    
     # List Dataset Parents -> prints no parents? TODO
    print " ====== Dataset Parents ====== "
    datasetParents = listDatasetParents(dataset = datasetList[0].get('dataset'))
    for item in datasetParents:
        print item
        
    
    # List Dayaset Array
    # TODO: does not work?
    # print "========= List dataset array ========"
    #datasetArray = listDatasetArray(dataset = datasetList)  
    #for it in datasetArray:
    #    print it.get('primary_ds_name')
    # listBlockChildren
    #blockChildren = listBlockChildren(block_name = "HIRun2013A")
    #for item in blockChildren:
    #    print item
     
    # listBlockOrigin
    #blockOrigin = listBlockOrigin()
    #for item in blockOrigin:
    #    print item 
    # list datasets  
   
        
    # print datasets    
   # for item in datasetList:
    #    print item
    
   
           
    # list block names of blocks with given dataset name
    print " ====== PRINTING BLOCKS with dataset = " + datasetList[0].get('dataset') + "======="
    blocks = listBlocks(dataset = datasetList[0].get('dataset'))
    for it in blocks:
       print it.get('block_name')
       
    # List file children of first block item: --> empty: TODO?
    print "====List file children of block: " + blocks[0].get('block_name') + "==="
    file_children = listFileChildren(block_name = blocks[0].get('block_name'))   
    for item in file_children:
        print item    
        
    # List file Lumis of first block item: 
    print "=========    List file Lumis of block: " + blocks[0].get('block_name') + " ======="
    file_Lumis = listFileLumis(block_name = blocks[0].get('block_name'))   
    for item in file_Lumis:
        print item     
    
    # List file parents of first block item:  --> no parent ?
    print "=========    List file parents of block: " + blocks[0].get('block_name') + " ======="
    file_parents = listFileParents(block_name = blocks[0].get('block_name'))   
    for item in file_parents:
        print item     
        
     # List file summaries of first block item: 
    print "=========    List file summaries of block: " + blocks[0].get('block_name') + " ======="
    file_summaries = listFileSummaries(block_name = blocks[0].get('block_name'))   
    for item in file_summaries:
        print item 
                 
    # List files of first block item: 
    print "=========    List files of block: " + blocks[0].get('block_name') + " ======="
    files = listFiles(block_name = blocks[0].get('block_name'))   
    for item in files:
        print item 
      
    # List output configs for first dataset item
    print "====== List output configs for " + datasetList[0].get('dataset') + "   ======"
    configs = listOutputConfigs(dataset = datasetList[0].get('dataset'))
    for item in configs:
        print item    
                
    # List physics groups
    print "====== List physics groups ======"
    physics_groups = listPhysicsGroups()
    for item in physics_groups:
        print item     
        
    # List primary DS types 
    print "====== List primary DS types ======"
    # primary_DS_types = listPrimaryDSTypes()
    # for item in primary_DS_types:
      #   print item 
        
    # List primary datasets
    print "====== List primary datasets ======"
    primary_datasets = listPrimaryDatasets()
   #  for item in primary_datasets:
   #      print item.get('primary_ds_name')        
        
    # List processing eras
    print "====== List processing eras ======"
    processing_eras = listProcessingEras()
    for item in processing_eras:
        print item
        
    # List release version
    print "====== List release version ======"
    release_versions = listReleaseVersions()
    for item in release_versions:
        print item.get('release_version') 
        
    # List run summaries of run_num 1000
    print "======== List run summaries for run_num = 1000 ======="
    run_summaries = listRunSummaries(run_num = 1000)      
    for item in run_summaries:
        print item  
        
    # List runs for the first dataset in the datasetList
    print "======== List runs for dataset: " + datasetList[0].get('dataset') + " ======="
    runs= listRuns(dataset = datasetList[0].get('dataset'))      
    for item in runs:
        print item      
            
    # Request content length
    print "======== Request content length ========="  
    content_length = requestContentLength()
    print content_length
    
    # Request timing info
    print "======== Request timing info ========="
    timing_info = requestTimingInfo()
    print timing_info
          
    # Request server info
    print "======== Request server info ========="
    print serverinfo()
    
    # Check status migration of the first dataset in the dataset list
    # TODO:!!!! HTTP Error 404: Method not found for the verb GET: status
    print " ======== Check status migration of dataset: " + datasetList[0].get('dataset')+ " ========"
    print "TODO: method not recognised: HTTP Error 404: Method not found for the verb GET: status"
    #print statusMigration(dataset = datasetList[0].get('dataset'))
    
    
    # Print Block dump
    print "======== Block dump for block with name " + blocks[0].get('block_name') + " ========="
    print blockDump(block_name = blocks[0].get('block_name'))
     
if __name__ == "__main__":    
    main()
