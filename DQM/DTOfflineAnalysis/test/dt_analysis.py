import FWCore.ParameterSet.Config as cms

process = cms.Process("DTOffAna")

# the source
process.source = cms.Source("PoolSource",
                            fileNames = cms.untracked.vstring(
           '/store/data/Commissioning10/MinimumBias/RAW-RECO/Apr1Skim_Muon_skim-v1/0139/5C9CA088-B43E-DF11-9BFE-002618FDA210.root',
           '/store/data/Commissioning10/MinimumBias/RAW-RECO/Apr1Skim_Muon_skim-v1/0139/1E042A38-CF3E-DF11-8471-002618943973.root',
           '/store/data/Commissioning10/MinimumBias/RAW-RECO/Apr1Skim_Muon_skim-v1/0139/1896B26A-B03E-DF11-9481-00248C0BE014.root'
                                ))

process.source.inputCommands = cms.untracked.vstring("keep *", "drop *_MEtoEDMConverter_*_*", "drop L1GlobalTriggerObjectMapRecord_hltL1GtObjectMap__HLT")

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(1000)
    )


process.load('Configuration/StandardSequences/MagneticField_AutoFromDBCurrent_cff')
process.load('Configuration/StandardSequences/GeometryIdeal_cff')


process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
process.GlobalTag.globaltag = "GR_R_35X_V8::All"

process.load("Configuration/StandardSequences/RawToDigi_Data_cff")
process.load("Configuration/StandardSequences/Reconstruction_cff")
process.load('Configuration/EventContent/EventContent_cff')

process.FEVTEventContent.outputCommands.append('drop *_MEtoEDMConverter_*_*')

process.load('L1TriggerConfig.L1GtConfigProducers.L1GtTriggerMaskAlgoTrigConfig_cff')
process.load('L1TriggerConfig.L1GtConfigProducers.L1GtTriggerMaskTechTrigConfig_cff')
process.load('HLTrigger/HLTfilters/hltLevel1GTSeed_cfi')



####################################################################################
##################################good collisions############################################

process.L1T1coll=process.hltLevel1GTSeed.clone()
process.L1T1coll.L1TechTriggerSeeding = cms.bool(True)
process.L1T1coll.L1SeedsLogicalExpression = cms.string('0 AND (40 OR 41) AND NOT (36 OR 37 OR 38 OR 39) AND NOT ((42 AND NOT 43) OR (43 AND NOT 42))')

process.l1tcollpath = cms.Path(process.L1T1coll)

process.primaryVertexFilter = cms.EDFilter("VertexSelector",
   src = cms.InputTag("offlinePrimaryVertices"),
   cut = cms.string("!isFake && ndof > 4 && abs(z) <= 15 && position.Rho <= 2"), # tracksSize() > 3 for the older cut
   filter = cms.bool(True),   # otherwise it won't filter the events, just produce an empty vertex collection.
)


process.noscraping = cms.EDFilter("FilterOutScraping",
applyfilter = cms.untracked.bool(True),
debugOn = cms.untracked.bool(False),
numtrack = cms.untracked.uint32(10),
thresh = cms.untracked.double(0.25)
)

process.goodvertex=cms.Path(process.primaryVertexFilter+process.noscraping)


process.collout = cms.OutputModule("PoolOutputModule",
    fileName = cms.untracked.string('good_coll.root'),
    outputCommands = process.FEVTEventContent.outputCommands,
    dataset = cms.untracked.PSet(
    	      dataTier = cms.untracked.string('RAW-RECO'),
    	      filterName = cms.untracked.string('GOODCOLL')),
    SelectEvents = cms.untracked.PSet(
        SelectEvents = cms.vstring('goodvertex','l1tcollpath')
    )
)

# # message logger
# process.MessageLogger = cms.Service("MessageLogger",
#                                      debugModules = cms.untracked.vstring('*'),
#                                      destinations = cms.untracked.vstring('cout'),
#                                      categories = cms.untracked.vstring('DTNoiseAnalysisTest'), 
#                                      cout = cms.untracked.PSet(threshold = cms.untracked.string('DEBUG'),
#                                                                noLineBreaks = cms.untracked.bool(False),
#                                                                DEBUG = cms.untracked.PSet(
#                                                                        limit = cms.untracked.int32(0)),
#                                                                INFO = cms.untracked.PSet(
#                                                                        limit = cms.untracked.int32(0)),
#                                                                DTNoiseAnalysisTest = cms.untracked.PSet(
#                                                                                   limit = cms.untracked.int32(-1))
#                                                                )
#                                      )



process.outpath = cms.EndPath(process.collout)

process.options = cms.untracked.PSet(
    wantSummary = cms.untracked.bool(True)
    )



# process.jobPath = cms.Path(process.reco + process.dtLocalRecoAnal)

#process.jobPath = cms.Path(process.dtLocalRecoAnal)


#f = file('aNewconfigurationFile.cfg', 'w')
#f.write(process.dumpConfig())
#f.close()

