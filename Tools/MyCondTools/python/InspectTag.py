import datetime

import os,sys, DLFCN
sys.setdlopenflags(DLFCN.RTLD_GLOBAL+DLFCN.RTLD_LAZY)


import pluginCondDBPyInterface as condDB
import CondCore.Utilities.iovInspector as iovInspector




"""
Module providing tools to inspect IOV tags in the DB

$Date: 2013/03/05 15:00:09 $
$Revision: 1.3 $

"""




def getSummaries(tagName, dbName, since, till, logName = 'oracle://cms_orcon_adg/CMS_COND_31X_POPCONLOG', passwdFile = '/afs/cern.ch/cms/DB/conddb'):
    """
    Get the summaries for a given IOV range using the py-wrappers
    """


    try:
        fwkInc = condDB.FWIncantation()
        rdbms = condDB.RDBMS(passwdFile)
        # rdbms.setLogger(logName)
        # import pdb; pdb.set_trace()

        db = rdbms.getReadOnlyDB(dbName)


        db.startReadOnlyTransaction()
        #log = db.lastLogEntry(tagName)
        iovs = iovInspector.Iov(db,tagName, since,till)
        db.commitTransaction()
    except Exception:
        raise 
    else:
        debug = False
        if debug:
            for iovSummary in iovs.summaries():
                print "----- OID: " + iovSummary[0] + " since: " + str(iovSummary[1]) + " till: " + str(iovSummary[2])
                print "Summary:"
                print iovSummary[3]
        return iovs.summaries()

    return None




if __name__ == "__main__":
    print getSummaries(tagName = "SiStripDetVOff_v6_prompt",\
                 dbName = "oracle://cms_orcon_adg/CMS_COND_31X_STRIP",\
                 since = 5813170907986667904,\
                 till = 5813170907986667904)




