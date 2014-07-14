#!/usr/bin/env python
"""

 DBS 3 Client Example.   This script is called 

./dbs3Example.py '/*/*Fall13-POST*/GEN-SIM'

"""

import  sys,time
from dbs.apis.dbsClient import DbsApi
from time import gmtime

def main():
    args=sys.argv[1:]
    data=args[0]
    data1='/*/*/*'
    sdays=86400  
    len=90
    now = time.time() 
    then = now - sdays*len
    print data
    url="https://cmsweb.cern.ch/dbs/prod/global/DBSReader"
    api=DbsApi(url=url)
    aquisitionEras = api.listlistAcquisitionEras()
    for aq_era in aquisitionEras:
        print "====Aquisition Era:   " + aq_era
        PD = api.listPrimaryDatasets()
    outputDataSetsValid = api.listDatasets(dataset=data1,detail=1, dataset_access_type="VALID")
    outputDataSetsProd = api.listDatasets(dataset=data,detail=1, dataset_access_type="PRODUCTION")
    outputDataSets = outputDataSetsValid + outputDataSetsProd
#    outputDataSets = outputDataSetsValid
    f = []

    for i in range(len):
       f.append(0)

    for dataset in outputDataSets:
       inp=dataset['dataset']
#       print "INSIDE"
#       print inp
       ct = dataset['creation_date']
       if ct > (then-30*sdays):
           print inp
           blocks = api.listBlocks(dataset=inp, detail=True)
           for block in blocks:
               reply= api.listBlockSummaries(block_name=block['block_name'])
               neventsb= reply[0]['num_event']
               reply=api.listFiles(block_name=block['block_name'],detail=True)
               ct=reply[0]['last_modification_date']
               for x in range (len):
                   tnow = now - (len-x)*86400
                   if ct > then and ct < tnow:
                       f[x]=f[x]+ neventsb
    for i in range(len):
       print f[i] 
    sys.exit(0);

if __name__ == "__main__":
    main()
    sys.exit(0);
