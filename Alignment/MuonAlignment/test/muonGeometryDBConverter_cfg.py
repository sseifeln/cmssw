from __future__ import print_function
import FWCore.ParameterSet.Config as cms
import FWCore.ParameterSet.VarParsing as VarParsing


################################################################################
# command line options
options = VarParsing.VarParsing()
options.register('input',
                 default = "ideal",
                 mytype = VarParsing.VarParsing.varType.string,
                 info = "input format")
options.register('inputFile',
                 default = None,
                 mytype = VarParsing.VarParsing.varType.string,
                 info = "input file name")
options.register('output',
                 default = "none",
                 mytype = VarParsing.VarParsing.varType.string,
                 info = "output format")
options.register('outputFile',
                 default = None,
                 mytype = VarParsing.VarParsing.varType.string,
                 info = "output file name")
options.parseArguments()

################################################################################
# setting up the process
process = cms.Process("CONVERT")
process.load("Configuration.StandardSequences.MagneticField_cff")
process.load("Configuration.Geometry.GeometryIdeal_cff")
process.load("Geometry.MuonNumbering.muonNumberingInitialization_cfi")
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
process.load("Alignment.MuonAlignment.muonGeometryDBConverter_cfi")

################################################################################
# parameters to configure:
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, "auto:phase1_2017_design")
process.muonGeometryDBConverter.input = options.input
process.muonGeometryDBConverter.output = options.output

if options.input == "db":
    process.GlobalTag.toGet.extend(
        [cms.PSet(connect = cms.string("sqlite_file:"+options.inputFile),
                  record = cms.string("DTAlignmentRcd"),
                  tag = cms.string("DTAlignmentRcd")),
         cms.PSet(connect = cms.string("sqlite_file:"+options.inputFile),
                  record = cms.string("DTAlignmentErrorExtendedRcd"),
                  tag = cms.string("DTAlignmentErrorExtendedRcd")),
         cms.PSet(connect = cms.string("sqlite_file:"+options.inputFile),
                  record = cms.string("CSCAlignmentRcd"),
                  tag = cms.string("CSCAlignmentRcd")),
         cms.PSet(connect = cms.string("sqlite_file:"+options.inputFile),
                  record = cms.string("CSCAlignmentErrorExtendedRcd"),
                  tag = cms.string("CSCAlignmentErrorExtendedRcd"))
        ])
elif options.input == "xml":
    process.muonGeometryDBConverter.fileName = options.inputFile

if options.output == "db":
    from CondCore.CondDB.CondDB_cfi import CondDB
    process.PoolDBOutputService = cms.Service(
        "PoolDBOutputService",
        CondDB,
        toPut = cms.VPSet(
            cms.PSet(record = cms.string("DTAlignmentRcd"),
                     tag = cms.string("DTAlignmentRcd")),
            cms.PSet(record = cms.string("DTAlignmentErrorExtendedRcd"),
                     tag = cms.string("DTAlignmentErrorExtendedRcd")),
            cms.PSet(record = cms.string("CSCAlignmentRcd"),
                     tag = cms.string("CSCAlignmentRcd")),
            cms.PSet(record = cms.string("CSCAlignmentErrorExtendedRcd"),
                     tag = cms.string("CSCAlignmentErrorExtendedRcd")),
        )
    )
    process.PoolDBOutputService.connect = "sqlite_file:"+options.outputFile
elif options.output == "xml":
    process.muonGeometryDBConverter.outputXML.fileName = options.outputFile
    process.muonGeometryDBConverter.outputXML.suppressDTSuperLayers = True
    process.muonGeometryDBConverter.outputXML.suppressDTLayers = True
    process.muonGeometryDBConverter.outputXML.suppressCSCLayers = True


################################################################################

usedGlobalTag = process.GlobalTag.globaltag.value()
print("Using Global Tag:", usedGlobalTag)

process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(1))
process.source = cms.Source("EmptySource")
process.p = cms.Path(process.muonGeometryDBConverter)
