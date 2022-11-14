import os
import re
import subprocess
import tempfile
import shutil
import pandas as pd
from xml.dom import minidom as xmlbuilder


## VIASH START
par = {
   "input": ["resources_test/maxquant_demo_files/raw/Sample.raw"],
   "reference": "resources_test/maxquant_demo_files/raw/reference.fasta",
   "output": "output/",
   "match_between_runs": True
}
meta = {
   "resources_dir": "src/maxquant/maxquant/"
}
## VIASH END

#########################################################################################################################################
#TODO MOVE IN OWN FILE?

def generateMaxquantParametersXML():
    global xml
    xml = xmlbuilder.Document() 
    global parameters
    parameters={}
    global fastas
    fastas=[]

    #CREATE ROOT STRUCTURE
    global maxQuantParams
    maxQuantParams = xml.createElement('MaxQuantParams') 
    maxQuantParams.setAttribute('xmlns:xsd','http://www.w3.org/2001/XMLSchema')
    maxQuantParams.setAttribute('xmlns:xsi','http://www.w3.org/2001/XMLSchema-instance')
    xml.appendChild(maxQuantParams)
    
    #CREATE FASTA SECTION
    global fastaFileParamsEl
    fastaFileParamsEl = xml.createElement('fastaFiles') 
    maxQuantParams.appendChild(fastaFileParamsEl)
 
    #CREATE DEFAULT PARAMETERS
    addDefaultParameters(maxQuantParams)

    #CREATE PARAMETER GROUPS
    global parameterGroupsEl
    parameterGroupsEl = xml.createElement('parameterGroups')
    maxQuantParams.appendChild(parameterGroupsEl) 
    addParameterGroup()
    
    #CREATE MSMS PARAMETER ARRAY
    global msmsParamArrayEl 
    msmsParamArrayEl= xml.createElement('msmsParamsArray')
    maxQuantParams.appendChild(msmsParamArrayEl) 
    addMassSpecType('FTMS',[20,True,7,True,25,True,True,12,100,True,True,True,True,False])
    addMassSpecType('ITMS',[0.5,False,0.15,False,0.5,False,False,8,100,True,True,True,True,False])
    addMassSpecType('TOF',[40,True,0.01,False,25,True,True,10,100,True,True,True,True,False])
    addMassSpecType('Unknown',[20,True,7,True,25,True,True,12,100,True,True,True,True,False])

    #CREATE FRAGMENTATION PARAMETER ARRAY
    global fragParamArrayEl 
    fragParamArrayEl= xml.createElement('fragmentationParamsArray')
    maxQuantParams.appendChild(fragParamArrayEl) 
    addFragmentationType('CID',[False,1,1,1,False,1,'KRH'])
    addFragmentationType('HCD',[False,1,1,1,False,1,'KRH'])
    addFragmentationType('ETD',[False,1,1,1,False,1,'KRH'])
    addFragmentationType('PQD',[False,1,1,1,False,1,'KRH'])
    addFragmentationType('ETHCD',[False,1,1,1,False,1,'KRH'])
    addFragmentationType('ETCID',[False,1,1,1,False,1,'KRH'])
    addFragmentationType('UVPD',[False,1,1,1,False,1,'KRH'])
    addFragmentationType('Unknown',[False,1,1,1,False,1,'KRH'])

def createParameter(parameterParent,parameterName,parameterValue,parameterPrefix=''):
    parameterEL=xml.createElement(parameterName)
    parameterElValue=xml.createTextNode(str(parameterValue))
    parameterEL.appendChild(parameterElValue)
    parameterParent.appendChild(parameterEL)
    parameters[parameterPrefix+parameterName]=parameterEL

def updateParameter(parameterName,parameterValue):
    if(not parameterName in parameters):
     createParameter(maxQuantParams,parameterName,parameterValue)
    parameters[parameterName].firstChild.replaceWholeText(parameterValue)
       
def addFastaFile(fastaFilePath,taxonomyId=""):
    fastaFileIndex=len(fastas)
    fastas.append(fastaFilePath)
    fastaFileInfoEl = xml.createElement('FastaFileInfo')
    fastaFileParamsEl.appendChild(fastaFileInfoEl) 
    prefix=str(fastaFileIndex)+"_"
    createParameter(fastaFileInfoEl,'fastaFilePath',fastaFilePath,prefix)
    createParameter(fastaFileInfoEl,'identifierParseRule','>.*\|(.*)\|',prefix)
    createParameter(fastaFileInfoEl,'descriptionParseRule','>(.*)',prefix)
    createParameter(fastaFileInfoEl,'taxonomyParseRule',"",prefix)
    createParameter(fastaFileInfoEl,'variationParseRule',"",prefix)
    createParameter(fastaFileInfoEl,'modificationParseRule',"",prefix)
    createParameter(fastaFileInfoEl,'taxonomyId',taxonomyId,prefix)

def addDefaultParameters(parameterParent):
   createParameter(parameterParent,"fastaFilesProteogenomics","")
   createParameter(parameterParent,"fastaFilesFirstSearch","")
   createParameter(parameterParent,"fixedSearchFolder","")
   createParameter(parameterParent,'andromedaCacheSize','350000')
   createParameter(parameterParent,'advancedRatios','True')
   createParameter(parameterParent,'pvalThres','0.005')
   createParameter(parameterParent,'rtShift','False')
   createParameter(parameterParent,'separateLfq','False')
   createParameter(parameterParent,'lfqStabilizeLargeRatios','True')
   createParameter(parameterParent,'lfqRequireMsms','True')
   createParameter(parameterParent,'lfqBayesQuant','False')
   createParameter(parameterParent,'decoyMode','revert')
   createParameter(parameterParent,'boxCarMode','all')
   createParameter(parameterParent,'includeContaminants','True')
   createParameter(parameterParent,'maxPeptideMass','4600')
   createParameter(parameterParent,'epsilonMutationScore','True')
   createParameter(parameterParent,'mutatedPeptidesSeparately','True')
   createParameter(parameterParent,'proteogenomicPeptidesSeparately','True')
   createParameter(parameterParent,'minDeltaScoreUnmodifiedPeptides','0')
   createParameter(parameterParent,'minDeltaScoreModifiedPeptides','6')
   createParameter(parameterParent,'minScoreUnmodifiedPeptides','0')
   createParameter(parameterParent,'minScoreModifiedPeptides','40')
   createParameter(parameterParent,'secondPeptide','True')
   createParameter(parameterParent,'matchBetweenRuns','True')
   createParameter(parameterParent,'matchUnidentifiedFeatures','False')
   createParameter(parameterParent,'matchBetweenRunsFdr','False')
   createParameter(parameterParent,'dependentPeptides','False')
   createParameter(parameterParent,'dependentPeptideFdr','0')
   createParameter(parameterParent,'dependentPeptideMassBin','0')
   createParameter(parameterParent,'dependentPeptidesBetweenRuns','False')
   createParameter(parameterParent,'dependentPeptidesWithinExperiment','False')
   createParameter(parameterParent,'dependentPeptidesWithinParameterGroup','False')
   createParameter(parameterParent,'dependentPeptidesRestrictFractions','False')
   createParameter(parameterParent,'dependentPeptidesFractionDifference','0')
   createParameter(parameterParent,'ibaq','False')
   createParameter(parameterParent,'top3','False')
   createParameter(parameterParent,'independentEnzymes','False')
   createParameter(parameterParent,'useDeltaScore','False')
   createParameter(parameterParent,'splitProteinGroupsByTaxonomy','False')
   createParameter(parameterParent,'taxonomyLevel','Species')
   createParameter(parameterParent,'avalon','False')
   createParameter(parameterParent,'nModColumns','3')
   createParameter(parameterParent,'ibaqLogFit','False')
   createParameter(parameterParent,'ibaqChargeNormalization','False')
   createParameter(parameterParent,'razorProteinFdr','True')
   createParameter(parameterParent,'deNovoSequencing','False')
   createParameter(parameterParent,'deNovoVarMods','False')
   createParameter(parameterParent,'deNovoCompleteSequence','False')
   createParameter(parameterParent,'deNovoCalibratedMasses','False')
   createParameter(parameterParent,'deNovoMaxIterations','0')
   createParameter(parameterParent,'deNovoProteaseReward','0')
   createParameter(parameterParent,'deNovoProteaseRewardTof','0')
   createParameter(parameterParent,'deNovoAgPenalty','0')
   createParameter(parameterParent,'deNovoGgPenalty','0')
   createParameter(parameterParent,'deNovoUseComplementScore','True')
   createParameter(parameterParent,'deNovoUseProteaseScore','True')
   createParameter(parameterParent,'deNovoUseWaterLossScore','True')
   createParameter(parameterParent,'deNovoUseAmmoniaLossScore','True')
   createParameter(parameterParent,'deNovoUseA2Score','True')
   createParameter(parameterParent,'massDifferenceSearch','False')
   createParameter(parameterParent,'isotopeCalc','False')
   createParameter(parameterParent,'writePeptidesForSpectrumFile','')
   createParameter(parameterParent,'intensityPredictionsFile','')
   createParameter(parameterParent,'minPepLen','7')
   createParameter(parameterParent,'psmFdrCrosslink','0.01')
   createParameter(parameterParent,'peptideFdr','0.01')
   createParameter(parameterParent,'proteinFdr','0.01')
   createParameter(parameterParent,'siteFdr','0.01')
   createParameter(parameterParent,'minPeptideLengthForUnspecificSearch','8')
   createParameter(parameterParent,'maxPeptideLengthForUnspecificSearch','25')
   createParameter(parameterParent,'useNormRatiosForOccupancy','True')
   createParameter(parameterParent,'minPeptides','1')
   createParameter(parameterParent,'minRazorPeptides','1')
   createParameter(parameterParent,'minUniquePeptides','0')
   createParameter(parameterParent,'useCounterparts','False')
   createParameter(parameterParent,'advancedSiteIntensities','True')
   createParameter(parameterParent,'customProteinQuantification','False')
   createParameter(parameterParent,'customProteinQuantificationFile','')
   createParameter(parameterParent,'minRatioCount','2')
   createParameter(parameterParent,'restrictProteinQuantification','True')

   restrictionModsEl = xml.createElement('restrictMods')
   maxQuantParams.appendChild(restrictionModsEl) 
   createParameter(restrictionModsEl,'string','Oxidation (M)')
   createParameter(restrictionModsEl,'string','Acetyl (Protein N-term)')

   createParameter(maxQuantParams,'matchingTimeWindow','0.7')
   createParameter(maxQuantParams,'matchingIonMobilityWindow','0.05')
   createParameter(maxQuantParams,'alignmentTimeWindow','20')
   createParameter(maxQuantParams,'alignmentIonMobilityWindow','1')
   createParameter(maxQuantParams,'numberOfCandidatesMsms','15')
   createParameter(maxQuantParams,'compositionPrediction','0')
   createParameter(maxQuantParams,'quantMode','1')
   createParameter(maxQuantParams,'massDifferenceMods','')
   createParameter(maxQuantParams,'mainSearchMaxCombinations','200')
   createParameter(maxQuantParams,'writeMsScansTable','True')
   createParameter(maxQuantParams,'writeMsmsScansTable','True')
   createParameter(maxQuantParams,'writePasefMsmsScansTable','True')
   createParameter(maxQuantParams,'writeAccumulatedMsmsScansTable','True')
   createParameter(maxQuantParams,'writeMs3ScansTable','True')
   createParameter(maxQuantParams,'writeAllPeptidesTable','True')
   createParameter(maxQuantParams,'writeMzRangeTable','True')
   createParameter(maxQuantParams,'writeDiaFragmentTable','True')
   createParameter(maxQuantParams,'writeDiaFragmentQuantTable','True')
   createParameter(maxQuantParams,'writeMzTab','True')
   createParameter(maxQuantParams,'disableMd5','False')
   createParameter(maxQuantParams,'cacheBinInds','True')
   createParameter(maxQuantParams,'etdIncludeB','False')
   createParameter(maxQuantParams,'ms2PrecursorShift','0')
   createParameter(maxQuantParams,'complementaryIonPpm','20')
   createParameter(maxQuantParams,'variationParseRule','')
   createParameter(maxQuantParams,'variationMode','none')
   createParameter(maxQuantParams,'useSeriesReporters','False')
   createParameter(maxQuantParams,'name','session1')
   createParameter(maxQuantParams,'maxQuantVersion','2.0.3.0')
   createParameter(maxQuantParams,'pluginFolder','')
   createParameter(maxQuantParams,'numThreads','1')
   createParameter(maxQuantParams,'emailAddress','')
   createParameter(maxQuantParams,'smtpHost','')
   createParameter(maxQuantParams,'emailFromAddress','')
   createParameter(maxQuantParams,'fixedCombinedFolder','')
   createParameter(maxQuantParams,'fullMinMz','-1.79769313486232E+308')
   createParameter(maxQuantParams,'fullMaxMz','1.79769313486232E+308')
   createParameter(maxQuantParams,'sendEmail','False')
   createParameter(maxQuantParams,'ionCountIntensities','False')
   createParameter(maxQuantParams,'verboseColumnHeaders','False')
   createParameter(maxQuantParams,'calcPeakProperties','True')
   createParameter(maxQuantParams,'showCentroidMassDifferences','False')
   createParameter(maxQuantParams,'showIsotopeMassDifferences','False')
   createParameter(maxQuantParams,'useDotNetCore','True')
   createParameter(maxQuantParams,'profilePerformance','False')

   global filePaths
   filePaths = xml.createElement('filePaths')
   maxQuantParams.appendChild(filePaths) 

   global experiments
   experiments = xml.createElement('experiments')
   maxQuantParams.appendChild(experiments) 

   global fractions
   fractions = xml.createElement('fractions')
   maxQuantParams.appendChild(fractions) 

   global ptms
   ptms = xml.createElement('ptms')
   maxQuantParams.appendChild(ptms) 

   global paramGroupIndices
   paramGroupIndices = xml.createElement('paramGroupIndices')
   maxQuantParams.appendChild(paramGroupIndices) 

   global referenceChannels
   referenceChannels = xml.createElement('referenceChannel')
   maxQuantParams.appendChild(referenceChannels) 


   createParameter(maxQuantParams,'intensPred','False')
   createParameter(maxQuantParams,'intensPredModelReTrain','False')
   createParameter(maxQuantParams,'lfqTopNPeptides','0')
   createParameter(maxQuantParams,'diaJoinPrecChargesForLfq','False')
   createParameter(maxQuantParams,'diaFragChargesForQuant','1')
   createParameter(maxQuantParams,'timsRearrangeSpectra','False')
   createParameter(maxQuantParams,'gridSpacing','0.5')
   createParameter(maxQuantParams,'proteinGroupingFile','')

def addParameterGroup():
   parameterParent = xml.createElement('parameterGroup')
   parameterGroupsEl.appendChild(parameterParent) 
   createParameter(parameterParent,'msInstrument','0')
   createParameter(parameterParent,'maxCharge','7')
   createParameter(parameterParent,'minPeakLen','2')
   createParameter(parameterParent,'diaMinPeakLen','1')
   createParameter(parameterParent,'useMs1Centroids','False')
   createParameter(parameterParent,'useMs2Centroids','False')
   createParameter(parameterParent,'cutPeaks','True')
   createParameter(parameterParent,'gapScans','1')
   createParameter(parameterParent,'minTime','NaN')
   createParameter(parameterParent,'maxTime','NaN')
   createParameter(parameterParent,'matchType','MatchFromAndTo')
   createParameter(parameterParent,'intensityDetermination','0')
   createParameter(parameterParent,'centroidMatchTol','8')
   createParameter(parameterParent,'centroidMatchTolInPpm','True')
   createParameter(parameterParent,'centroidHalfWidth','35')
   createParameter(parameterParent,'centroidHalfWidthInPpm','True')
   createParameter(parameterParent,'valleyFactor','1.4')
   createParameter(parameterParent,'isotopeValleyFactor','1.2')
   createParameter(parameterParent,'advancedPeakSplitting','False')
   createParameter(parameterParent,'intensityThresholdMs1','0')
   createParameter(parameterParent,'intensityThresholdMs2','0')

   labelMods = xml.createElement('labelMods')
   parameterParent.appendChild(labelMods) 
   createParameter(labelMods,"string",'')

   createParameter(parameterParent,'lcmsRunType','Standard')
   createParameter(parameterParent,'reQuantify','False')
   createParameter(parameterParent,'lfqMode','1')
   createParameter(parameterParent,'lfqNormClusterSize','80')
   createParameter(parameterParent,'lfqMinEdgesPerNode','3')
   createParameter(parameterParent,'lfqAvEdgesPerNode','6')
   createParameter(parameterParent,'lfqMaxFeatures','100000')
   createParameter(parameterParent,'neucodeMaxPpm','0')
   createParameter(parameterParent,'neucodeResolution','0')
   createParameter(parameterParent,'neucodeResolutionInMda','False')
   createParameter(parameterParent,'neucodeInSilicoLowRes','False')
   createParameter(parameterParent,'fastLfq','True')
   createParameter(parameterParent,'lfqRestrictFeatures','False')
   createParameter(parameterParent,'lfqMinRatioCount','2')
   createParameter(parameterParent,'maxLabeledAa','0')
   createParameter(parameterParent,'maxNmods','5')
   createParameter(parameterParent,'maxMissedCleavages','2')
   createParameter(parameterParent,'multiplicity','1')
   createParameter(parameterParent,'enzymeMode','0')
   createParameter(parameterParent,'complementaryReporterType','0')
   createParameter(parameterParent,'reporterNormalization','0')
   createParameter(parameterParent,'neucodeIntensityMode','0')

   fixedModifications = xml.createElement('fixedModifications')
   parameterParent.appendChild(fixedModifications) 
   createParameter(fixedModifications,"string",'Carbamidomethyl (C)')

   enzymes = xml.createElement('enzymes')
   parameterParent.appendChild(enzymes) 
   createParameter(enzymes,"string",'Trypsin/P')
   createParameter(parameterParent,"enzymesFirstSearch",'')
   createParameter(parameterParent,"enzymeModeFirstSearch",'0')
   createParameter(parameterParent,"useEnzymeFirstSearch",'False')
   createParameter(parameterParent,"useVariableModificationsFirstSearch",'False')

   variableModifications = xml.createElement('variableModifications')
   parameterParent.appendChild(variableModifications) 
   createParameter(variableModifications,"string",'Oxidation (M)')
   createParameter(variableModifications,"string",'Acetyl (Protein N-term)')

   createParameter(parameterParent,'useMultiModification','False')
   createParameter(parameterParent,'multiModifications','')
   createParameter(parameterParent,'isobaricLabels','')
   createParameter(parameterParent,'neucodeLabels','')
   createParameter(parameterParent,'variableModificationsFirstSearch','')
   createParameter(parameterParent,'hasAdditionalVariableModifications','False')
   createParameter(parameterParent,'additionalVariableModifications','')
   createParameter(parameterParent,'additionalVariableModificationProteins','')
   createParameter(parameterParent,'doMassFiltering','True')
   createParameter(parameterParent,'firstSearchTol','20')
   createParameter(parameterParent,'mainSearchTol','4.5')
   createParameter(parameterParent,'searchTolInPpm','True')
   createParameter(parameterParent,'isotopeMatchTol','2')
   createParameter(parameterParent,'isotopeMatchTolInPpm','True')
   createParameter(parameterParent,'isotopeTimeCorrelation','0.6')
   createParameter(parameterParent,'theorIsotopeCorrelation','0.6')
   createParameter(parameterParent,'checkMassDeficit','True')
   createParameter(parameterParent,'recalibrationInPpm','True')
   createParameter(parameterParent,'intensityDependentCalibration','False')
   createParameter(parameterParent,'minScoreForCalibration','70')
   createParameter(parameterParent,'matchLibraryFile','False')
   createParameter(parameterParent,'libraryFile','')
   createParameter(parameterParent,'matchLibraryMassTolPpm','0')
   createParameter(parameterParent,'matchLibraryTimeTolMin','0')
   createParameter(parameterParent,'matchLabelTimeTolMin','0')
   createParameter(parameterParent,'reporterMassTolerance','NaN')
   createParameter(parameterParent,'reporterPif','NaN')
   createParameter(parameterParent,'filterPif','False')
   createParameter(parameterParent,'reporterFraction','NaN')
   createParameter(parameterParent,'reporterBasePeakRatio','NaN')
   createParameter(parameterParent,'timsHalfWidth','0')
   createParameter(parameterParent,'timsStep','0')
   createParameter(parameterParent,'timsResolution','0')
   createParameter(parameterParent,'timsMinMsmsIntensity','0')
   createParameter(parameterParent,'timsRemovePrecursor','True')
   createParameter(parameterParent,'timsIsobaricLabels','False')
   createParameter(parameterParent,'timsCollapseMsms','True')
   createParameter(parameterParent,'crossLinkingType','0')
   createParameter(parameterParent,'crossLinker','')

   createParameter(parameterParent,'minMatchXl','3')
   createParameter(parameterParent,'minPairedPepLenXl','6')
   createParameter(parameterParent,'minScore_Dipeptide','40')
   createParameter(parameterParent,'minScore_Monopeptide','0')
   createParameter(parameterParent,'minScore_PartialCross','10')
   createParameter(parameterParent,'crosslinkOnlyIntraProtein','False')
   createParameter(parameterParent,'crosslinkIntensityBasedPrecursor','True')
   createParameter(parameterParent,'isHybridPrecDetermination','False')
   createParameter(parameterParent,'topXcross','3')
   createParameter(parameterParent,'doesSeparateInterIntraProteinCross','False')
   createParameter(parameterParent,'crosslinkMaxMonoUnsaturated','0')
   createParameter(parameterParent,'crosslinkMaxMonoSaturated','0')
   createParameter(parameterParent,'crosslinkMaxDiUnsaturated','0')
   createParameter(parameterParent,'crosslinkMaxDiSaturated','0')
   createParameter(parameterParent,'crosslinkModifications','')
   createParameter(parameterParent,'crosslinkFastaFiles','')
   createParameter(parameterParent,'crosslinkSites','')
   createParameter(parameterParent,'crosslinkNetworkFiles','')
   createParameter(parameterParent,'crosslinkMode','')
   createParameter(parameterParent,'peakRefinement','False')
   createParameter(parameterParent,'isobaricSumOverWindow','True')
   createParameter(parameterParent,'isobaricWeightExponent','0.75')
   createParameter(parameterParent,'collapseMsmsOnIsotopePatterns','False')
   createParameter(parameterParent,'diaLibraryType','0')
   createParameter(parameterParent,'diaLibraryPaths','')
   createParameter(parameterParent,'diaPeptidePaths','')
   createParameter(parameterParent,'diaEvidencePaths','')
   createParameter(parameterParent,'diaMsmsPaths','')
   createParameter(parameterParent,'diaInitialPrecMassTolPpm','20')
   createParameter(parameterParent,'diaInitialFragMassTolPpm','20')
   createParameter(parameterParent,'diaCorrThresholdFeatureClustering','0.85')
   createParameter(parameterParent,'diaPrecTolPpmFeatureClustering','2')
   createParameter(parameterParent,'diaFragTolPpmFeatureClustering','2')
   createParameter(parameterParent,'diaScoreN','7')
   createParameter(parameterParent,'diaMinScore','1.99')
   createParameter(parameterParent,'diaXgBoostBaseScore','0.4')
   createParameter(parameterParent,'diaXgBoostSubSample','0.9')
   createParameter(parameterParent,'centroidPosition','0')
   createParameter(parameterParent,'diaQuantMethod','7')
   createParameter(parameterParent,'diaFeatureQuantMethod','2')
   createParameter(parameterParent,'lfqNormType','1')
   createParameter(parameterParent,'diaTopNForQuant','10')
   createParameter(parameterParent,'diaMinMsmsIntensityForQuant','0')
   createParameter(parameterParent,'diaTopMsmsIntensityQuantileForQuant','0.85')
   createParameter(parameterParent,'diaPrecursorFilterType','0')
   createParameter(parameterParent,'diaMinFragmentOverlapScore','1')
   createParameter(parameterParent,'diaMinPrecursorScore','0.5')
   createParameter(parameterParent,'diaMinProfileCorrelation','0')
   createParameter(parameterParent,'diaXgBoostMinChildWeight','9')
   createParameter(parameterParent,'diaXgBoostMaximumTreeDepth','12')
   createParameter(parameterParent,'diaXgBoostEstimators','580')
   createParameter(parameterParent,'diaXgBoostGamma','0.9')
   createParameter(parameterParent,'diaXgBoostMaxDeltaStep','3')
   createParameter(parameterParent,'diaGlobalMl','True')
   createParameter(parameterParent,'diaAdaptiveMassAccuracy','False')
   createParameter(parameterParent,'diaMassWindowFactor','3.3')
   createParameter(parameterParent,'diaRtPrediction','False')
   createParameter(parameterParent,'diaRtPredictionSecondRound','False')
   createParameter(parameterParent,'diaNoMl','False')
   createParameter(parameterParent,'diaPermuteRt','False')
   createParameter(parameterParent,'diaPermuteCcs','False')
   createParameter(parameterParent,'diaBackgroundSubtraction','False')
   createParameter(parameterParent,'diaBackgroundSubtractionQuantile','0.5')
   createParameter(parameterParent,'diaBackgroundSubtractionFactor','4')
   createParameter(parameterParent,'diaLfqWeightedMedian','False')
   createParameter(parameterParent,'diaTransferQvalue','0.3')
   createParameter(parameterParent,'diaOnlyIsosForRecal','True')
   createParameter(parameterParent,'diaMinPeaksForRecal','5')
   createParameter(parameterParent,'diaUseFragIntensForMl','False')
   createParameter(parameterParent,'diaUseFragMassesForMl','False')
   createParameter(parameterParent,'diaMaxTrainInstances','1000000')

def addMassSpecType(name,values):
    prefix=name+"_"
    msmsParams = xml.createElement('msmsParams')
    msmsParamArrayEl.appendChild(msmsParams) 
    createParameter(msmsParams,'Name', name,prefix)
    createParameter(msmsParams,'MatchTolerance',str(values[0]),prefix)
    createParameter(msmsParams,'MatchToleranceInPpm',str(values[1]),prefix)
    createParameter(msmsParams,'DeisotopeTolerance',str(values[2]),prefix)
    createParameter(msmsParams,'DeisotopeToleranceInPpm',str(values[3]),prefix)
    createParameter(msmsParams,'DeNovoTolerance',str(values[4]),prefix)
    createParameter(msmsParams,'DeNovoToleranceInPpm',str(values[5]),prefix)
    createParameter(msmsParams,'Deisotope',str(values[6]),prefix)
    createParameter(msmsParams,'Topx',str(values[7]),prefix)
    createParameter(msmsParams,'TopxInterval',str(values[8]),prefix)
    createParameter(msmsParams,'HigherCharges',str(values[9]),prefix)
    createParameter(msmsParams,'IncludeWater',str(values[10]),prefix)
    createParameter(msmsParams,'IncludeAmmonia',str(values[11]),prefix)
    createParameter(msmsParams,'DependentLosses',str(values[12]),prefix)
    createParameter(msmsParams,'Recalibration',str(values[13]),prefix)

def addFragmentationType(name,values):
    prefix=name+"_"
    fragmentationParams = xml.createElement('fragmentationParams')
    fragParamArrayEl.appendChild(fragmentationParams) 
    createParameter(fragmentationParams,'Name', name,prefix)
    createParameter(fragmentationParams,'Connected',str(values[0]),prefix)
    createParameter(fragmentationParams,'ConnectedScore0',str(values[1]),prefix)
    createParameter(fragmentationParams,'ConnectedScore1',str(values[2]),prefix)
    createParameter(fragmentationParams,'ConnectedScore2',str(values[3]),prefix)
    createParameter(fragmentationParams,'InternalFragments',str(values[4]),prefix)
    createParameter(fragmentationParams,'InternalFragmentWeight',str(values[5]),prefix)
    createParameter(fragmentationParams,'InternalFragmentAas',str(values[6]),prefix)

def toString():
   nativeXML = xml.toprettyxml(indent ="   ",).replace("&gt;",">").replace("&lt;","<")
   nativeXML=nativeXML.replace('<?xml version="1.0"','<?xml version="1.0" encoding="utf-8"')
   return nativeXML

#########################################################################################################################################

# if par_input is a directory, look for raw files
if len(par["input"]) == 1 and os.path.isdir(par["input"][0]):
   par["input"] = [ os.path.join(dp, f) for dp, dn, filenames in os.walk(par["input"]) for f in filenames if re.match(r'.*\.raw', f) ]

# set taxonomy id to empty string if not specified
if not par["ref_taxonomy_id"]:
   par["ref_taxonomy_id"] = [ "" for ref in par["reference"] ]

# use absolute paths
par["input"] = [ os.path.abspath(f) for f in par["input"] ]
par["reference"] = [ os.path.abspath(f) for f in par["reference"] ]
par["output"] = os.path.abspath(par["output"])

# auto set experiment names
experiment_names = [ re.sub(r"_\d+$", "", os.path.basename(file)) for file in par["input"] ]

# load default matching settings
match_between_runs_settings = pd.read_table(
   meta["resources_dir"] + "/settings/match_between_runs.tsv",
   sep="\t",
   index_col="id",
   dtype=str,
   keep_default_na=False,
   na_values=['_']
)

# load default instrument settings
ms_instrument_settings = pd.read_table(
   meta["resources_dir"] + "/settings/ms_instrument.tsv",
   sep="\t",
   index_col="id",
   dtype=str,
   keep_default_na=False,
   na_values=['_']
)

# load default group type settings
group_type_settings = pd.read_table(
   meta["resources_dir"] + "/settings/group_type.tsv",
   sep="\t",
   index_col="id",
   dtype=str,
   keep_default_na=False,
   na_values=['_']
)

# check reference metadata

assert len(par["reference"]) == len(par["ref_taxonomy_id"]), "--ref_taxonomy_id must have same length as --reference"

# copy input files to tempdir
with tempfile.TemporaryDirectory() as temp_dir:
   # prepare to copy input files to tempdir
   old_inputs = par["input"]
   new_inputs = [ os.path.join(temp_dir, os.path.basename(f)) for f in old_inputs ]
   par["input"] = new_inputs

   # create output dir if not exists
   if not os.path.exists(par["output"]):
      os.makedirs(par["output"])

   # Create params file
   param_file = os.path.join(par["output"], "mqpar.xml")
   endl = "\n"

   generateMaxquantParametersXML()

   for path, taxid in zip(par["reference"], par["ref_taxonomy_id"]):
        addFastaFile(path,taxid)
  
   updateParameter('matchBetweenRuns',par["match_between_runs"])
   updateParameter('matchingTimeWindow',match_between_runs_settings.at[par["match_between_runs"], "matchingTimeWindow"])
   updateParameter('matchingIonMobilityWindow',match_between_runs_settings.at[par["match_between_runs"], "matchingIonMobilityWindow"])
   updateParameter('alignmentTimeWindow',match_between_runs_settings.at[par["match_between_runs"], "alignmentTimeWindow"])
   
   updateParameter('alignmentIonMobilityWindow',match_between_runs_settings.at[par["match_between_runs"], "alignmentIonMobilityWindow"])

   updateParameter('writeMsScansTable',"msScans" in par["write_tables"])
   updateParameter('writeMsmsScansTable',"msmsScans" in par["write_tables"])
   updateParameter('writePasefMsmsScansTable',"pasefMsmsScans" in par["write_tables"])
   updateParameter('writeAccumulatedMsmsScansTable',"accumulatedMsmsScans" in par["write_tables"])
   updateParameter('writeMs3ScansTable',"ms3Scans" in par["write_tables"])
   updateParameter('writeAllPeptidesTable',"allPeptides" in par["write_tables"])
   updateParameter('writeMzRangeTable',"mzRange" in par["write_tables"])
   updateParameter('writeDiaFragmentTable',"DIA fragments" in par["write_tables"])
   updateParameter('writeDiaFragmentQuantTable',"DIA fragments quant" in par["write_tables"])
   updateParameter('writeMzTab',"mzTab" in par["write_tables"])

   updateParameter('numThreads',meta["cpus"] if meta["cpus"] else "1")
   updateParameter('fixedCombinedFolder',par["output"])

   i=0
   for file in par["input"]:
      prefix =str(i)+'_'
      createParameter(filePaths,'string',file,prefix)
      createParameter(fractions,'short','32767',prefix)
      createParameter(ptms,'boolean','False',prefix)
      createParameter(paramGroupIndices,'int','0',prefix)
      createParameter(referenceChannels,'string','',prefix)

   i=0
   for experiment in experiment_names:
      createParameter(experiments,'string',experiment,str(i)+'_')

   updateParameter('msInstrument',ms_instrument_settings.at[par["ms_instrument"], "msInstrument"])
   updateParameter('maxCharge',ms_instrument_settings.at[par["ms_instrument"], "maxCharge"])
   updateParameter('minPeakLen',ms_instrument_settings.at[par["ms_instrument"], "minPeakLen"])
   updateParameter('diaMinPeakLen',ms_instrument_settings.at[par["ms_instrument"], "diaMinPeakLen"])
   updateParameter('useMs1Centroids',ms_instrument_settings.at[par["ms_instrument"], "useMs1Centroids"])
   updateParameter('useMs2Centroids',ms_instrument_settings.at[par["ms_instrument"], "useMs2Centroids"])

   updateParameter('intensityDetermination',ms_instrument_settings.at[par["ms_instrument"], "intensityDetermination"])
   updateParameter('centroidMatchTol',ms_instrument_settings.at[par["ms_instrument"], "centroidMatchTol"])
   updateParameter('valleyFactor',ms_instrument_settings.at[par["ms_instrument"], "valleyFactor"])
   updateParameter('advancedPeakSplitting',ms_instrument_settings.at[par["ms_instrument"], "advancedPeakSplitting"])
   updateParameter('intensityThresholdMs1',ms_instrument_settings.at[par["ms_instrument"], "intensityThresholdMs1"])
   updateParameter('intensityThresholdMs2',ms_instrument_settings.at[par["ms_instrument"], "intensityThresholdMs2"])



   updateParameter('lcmsRunType',par["lcms_run_type"])
   #setParameter('lfqMode',{group_type_settings.at[par["lcms_run_type"], "lfqMode"]})
   updateParameter('neucodeMaxPpm',group_type_settings.at[par["lcms_run_type"], "neucodeMaxPpm"])
   updateParameter('neucodeResolution',group_type_settings.at[par["lcms_run_type"], "neucodeResolution"])
   updateParameter('neucodeResolutionInMda',group_type_settings.at[par["lcms_run_type"], "neucodeResolutionInMda"])
   updateParameter('neucodeInSilicoLowRes',group_type_settings.at[par["lcms_run_type"], "neucodeInSilicoLowRes"])
   updateParameter('maxLabeledAa',group_type_settings.at[par["lcms_run_type"], "maxLabeledAa"])

   updateParameter('mainSearchTol',ms_instrument_settings.at[par["ms_instrument"], "mainSearchTol"])
   updateParameter('isotopeMatchTol',ms_instrument_settings.at[par["ms_instrument"], "isotopeMatchTol"])
   updateParameter('isotopeMatchTolInPpm',ms_instrument_settings.at[par["ms_instrument"], "isotopeMatchTolInPpm"])
   updateParameter('checkMassDeficit',ms_instrument_settings.at[par["ms_instrument"], "checkMassDeficit"])
   updateParameter('intensityDependentCalibration',ms_instrument_settings.at[par["ms_instrument"], "intensityDependentCalibration"])
   updateParameter('minScoreForCalibration',ms_instrument_settings.at[par["ms_instrument"], "minScoreForCalibration"])

   updateParameter('reporterFraction',group_type_settings.at[par["lcms_run_type"], "reporterFraction"])
   updateParameter('reporterBasePeakRatio',group_type_settings.at[par["lcms_run_type"], "reporterBasePeakRatio"])
   updateParameter('timsHalfWidth',group_type_settings.at[par["lcms_run_type"], "timsHalfWidth"])
   updateParameter('timsStep',group_type_settings.at[par["lcms_run_type"], "timsStep"])
   updateParameter('timsResolution',group_type_settings.at[par["lcms_run_type"], "timsResolution"])
   updateParameter('timsMinMsmsIntensity',group_type_settings.at[par["lcms_run_type"], "timsMinMsmsIntensity"])

   updateParameter("diaTopNForQuant",ms_instrument_settings.at[par["ms_instrument"], "diaTopNForQuant"])
   updateParameter("diaBackgroundSubtraction",ms_instrument_settings.at[par["ms_instrument"], "diaBackgroundSubtraction"])
   updateParameter("diaBackgroundSubtractionQuantile",ms_instrument_settings.at[par["ms_instrument"], "diaBackgroundSubtractionQuantile"])
   updateParameter("diaLfqWeightedMedian",ms_instrument_settings.at[par["ms_instrument"], "diaLfqWeightedMedian"])

   param_content = toString()

   with open(param_file, "w") as f:
      f.write(param_content)

   if not par["dryrun"]:
      # copy input files
      for old, new in zip(old_inputs, new_inputs):
         if (os.path.isdir(old)):
            shutil.copytree(old, new)
         else:
            shutil.copyfile(old, new)
         
      
      # run maxquant
      p = subprocess.Popen(
         ["dotnet", "/maxquant/bin/MaxQuantCmd.exe", os.path.basename(param_file)], 
         # ["maxquant", os.path.basename(param_file)], 
         cwd=os.path.dirname(param_file)
      )
      p.wait()

      if p.returncode != 0:
         raise Exception(f"MaxQuant finished with exit code {p.returncode}") 



