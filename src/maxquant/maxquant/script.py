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

# creates the base root structure for the maxquant parameter object
def generateMaxquantParametersXML(document,maxQuantParameters):

    #CREATE ROOT STRUCTURE
    maxQuantParameters.setAttribute('xmlns:xsd','http://www.w3.org/2001/XMLSchema')
    maxQuantParameters.setAttribute('xmlns:xsi','http://www.w3.org/2001/XMLSchema-instance')
    document.appendChild(maxQuantParameters)
     
    #CREATE DEFAULT PARAMETERS
    addDefaultParameters(document,maxQuantParameters)

    #CREATE PARAMETER GROUPS
    parameterGroupsParent = document.createElement('parameterGroups')
    maxQuantParameters.appendChild(parameterGroupsParent) 
    addParameterGroup(document,parameterGroupsParent)
    
    #CREATE MSMS PARAMETER ARRAY
    msmsParamArrayParent= document.createElement('msmsParamsArray')
    maxQuantParameters.appendChild(msmsParamArrayParent) 
    addMassSpecType(document,msmsParamArrayParent,['FTMS',20,True,7,True,25,True,True,12,100,True,True,True,True,False])
    addMassSpecType(document,msmsParamArrayParent,['ITMS',0.5,False,0.15,False,0.5,False,False,8,100,True,True,True,True,False])
    addMassSpecType(document,msmsParamArrayParent,['TOF',40,True,0.01,False,25,True,True,10,100,True,True,True,True,False])
    addMassSpecType(document,msmsParamArrayParent,['Unknown',20,True,7,True,25,True,True,12,100,True,True,True,True,False])

    #CREATE FRAGMENTATION PARAMETER ARRAY

    fragParamArrayParent= document.createElement('fragmentationParamsArray')
    maxQuantParameters.appendChild(fragParamArrayParent) 
    addFragmentationType(document,fragParamArrayParent,['CID',False,1,1,1,False,1,'KRH'])
    addFragmentationType(document,fragParamArrayParent,['HCD',False,1,1,1,False,1,'KRH'])
    addFragmentationType(document,fragParamArrayParent,['ETD',False,1,1,1,False,1,'KRH'])
    addFragmentationType(document,fragParamArrayParent,['PQD',False,1,1,1,False,1,'KRH'])
    addFragmentationType(document,fragParamArrayParent,['ETHCD',False,1,1,1,False,1,'KRH'])
    addFragmentationType(document,fragParamArrayParent,['ETCID',False,1,1,1,False,1,'KRH'])
    addFragmentationType(document,fragParamArrayParent,['UVPD',False,1,1,1,False,1,'KRH'])
    addFragmentationType(document,fragParamArrayParent,['Unknown',False,1,1,1,False,1,'KRH'])

# creates a single parameter and adds it into the parameter dictionary (in case defaults need to be overridden later) 
def createParameter(document,parameterParent,parameterDictionary,parameterName,parameterValue,parameterPrefix=''):
    parameterEL=document.createElement(parameterName)
    parameterElValue=document.createTextNode(str(parameterValue))
    parameterEL.appendChild(parameterElValue)
    parameterParent.appendChild(parameterEL)
    parameterDictionary[parameterPrefix+parameterName]=parameterEL

# updates a given parameter that is present in the parameter dictionary, creates if not exist
def updateParameter(document,maxQuantParameters,parameterDictionary,parameterName,parameterValue):
    if(not parameterName in parameterDictionary):
     createParameter(document,maxQuantParameters,parameterDictionary,parameterName,parameterValue)
    parameterDictionary[parameterName].firstChild.replaceWholeText(parameterValue)
       
# adds a fasta file to the parameters
def addFastaFile(document,fastaParent,parameterDictionary,fastaArray,fastaFilePath,taxonomyId=""):
    fastaFileIndex=len(fastaArray)
    fastaArray.append(fastaFilePath)
    fastaFileInfoEl = document.createElement('FastaFileInfo')
    fastaParent.appendChild(fastaFileInfoEl) 
   
    prefix=str(fastaFileIndex)+"_"
    createParameter(document,fastaFileInfoEl,parameterDictionary,'fastaFilePath',fastaFilePath,prefix)
    createParameter(document,fastaFileInfoEl,parameterDictionary,'identifierParseRule','>.*\|(.*)\|',prefix)
    createParameter(document,fastaFileInfoEl,parameterDictionary,'descriptionParseRule','>(.*)',prefix)
    createParameter(document,fastaFileInfoEl,parameterDictionary,'taxonomyParseRule',"",prefix)
    createParameter(document,fastaFileInfoEl,parameterDictionary,'variationParseRule',"",prefix)
    createParameter(document,fastaFileInfoEl,parameterDictionary,'modificationParseRule',"",prefix)
    createParameter(document,fastaFileInfoEl,parameterDictionary,'taxonomyId',taxonomyId,prefix)

# sets default parameters
def addDefaultParameters(document,maxQuantParameters):
   createParameter(document,maxQuantParameters,parameterDictionary,"fastaFilesProteogenomics","")
   createParameter(document,maxQuantParameters,parameterDictionary,"fastaFilesFirstSearch","")
   createParameter(document,maxQuantParameters,parameterDictionary,"fixedSearchFolder","")
   createParameter(document,maxQuantParameters,parameterDictionary,'andromedaCacheSize','350000')
   createParameter(document,maxQuantParameters,parameterDictionary,'advancedRatios','True')
   createParameter(document,maxQuantParameters,parameterDictionary,'pvalThres','0.005')
   createParameter(document,maxQuantParameters,parameterDictionary,'rtShift','False')
   createParameter(document,maxQuantParameters,parameterDictionary,'separateLfq','False')
   createParameter(document,maxQuantParameters,parameterDictionary,'lfqStabilizeLargeRatios','True')
   createParameter(document,maxQuantParameters,parameterDictionary,'lfqRequireMsms','True')
   createParameter(document,maxQuantParameters,parameterDictionary,'lfqBayesQuant','False')
   createParameter(document,maxQuantParameters,parameterDictionary,'decoyMode','revert')
   createParameter(document,maxQuantParameters,parameterDictionary,'boxCarMode','all')
   createParameter(document,maxQuantParameters,parameterDictionary,'includeContaminants','True')
   createParameter(document,maxQuantParameters,parameterDictionary,'maxPeptideMass','4600')
   createParameter(document,maxQuantParameters,parameterDictionary,'epsilonMutationScore','True')
   createParameter(document,maxQuantParameters,parameterDictionary,'mutatedPeptidesSeparately','True')
   createParameter(document,maxQuantParameters,parameterDictionary,'proteogenomicPeptidesSeparately','True')
   createParameter(document,maxQuantParameters,parameterDictionary,'minDeltaScoreUnmodifiedPeptides','0')
   createParameter(document,maxQuantParameters,parameterDictionary,'minDeltaScoreModifiedPeptides','6')
   createParameter(document,maxQuantParameters,parameterDictionary,'minScoreUnmodifiedPeptides','0')
   createParameter(document,maxQuantParameters,parameterDictionary,'minScoreModifiedPeptides','40')
   createParameter(document,maxQuantParameters,parameterDictionary,'secondPeptide','True')
   createParameter(document,maxQuantParameters,parameterDictionary,'matchBetweenRuns','True')
   createParameter(document,maxQuantParameters,parameterDictionary,'matchUnidentifiedFeatures','False')
   createParameter(document,maxQuantParameters,parameterDictionary,'matchBetweenRunsFdr','False')
   createParameter(document,maxQuantParameters,parameterDictionary,'dependentPeptides','False')
   createParameter(document,maxQuantParameters,parameterDictionary,'dependentPeptideFdr','0')
   createParameter(document,maxQuantParameters,parameterDictionary,'dependentPeptideMassBin','0')
   createParameter(document,maxQuantParameters,parameterDictionary,'dependentPeptidesBetweenRuns','False')
   createParameter(document,maxQuantParameters,parameterDictionary,'dependentPeptidesWithinExperiment','False')
   createParameter(document,maxQuantParameters,parameterDictionary,'dependentPeptidesWithinParameterGroup','False')
   createParameter(document,maxQuantParameters,parameterDictionary,'dependentPeptidesRestrictFractions','False')
   createParameter(document,maxQuantParameters,parameterDictionary,'dependentPeptidesFractionDifference','0')
   createParameter(document,maxQuantParameters,parameterDictionary,'ibaq','False')
   createParameter(document,maxQuantParameters,parameterDictionary,'top3','False')
   createParameter(document,maxQuantParameters,parameterDictionary,'independentEnzymes','False')
   createParameter(document,maxQuantParameters,parameterDictionary,'useDeltaScore','False')
   createParameter(document,maxQuantParameters,parameterDictionary,'splitProteinGroupsByTaxonomy','False')
   createParameter(document,maxQuantParameters,parameterDictionary,'taxonomyLevel','Species')
   createParameter(document,maxQuantParameters,parameterDictionary,'avalon','False')
   createParameter(document,maxQuantParameters,parameterDictionary,'nModColumns','3')
   createParameter(document,maxQuantParameters,parameterDictionary,'ibaqLogFit','False')
   createParameter(document,maxQuantParameters,parameterDictionary,'ibaqChargeNormalization','False')
   createParameter(document,maxQuantParameters,parameterDictionary,'razorProteinFdr','True')
   createParameter(document,maxQuantParameters,parameterDictionary,'deNovoSequencing','False')
   createParameter(document,maxQuantParameters,parameterDictionary,'deNovoVarMods','False')
   createParameter(document,maxQuantParameters,parameterDictionary,'deNovoCompleteSequence','False')
   createParameter(document,maxQuantParameters,parameterDictionary,'deNovoCalibratedMasses','False')
   createParameter(document,maxQuantParameters,parameterDictionary,'deNovoMaxIterations','0')
   createParameter(document,maxQuantParameters,parameterDictionary,'deNovoProteaseReward','0')
   createParameter(document,maxQuantParameters,parameterDictionary,'deNovoProteaseRewardTof','0')
   createParameter(document,maxQuantParameters,parameterDictionary,'deNovoAgPenalty','0')
   createParameter(document,maxQuantParameters,parameterDictionary,'deNovoGgPenalty','0')
   createParameter(document,maxQuantParameters,parameterDictionary,'deNovoUseComplementScore','True')
   createParameter(document,maxQuantParameters,parameterDictionary,'deNovoUseProteaseScore','True')
   createParameter(document,maxQuantParameters,parameterDictionary,'deNovoUseWaterLossScore','True')
   createParameter(document,maxQuantParameters,parameterDictionary,'deNovoUseAmmoniaLossScore','True')
   createParameter(document,maxQuantParameters,parameterDictionary,'deNovoUseA2Score','True')
   createParameter(document,maxQuantParameters,parameterDictionary,'massDifferenceSearch','False')
   createParameter(document,maxQuantParameters,parameterDictionary,'isotopeCalc','False')
   createParameter(document,maxQuantParameters,parameterDictionary,'writePeptidesForSpectrumFile','')
   createParameter(document,maxQuantParameters,parameterDictionary,'intensityPredictionsFile','')
   createParameter(document,maxQuantParameters,parameterDictionary,'minPepLen','7')
   createParameter(document,maxQuantParameters,parameterDictionary,'psmFdrCrosslink','0.01')
   createParameter(document,maxQuantParameters,parameterDictionary,'peptideFdr','0.01')
   createParameter(document,maxQuantParameters,parameterDictionary,'proteinFdr','0.01')
   createParameter(document,maxQuantParameters,parameterDictionary,'siteFdr','0.01')
   createParameter(document,maxQuantParameters,parameterDictionary,'minPeptideLengthForUnspecificSearch','8')
   createParameter(document,maxQuantParameters,parameterDictionary,'maxPeptideLengthForUnspecificSearch','25')
   createParameter(document,maxQuantParameters,parameterDictionary,'useNormRatiosForOccupancy','True')
   createParameter(document,maxQuantParameters,parameterDictionary,'minPeptides','1')
   createParameter(document,maxQuantParameters,parameterDictionary,'minRazorPeptides','1')
   createParameter(document,maxQuantParameters,parameterDictionary,'minUniquePeptides','0')
   createParameter(document,maxQuantParameters,parameterDictionary,'useCounterparts','False')
   createParameter(document,maxQuantParameters,parameterDictionary,'advancedSiteIntensities','True')
   createParameter(document,maxQuantParameters,parameterDictionary,'customProteinQuantification','False')
   createParameter(document,maxQuantParameters,parameterDictionary,'customProteinQuantificationFile','')
   createParameter(document,maxQuantParameters,parameterDictionary,'minRatioCount','2')
   createParameter(document,maxQuantParameters,parameterDictionary,'restrictProteinQuantification','True')

   restrictionModsEl = document.createElement('restrictMods')
   maxQuantParameters.appendChild(restrictionModsEl) 
   createParameter(document,restrictionModsEl,parameterDictionary,'string','Oxidation (M)')
   createParameter(document,restrictionModsEl,parameterDictionary,'string','Acetyl (Protein N-term)')

   createParameter(document,maxQuantParameters,parameterDictionary,'matchingTimeWindow','0.7')
   createParameter(document,maxQuantParameters,parameterDictionary,'matchingIonMobilityWindow','0.05')
   createParameter(document,maxQuantParameters,parameterDictionary,'alignmentTimeWindow','20')
   createParameter(document,maxQuantParameters,parameterDictionary,'alignmentIonMobilityWindow','1')
   createParameter(document,maxQuantParameters,parameterDictionary,'numberOfCandidatesMsms','15')
   createParameter(document,maxQuantParameters,parameterDictionary,'compositionPrediction','0')
   createParameter(document,maxQuantParameters,parameterDictionary,'quantMode','1')
   createParameter(document,maxQuantParameters,parameterDictionary,'massDifferenceMods','')
   createParameter(document,maxQuantParameters,parameterDictionary,'mainSearchMaxCombinations','200')
   createParameter(document,maxQuantParameters,parameterDictionary,'writeMsScansTable','True')
   createParameter(document,maxQuantParameters,parameterDictionary,'writeMsmsScansTable','True')
   createParameter(document,maxQuantParameters,parameterDictionary,'writePasefMsmsScansTable','True')
   createParameter(document,maxQuantParameters,parameterDictionary,'writeAccumulatedMsmsScansTable','True')
   createParameter(document,maxQuantParameters,parameterDictionary,'writeMs3ScansTable','True')
   createParameter(document,maxQuantParameters,parameterDictionary,'writeAllPeptidesTable','True')
   createParameter(document,maxQuantParameters,parameterDictionary,'writeMzRangeTable','True')
   createParameter(document,maxQuantParameters,parameterDictionary,'writeDiaFragmentTable','True')
   createParameter(document,maxQuantParameters,parameterDictionary,'writeDiaFragmentQuantTable','True')
   createParameter(document,maxQuantParameters,parameterDictionary,'writeMzTab','True')
   createParameter(document,maxQuantParameters,parameterDictionary,'disableMd5','False')
   createParameter(document,maxQuantParameters,parameterDictionary,'cacheBinInds','True')
   createParameter(document,maxQuantParameters,parameterDictionary,'etdIncludeB','False')
   createParameter(document,maxQuantParameters,parameterDictionary,'ms2PrecursorShift','0')
   createParameter(document,maxQuantParameters,parameterDictionary,'complementaryIonPpm','20')
   createParameter(document,maxQuantParameters,parameterDictionary,'variationParseRule','')
   createParameter(document,maxQuantParameters,parameterDictionary,'variationMode','none')
   createParameter(document,maxQuantParameters,parameterDictionary,'useSeriesReporters','False')
   createParameter(document,maxQuantParameters,parameterDictionary,'name','session1')
   createParameter(document,maxQuantParameters,parameterDictionary,'maxQuantVersion','2.0.3.0')
   createParameter(document,maxQuantParameters,parameterDictionary,'pluginFolder','')
   createParameter(document,maxQuantParameters,parameterDictionary,'numThreads','1')
   createParameter(document,maxQuantParameters,parameterDictionary,'emailAddress','')
   createParameter(document,maxQuantParameters,parameterDictionary,'smtpHost','')
   createParameter(document,maxQuantParameters,parameterDictionary,'emailFromAddress','')
   createParameter(document,maxQuantParameters,parameterDictionary,'fixedCombinedFolder','')
   createParameter(document,maxQuantParameters,parameterDictionary,'fullMinMz','-1.79769313486232E+308')
   createParameter(document,maxQuantParameters,parameterDictionary,'fullMaxMz','1.79769313486232E+308')
   createParameter(document,maxQuantParameters,parameterDictionary,'sendEmail','False')
   createParameter(document,maxQuantParameters,parameterDictionary,'ionCountIntensities','False')
   createParameter(document,maxQuantParameters,parameterDictionary,'verboseColumnHeaders','False')
   createParameter(document,maxQuantParameters,parameterDictionary,'calcPeakProperties','True')
   createParameter(document,maxQuantParameters,parameterDictionary,'showCentroidMassDifferences','False')
   createParameter(document,maxQuantParameters,parameterDictionary,'showIsotopeMassDifferences','False')
   createParameter(document,maxQuantParameters,parameterDictionary,'useDotNetCore','True')
   createParameter(document,maxQuantParameters,parameterDictionary,'profilePerformance','False')
   createParameter(document,maxQuantParameters,parameterDictionary,'intensPred','False')
   createParameter(document,maxQuantParameters,parameterDictionary,'intensPredModelReTrain','False')
   createParameter(document,maxQuantParameters,parameterDictionary,'lfqTopNPeptides','0')
   createParameter(document,maxQuantParameters,parameterDictionary,'diaJoinPrecChargesForLfq','False')
   createParameter(document,maxQuantParameters,parameterDictionary,'diaFragChargesForQuant','1')
   createParameter(document,maxQuantParameters,parameterDictionary,'timsRearrangeSpectra','False')
   createParameter(document,maxQuantParameters,parameterDictionary,'gridSpacing','0.5')
   createParameter(document,maxQuantParameters,parameterDictionary,'proteinGroupingFile','')

# initiates a parameter group
def addParameterGroup(document,parameterGroupParent):
   parameterParent = document.createElement('parameterGroup')
   parameterGroupParent.appendChild(parameterParent) 
   createParameter(document,parameterParent,parameterDictionary,'msInstrument','0')
   createParameter(document,parameterParent,parameterDictionary,'maxCharge','7')
   createParameter(document,parameterParent,parameterDictionary,'minPeakLen','2')
   createParameter(document,parameterParent,parameterDictionary,'diaMinPeakLen','1')
   createParameter(document,parameterParent,parameterDictionary,'useMs1Centroids','False')
   createParameter(document,parameterParent,parameterDictionary,'useMs2Centroids','False')
   createParameter(document,parameterParent,parameterDictionary,'cutPeaks','True')
   createParameter(document,parameterParent,parameterDictionary,'gapScans','1')
   createParameter(document,parameterParent,parameterDictionary,'minTime','NaN')
   createParameter(document,parameterParent,parameterDictionary,'maxTime','NaN')
   createParameter(document,parameterParent,parameterDictionary,'matchType','MatchFromAndTo')
   createParameter(document,parameterParent,parameterDictionary,'intensityDetermination','0')
   createParameter(document,parameterParent,parameterDictionary,'centroidMatchTol','8')
   createParameter(document,parameterParent,parameterDictionary,'centroidMatchTolInPpm','True')
   createParameter(document,parameterParent,parameterDictionary,'centroidHalfWidth','35')
   createParameter(document,parameterParent,parameterDictionary,'centroidHalfWidthInPpm','True')
   createParameter(document,parameterParent,parameterDictionary,'valleyFactor','1.4')
   createParameter(document,parameterParent,parameterDictionary,'isotopeValleyFactor','1.2')
   createParameter(document,parameterParent,parameterDictionary,'advancedPeakSplitting','False')
   createParameter(document,parameterParent,parameterDictionary,'intensityThresholdMs1','0')
   createParameter(document,parameterParent,parameterDictionary,'intensityThresholdMs2','0')

   labelMods = document.createElement('labelMods')
   parameterParent.appendChild(labelMods) 
   createParameter(document,labelMods,parameterDictionary,"string",'')

   createParameter(document,parameterParent,parameterDictionary,'lcmsRunType','Standard')
   createParameter(document,parameterParent,parameterDictionary,'reQuantify','False')
   createParameter(document,parameterParent,parameterDictionary,'lfqMode','1')
   createParameter(document,parameterParent,parameterDictionary,'lfqNormClusterSize','80')
   createParameter(document,parameterParent,parameterDictionary,'lfqMinEdgesPerNode','3')
   createParameter(document,parameterParent,parameterDictionary,'lfqAvEdgesPerNode','6')
   createParameter(document,parameterParent,parameterDictionary,'lfqMaxFeatures','100000')
   createParameter(document,parameterParent,parameterDictionary,'neucodeMaxPpm','0')
   createParameter(document,parameterParent,parameterDictionary,'neucodeResolution','0')
   createParameter(document,parameterParent,parameterDictionary,'neucodeResolutionInMda','False')
   createParameter(document,parameterParent,parameterDictionary,'neucodeInSilicoLowRes','False')
   createParameter(document,parameterParent,parameterDictionary,'fastLfq','True')
   createParameter(document,parameterParent,parameterDictionary,'lfqRestrictFeatures','False')
   createParameter(document,parameterParent,parameterDictionary,'lfqMinRatioCount','2')
   createParameter(document,parameterParent,parameterDictionary,'maxLabeledAa','0')
   createParameter(document,parameterParent,parameterDictionary,'maxNmods','5')
   createParameter(document,parameterParent,parameterDictionary,'maxMissedCleavages','2')
   createParameter(document,parameterParent,parameterDictionary,'multiplicity','1')
   createParameter(document,parameterParent,parameterDictionary,'enzymeMode','0')
   createParameter(document,parameterParent,parameterDictionary,'complementaryReporterType','0')
   createParameter(document,parameterParent,parameterDictionary,'reporterNormalization','0')
   createParameter(document,parameterParent,parameterDictionary,'neucodeIntensityMode','0')

   fixedModifications = document.createElement('fixedModifications')
   parameterParent.appendChild(fixedModifications) 
   createParameter(document,fixedModifications,parameterDictionary,"string",'Carbamidomethyl (C)')

   enzymes = document.createElement('enzymes')
   parameterParent.appendChild(enzymes) 
   createParameter(document,enzymes,parameterDictionary,"string",'Trypsin/P')
   createParameter(document,parameterParent,parameterDictionary,"enzymesFirstSearch",'')
   createParameter(document,parameterParent,parameterDictionary,"enzymeModeFirstSearch",'0')
   createParameter(document,parameterParent,parameterDictionary,"useEnzymeFirstSearch",'False')
   createParameter(document,parameterParent,parameterDictionary,"useVariableModificationsFirstSearch",'False')

   variableModifications = document.createElement('variableModifications')
   parameterParent.appendChild(variableModifications) 
   createParameter(document,variableModifications,parameterDictionary,"string",'Oxidation (M)')
   createParameter(document,variableModifications,parameterDictionary,"string",'Acetyl (Protein N-term)')

   createParameter(document,parameterParent,parameterDictionary,'useMultiModification','False')
   createParameter(document,parameterParent,parameterDictionary,'multiModifications','')
   createParameter(document,parameterParent,parameterDictionary,'isobaricLabels','')
   createParameter(document,parameterParent,parameterDictionary,'neucodeLabels','')
   createParameter(document,parameterParent,parameterDictionary,'variableModificationsFirstSearch','')
   createParameter(document,parameterParent,parameterDictionary,'hasAdditionalVariableModifications','False')
   createParameter(document,parameterParent,parameterDictionary,'additionalVariableModifications','')
   createParameter(document,parameterParent,parameterDictionary,'additionalVariableModificationProteins','')
   createParameter(document,parameterParent,parameterDictionary,'doMassFiltering','True')
   createParameter(document,parameterParent,parameterDictionary,'firstSearchTol','20')
   createParameter(document,parameterParent,parameterDictionary,'mainSearchTol','4.5')
   createParameter(document,parameterParent,parameterDictionary,'searchTolInPpm','True')
   createParameter(document,parameterParent,parameterDictionary,'isotopeMatchTol','2')
   createParameter(document,parameterParent,parameterDictionary,'isotopeMatchTolInPpm','True')
   createParameter(document,parameterParent,parameterDictionary,'isotopeTimeCorrelation','0.6')
   createParameter(document,parameterParent,parameterDictionary,'theorIsotopeCorrelation','0.6')
   createParameter(document,parameterParent,parameterDictionary,'checkMassDeficit','True')
   createParameter(document,parameterParent,parameterDictionary,'recalibrationInPpm','True')
   createParameter(document,parameterParent,parameterDictionary,'intensityDependentCalibration','False')
   createParameter(document,parameterParent,parameterDictionary,'minScoreForCalibration','70')
   createParameter(document,parameterParent,parameterDictionary,'matchLibraryFile','False')
   createParameter(document,parameterParent,parameterDictionary,'libraryFile','')
   createParameter(document,parameterParent,parameterDictionary,'matchLibraryMassTolPpm','0')
   createParameter(document,parameterParent,parameterDictionary,'matchLibraryTimeTolMin','0')
   createParameter(document,parameterParent,parameterDictionary,'matchLabelTimeTolMin','0')
   createParameter(document,parameterParent,parameterDictionary,'reporterMassTolerance','NaN')
   createParameter(document,parameterParent,parameterDictionary,'reporterPif','NaN')
   createParameter(document,parameterParent,parameterDictionary,'filterPif','False')
   createParameter(document,parameterParent,parameterDictionary,'reporterFraction','NaN')
   createParameter(document,parameterParent,parameterDictionary,'reporterBasePeakRatio','NaN')
   createParameter(document,parameterParent,parameterDictionary,'timsHalfWidth','0')
   createParameter(document,parameterParent,parameterDictionary,'timsStep','0')
   createParameter(document,parameterParent,parameterDictionary,'timsResolution','0')
   createParameter(document,parameterParent,parameterDictionary,'timsMinMsmsIntensity','0')
   createParameter(document,parameterParent,parameterDictionary,'timsRemovePrecursor','True')
   createParameter(document,parameterParent,parameterDictionary,'timsIsobaricLabels','False')
   createParameter(document,parameterParent,parameterDictionary,'timsCollapseMsms','True')
   createParameter(document,parameterParent,parameterDictionary,'crossLinkingType','0')
   createParameter(document,parameterParent,parameterDictionary,'crossLinker','')

   createParameter(document,parameterParent,parameterDictionary,'minMatchXl','3')
   createParameter(document,parameterParent,parameterDictionary,'minPairedPepLenXl','6')
   createParameter(document,parameterParent,parameterDictionary,'minScore_Dipeptide','40')
   createParameter(document,parameterParent,parameterDictionary,'minScore_Monopeptide','0')
   createParameter(document,parameterParent,parameterDictionary,'minScore_PartialCross','10')
   createParameter(document,parameterParent,parameterDictionary,'crosslinkOnlyIntraProtein','False')
   createParameter(document,parameterParent,parameterDictionary,'crosslinkIntensityBasedPrecursor','True')
   createParameter(document,parameterParent,parameterDictionary,'isHybridPrecDetermination','False')
   createParameter(document,parameterParent,parameterDictionary,'topXcross','3')
   createParameter(document,parameterParent,parameterDictionary,'doesSeparateInterIntraProteinCross','False')
   createParameter(document,parameterParent,parameterDictionary,'crosslinkMaxMonoUnsaturated','0')
   createParameter(document,parameterParent,parameterDictionary,'crosslinkMaxMonoSaturated','0')
   createParameter(document,parameterParent,parameterDictionary,'crosslinkMaxDiUnsaturated','0')
   createParameter(document,parameterParent,parameterDictionary,'crosslinkMaxDiSaturated','0')
   createParameter(document,parameterParent,parameterDictionary,'crosslinkModifications','')
   createParameter(document,parameterParent,parameterDictionary,'crosslinkFastaFiles','')
   createParameter(document,parameterParent,parameterDictionary,'crosslinkSites','')
   createParameter(document,parameterParent,parameterDictionary,'crosslinkNetworkFiles','')
   createParameter(document,parameterParent,parameterDictionary,'crosslinkMode','')
   createParameter(document,parameterParent,parameterDictionary,'peakRefinement','False')
   createParameter(document,parameterParent,parameterDictionary,'isobaricSumOverWindow','True')
   createParameter(document,parameterParent,parameterDictionary,'isobaricWeightExponent','0.75')
   createParameter(document,parameterParent,parameterDictionary,'collapseMsmsOnIsotopePatterns','False')
   createParameter(document,parameterParent,parameterDictionary,'diaLibraryType','0')
   createParameter(document,parameterParent,parameterDictionary,'diaLibraryPaths','')
   createParameter(document,parameterParent,parameterDictionary,'diaPeptidePaths','')
   createParameter(document,parameterParent,parameterDictionary,'diaEvidencePaths','')
   createParameter(document,parameterParent,parameterDictionary,'diaMsmsPaths','')
   createParameter(document,parameterParent,parameterDictionary,'diaInitialPrecMassTolPpm','20')
   createParameter(document,parameterParent,parameterDictionary,'diaInitialFragMassTolPpm','20')
   createParameter(document,parameterParent,parameterDictionary,'diaCorrThresholdFeatureClustering','0.85')
   createParameter(document,parameterParent,parameterDictionary,'diaPrecTolPpmFeatureClustering','2')
   createParameter(document,parameterParent,parameterDictionary,'diaFragTolPpmFeatureClustering','2')
   createParameter(document,parameterParent,parameterDictionary,'diaScoreN','7')
   createParameter(document,parameterParent,parameterDictionary,'diaMinScore','1.99')
   createParameter(document,parameterParent,parameterDictionary,'diaXgBoostBaseScore','0.4')
   createParameter(document,parameterParent,parameterDictionary,'diaXgBoostSubSample','0.9')
   createParameter(document,parameterParent,parameterDictionary,'centroidPosition','0')
   createParameter(document,parameterParent,parameterDictionary,'diaQuantMethod','7')
   createParameter(document,parameterParent,parameterDictionary,'diaFeatureQuantMethod','2')
   createParameter(document,parameterParent,parameterDictionary,'lfqNormType','1')
   createParameter(document,parameterParent,parameterDictionary,'diaTopNForQuant','10')
   createParameter(document,parameterParent,parameterDictionary,'diaMinMsmsIntensityForQuant','0')
   createParameter(document,parameterParent,parameterDictionary,'diaTopMsmsIntensityQuantileForQuant','0.85')
   createParameter(document,parameterParent,parameterDictionary,'diaPrecursorFilterType','0')
   createParameter(document,parameterParent,parameterDictionary,'diaMinFragmentOverlapScore','1')
   createParameter(document,parameterParent,parameterDictionary,'diaMinPrecursorScore','0.5')
   createParameter(document,parameterParent,parameterDictionary,'diaMinProfileCorrelation','0')
   createParameter(document,parameterParent,parameterDictionary,'diaXgBoostMinChildWeight','9')
   createParameter(document,parameterParent,parameterDictionary,'diaXgBoostMaximumTreeDepth','12')
   createParameter(document,parameterParent,parameterDictionary,'diaXgBoostEstimators','580')
   createParameter(document,parameterParent,parameterDictionary,'diaXgBoostGamma','0.9')
   createParameter(document,parameterParent,parameterDictionary,'diaXgBoostMaxDeltaStep','3')
   createParameter(document,parameterParent,parameterDictionary,'diaGlobalMl','True')
   createParameter(document,parameterParent,parameterDictionary,'diaAdaptiveMassAccuracy','False')
   createParameter(document,parameterParent,parameterDictionary,'diaMassWindowFactor','3.3')
   createParameter(document,parameterParent,parameterDictionary,'diaRtPrediction','False')
   createParameter(document,parameterParent,parameterDictionary,'diaRtPredictionSecondRound','False')
   createParameter(document,parameterParent,parameterDictionary,'diaNoMl','False')
   createParameter(document,parameterParent,parameterDictionary,'diaPermuteRt','False')
   createParameter(document,parameterParent,parameterDictionary,'diaPermuteCcs','False')
   createParameter(document,parameterParent,parameterDictionary,'diaBackgroundSubtraction','False')
   createParameter(document,parameterParent,parameterDictionary,'diaBackgroundSubtractionQuantile','0.5')
   createParameter(document,parameterParent,parameterDictionary,'diaBackgroundSubtractionFactor','4')
   createParameter(document,parameterParent,parameterDictionary,'diaLfqWeightedMedian','False')
   createParameter(document,parameterParent,parameterDictionary,'diaTransferQvalue','0.3')
   createParameter(document,parameterParent,parameterDictionary,'diaOnlyIsosForRecal','True')
   createParameter(document,parameterParent,parameterDictionary,'diaMinPeaksForRecal','5')
   createParameter(document,parameterParent,parameterDictionary,'diaUseFragIntensForMl','False')
   createParameter(document,parameterParent,parameterDictionary,'diaUseFragMassesForMl','False')
   createParameter(document,parameterParent,parameterDictionary,'diaMaxTrainInstances','1000000')

# initiates a mass spec type template
def addMassSpecType(document,massSpecTypeParent,massSpecTypeParameters):
    prefix=massSpecTypeParameters[0]+"_"
    msmsParams = document.createElement('msmsParams')
    massSpecTypeParent.appendChild(msmsParams) 
    createParameter(document,msmsParams,parameterDictionary,'Name', str(massSpecTypeParameters[0]),prefix)
    createParameter(document,msmsParams,parameterDictionary,'MatchTolerance',str(massSpecTypeParameters[1]),prefix)
    createParameter(document,msmsParams,parameterDictionary,'MatchToleranceInPpm',str(massSpecTypeParameters[2]),prefix)
    createParameter(document,msmsParams,parameterDictionary,'DeisotopeTolerance',str(massSpecTypeParameters[3]),prefix)
    createParameter(document,msmsParams,parameterDictionary,'DeisotopeToleranceInPpm',str(massSpecTypeParameters[4]),prefix)
    createParameter(document,msmsParams,parameterDictionary,'DeNovoTolerance',str(massSpecTypeParameters[5]),prefix)
    createParameter(document,msmsParams,parameterDictionary,'DeNovoToleranceInPpm',str(massSpecTypeParameters[6]),prefix)
    createParameter(document,msmsParams,parameterDictionary,'Deisotope',str(massSpecTypeParameters[7]),prefix)
    createParameter(document,msmsParams,parameterDictionary,'Topx',str(massSpecTypeParameters[8]),prefix)
    createParameter(document,msmsParams,parameterDictionary,'TopxInterval',str(massSpecTypeParameters[9]),prefix)
    createParameter(document,msmsParams,parameterDictionary,'HigherCharges',str(massSpecTypeParameters[10]),prefix)
    createParameter(document,msmsParams,parameterDictionary,'IncludeWater',str(massSpecTypeParameters[11]),prefix)
    createParameter(document,msmsParams,parameterDictionary,'IncludeAmmonia',str(massSpecTypeParameters[12]),prefix)
    createParameter(document,msmsParams,parameterDictionary,'DependentLosses',str(massSpecTypeParameters[13]),prefix)
    createParameter(document,msmsParams,parameterDictionary,'Recalibration',str(massSpecTypeParameters[14]),prefix)

# initiates a fragmentation type
def addFragmentationType(document,fragmentationTypeParent,fragmentationTypeParameters):
    prefix=str(fragmentationTypeParameters[0])+"_"
    fragmentationParams = document.createElement('fragmentationParams')
    fragmentationTypeParent.appendChild(fragmentationParams) 
    createParameter(document,fragmentationParams,parameterDictionary,'Name', str(fragmentationTypeParameters[0]),prefix)
    createParameter(document,fragmentationParams,parameterDictionary,'Connected',str(fragmentationTypeParameters[1]),prefix)
    createParameter(document,fragmentationParams,parameterDictionary,'ConnectedScore0',str(fragmentationTypeParameters[2]),prefix)
    createParameter(document,fragmentationParams,parameterDictionary,'ConnectedScore1',str(fragmentationTypeParameters[3]),prefix)
    createParameter(document,fragmentationParams,parameterDictionary,'ConnectedScore2',str(fragmentationTypeParameters[4]),prefix)
    createParameter(document,fragmentationParams,parameterDictionary,'InternalFragments',str(fragmentationTypeParameters[5]),prefix)
    createParameter(document,fragmentationParams,parameterDictionary,'InternalFragmentWeight',str(fragmentationTypeParameters[6]),prefix)
    createParameter(document,fragmentationParams,parameterDictionary,'InternalFragmentAas',str(fragmentationTypeParameters[7]),prefix)

# pretty prints the XML document in a maxquant compatible format (UTF-8)
def toString(document):
   nativeXML = document.toprettyxml(indent ="   ",).replace("&gt;",">").replace("&lt;","<")
   nativeXML=nativeXML.replace('<?xml version="1.0"','<?xml version="1.0" encoding="utf-8"')
   return nativeXML

#########################################################################################################################################

document = xmlbuilder.Document() 
maxQuantParameters = document.createElement('maxQuantParameters') 
parameterDictionary={}
fastaArray=[]

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

   generateMaxquantParametersXML(document,maxQuantParameters)

    #CREATE FASTA SECTION
   fastaFileParamsEl = document.createElement('fastaFiles') 
   maxQuantParameters.appendChild(fastaFileParamsEl)

   for path, taxid in zip(par["reference"], par["ref_taxonomy_id"]):
      addFastaFile(document,fastaFileParamsEl,parameterDictionary,fastaArray,path,taxid)
  
   updateParameter(document,maxQuantParameters,parameterDictionary,'matchBetweenRuns',par["match_between_runs"])
   updateParameter(document,maxQuantParameters,parameterDictionary,'matchingTimeWindow',match_between_runs_settings.at[par["match_between_runs"], "matchingTimeWindow"])
   updateParameter(document,maxQuantParameters,parameterDictionary,'matchingIonMobilityWindow',match_between_runs_settings.at[par["match_between_runs"], "matchingIonMobilityWindow"])
   updateParameter(document,maxQuantParameters,parameterDictionary,'alignmentTimeWindow',match_between_runs_settings.at[par["match_between_runs"], "alignmentTimeWindow"])
   
   updateParameter(document,maxQuantParameters,parameterDictionary,'alignmentIonMobilityWindow',match_between_runs_settings.at[par["match_between_runs"], "alignmentIonMobilityWindow"])

   updateParameter(document,maxQuantParameters,parameterDictionary,'writeMsScansTable',"msScans" in par["write_tables"])
   updateParameter(document,maxQuantParameters,parameterDictionary,'writeMsmsScansTable',"msmsScans" in par["write_tables"])
   updateParameter(document,maxQuantParameters,parameterDictionary,'writePasefMsmsScansTable',"pasefMsmsScans" in par["write_tables"])
   updateParameter(document,maxQuantParameters,parameterDictionary,'writeAccumulatedMsmsScansTable',"accumulatedMsmsScans" in par["write_tables"])
   updateParameter(document,maxQuantParameters,parameterDictionary,'writeMs3ScansTable',"ms3Scans" in par["write_tables"])
   updateParameter(document,maxQuantParameters,parameterDictionary,'writeAllPeptidesTable',"allPeptides" in par["write_tables"])
   updateParameter(document,maxQuantParameters,parameterDictionary,'writeMzRangeTable',"mzRange" in par["write_tables"])
   updateParameter(document,maxQuantParameters,parameterDictionary,'writeDiaFragmentTable',"DIA fragments" in par["write_tables"])
   updateParameter(document,maxQuantParameters,parameterDictionary,'writeDiaFragmentQuantTable',"DIA fragments quant" in par["write_tables"])
   updateParameter(document,maxQuantParameters,parameterDictionary,'writeMzTab',"mzTab" in par["write_tables"])

   updateParameter(document,maxQuantParameters,parameterDictionary,'numThreads',meta["cpus"] if meta["cpus"] else "1")
   updateParameter(document,maxQuantParameters,parameterDictionary,'fixedCombinedFolder',par["output"])

   filePaths = document.createElement('filePaths')
   maxQuantParameters.appendChild(filePaths) 

   experiments = document.createElement('experiments')
   maxQuantParameters.appendChild(experiments) 

   fractions = document.createElement('fractions')
   maxQuantParameters.appendChild(fractions) 

   ptms = document.createElement('ptms')
   maxQuantParameters.appendChild(ptms) 

   paramGroupIndices = document.createElement('paramGroupIndices')
   maxQuantParameters.appendChild(paramGroupIndices) 

   referenceChannels = document.createElement('referenceChannel')
   maxQuantParameters.appendChild(referenceChannels) 

   i=0
   for file in par["input"]:
      prefix =str(i)+'_'
      createParameter(document,filePaths,parameterDictionary,'string',file,prefix)
      createParameter(document,fractions,parameterDictionary,'short','32767',prefix)
      createParameter(document,ptms,parameterDictionary,'boolean','False',prefix)
      createParameter(document,paramGroupIndices,parameterDictionary,'int','0',prefix)
      createParameter(document,referenceChannels,parameterDictionary,'string','',prefix)

   i=0
   for experiment in experiment_names:
      createParameter(document,experiments,parameterDictionary,'string',experiment,str(i)+'_')

   updateParameter(document,maxQuantParameters,parameterDictionary,'msInstrument',ms_instrument_settings.at[par["ms_instrument"], "msInstrument"])
   updateParameter(document,maxQuantParameters,parameterDictionary,'maxCharge',ms_instrument_settings.at[par["ms_instrument"], "maxCharge"])
   updateParameter(document,maxQuantParameters,parameterDictionary,'minPeakLen',ms_instrument_settings.at[par["ms_instrument"], "minPeakLen"])
   updateParameter(document,maxQuantParameters,parameterDictionary,'diaMinPeakLen',ms_instrument_settings.at[par["ms_instrument"], "diaMinPeakLen"])
   updateParameter(document,maxQuantParameters,parameterDictionary,'useMs1Centroids',ms_instrument_settings.at[par["ms_instrument"], "useMs1Centroids"])
   updateParameter(document,maxQuantParameters,parameterDictionary,'useMs2Centroids',ms_instrument_settings.at[par["ms_instrument"], "useMs2Centroids"])

   updateParameter(document,maxQuantParameters,parameterDictionary,'intensityDetermination',ms_instrument_settings.at[par["ms_instrument"], "intensityDetermination"])
   updateParameter(document,maxQuantParameters,parameterDictionary,'centroidMatchTol',ms_instrument_settings.at[par["ms_instrument"], "centroidMatchTol"])
   updateParameter(document,maxQuantParameters,parameterDictionary,'valleyFactor',ms_instrument_settings.at[par["ms_instrument"], "valleyFactor"])
   updateParameter(document,maxQuantParameters,parameterDictionary,'advancedPeakSplitting',ms_instrument_settings.at[par["ms_instrument"], "advancedPeakSplitting"])
   updateParameter(document,maxQuantParameters,parameterDictionary,'intensityThresholdMs1',ms_instrument_settings.at[par["ms_instrument"], "intensityThresholdMs1"])
   updateParameter(document,maxQuantParameters,parameterDictionary,'intensityThresholdMs2',ms_instrument_settings.at[par["ms_instrument"], "intensityThresholdMs2"])

   updateParameter(document,maxQuantParameters,parameterDictionary,'lcmsRunType',par["lcms_run_type"])
   #setParameter('lfqMode',{group_type_settings.at[par["lcms_run_type"], "lfqMode"]})
   updateParameter(document,maxQuantParameters,parameterDictionary,'neucodeMaxPpm',group_type_settings.at[par["lcms_run_type"], "neucodeMaxPpm"])
   updateParameter(document,maxQuantParameters,parameterDictionary,'neucodeResolution',group_type_settings.at[par["lcms_run_type"], "neucodeResolution"])
   updateParameter(document,maxQuantParameters,parameterDictionary,'neucodeResolutionInMda',group_type_settings.at[par["lcms_run_type"], "neucodeResolutionInMda"])
   updateParameter(document,maxQuantParameters,parameterDictionary,'neucodeInSilicoLowRes',group_type_settings.at[par["lcms_run_type"], "neucodeInSilicoLowRes"])
   updateParameter(document,maxQuantParameters,parameterDictionary,'maxLabeledAa',group_type_settings.at[par["lcms_run_type"], "maxLabeledAa"])

   updateParameter(document,maxQuantParameters,parameterDictionary,'mainSearchTol',ms_instrument_settings.at[par["ms_instrument"], "mainSearchTol"])
   updateParameter(document,maxQuantParameters,parameterDictionary,'isotopeMatchTol',ms_instrument_settings.at[par["ms_instrument"], "isotopeMatchTol"])
   updateParameter(document,maxQuantParameters,parameterDictionary,'isotopeMatchTolInPpm',ms_instrument_settings.at[par["ms_instrument"], "isotopeMatchTolInPpm"])
   updateParameter(document,maxQuantParameters,parameterDictionary,'checkMassDeficit',ms_instrument_settings.at[par["ms_instrument"], "checkMassDeficit"])
   updateParameter(document,maxQuantParameters,parameterDictionary,'intensityDependentCalibration',ms_instrument_settings.at[par["ms_instrument"], "intensityDependentCalibration"])
   updateParameter(document,maxQuantParameters,parameterDictionary,'minScoreForCalibration',ms_instrument_settings.at[par["ms_instrument"], "minScoreForCalibration"])

   updateParameter(document,maxQuantParameters,parameterDictionary,'reporterFraction',group_type_settings.at[par["lcms_run_type"], "reporterFraction"])
   updateParameter(document,maxQuantParameters,parameterDictionary,'reporterBasePeakRatio',group_type_settings.at[par["lcms_run_type"], "reporterBasePeakRatio"])
   updateParameter(document,maxQuantParameters,parameterDictionary,'timsHalfWidth',group_type_settings.at[par["lcms_run_type"], "timsHalfWidth"])
   updateParameter(document,maxQuantParameters,parameterDictionary,'timsStep',group_type_settings.at[par["lcms_run_type"], "timsStep"])
   updateParameter(document,maxQuantParameters,parameterDictionary,'timsResolution',group_type_settings.at[par["lcms_run_type"], "timsResolution"])
   updateParameter(document,maxQuantParameters,parameterDictionary,'timsMinMsmsIntensity',group_type_settings.at[par["lcms_run_type"], "timsMinMsmsIntensity"])

   updateParameter(document,maxQuantParameters,parameterDictionary,"diaTopNForQuant",ms_instrument_settings.at[par["ms_instrument"], "diaTopNForQuant"])
   updateParameter(document,maxQuantParameters,parameterDictionary,"diaBackgroundSubtraction",ms_instrument_settings.at[par["ms_instrument"], "diaBackgroundSubtraction"])
   updateParameter(document,maxQuantParameters,parameterDictionary,"diaBackgroundSubtractionQuantile",ms_instrument_settings.at[par["ms_instrument"], "diaBackgroundSubtractionQuantile"])
   updateParameter(document,maxQuantParameters,parameterDictionary,"diaLfqWeightedMedian",ms_instrument_settings.at[par["ms_instrument"], "diaLfqWeightedMedian"])

   param_content = toString(document)

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



