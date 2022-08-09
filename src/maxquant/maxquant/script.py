import os
import re
import subprocess
import tempfile
import shutil
import pandas as pd

## VIASH START
par = {
   "input": ["resources_test/zenodo_4274987/raw/Sample1.raw", "resources_test/zenodo_4274987/raw/Sample2.raw"],
   "reference": "resources_test/maxquant_test_data/Fasta/20211015_Kistler_Human.Cow.ZEBOV_NP_P2A_VP35_P2A_VP30.fasta",
   "output": "output/",
   "match_between_runs": True
}
meta = {
   "resources_dir": "src/maxquant/maxquant/"
}
## VIASH END

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
   param_content = f"""<?xml version="1.0" encoding="utf-8"?>
<MaxQuantParams xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
   <fastaFiles>"""

   # TODO: make taxonomy optional
   for path, taxid in zip(par["reference"], par["ref_taxonomy_id"]):
      param_content += f"""
      <FastaFileInfo>
         <fastaFilePath>{path}</fastaFilePath>
         <identifierParseRule>>.*\|(.*)\|</identifierParseRule>
         <descriptionParseRule>>(.*)</descriptionParseRule>
         <taxonomyParseRule></taxonomyParseRule>
         <variationParseRule></variationParseRule>
         <modificationParseRule></modificationParseRule>
         <taxonomyId>{taxid}</taxonomyId>
      </FastaFileInfo>"""

   param_content += f"""
   </fastaFiles>
   <fastaFilesProteogenomics>
   </fastaFilesProteogenomics>
   <fastaFilesFirstSearch>
   </fastaFilesFirstSearch>
   <fixedSearchFolder></fixedSearchFolder>
   <andromedaCacheSize>350000</andromedaCacheSize>
   <advancedRatios>True</advancedRatios>
   <pvalThres>0.005</pvalThres>
   <rtShift>False</rtShift>
   <separateLfq>False</separateLfq>
   <lfqStabilizeLargeRatios>True</lfqStabilizeLargeRatios>
   <lfqRequireMsms>True</lfqRequireMsms>
   <lfqBayesQuant>False</lfqBayesQuant>
   <decoyMode>revert</decoyMode>
   <boxCarMode>all</boxCarMode>
   <includeContaminants>True</includeContaminants>
   <maxPeptideMass>4600</maxPeptideMass>
   <epsilonMutationScore>True</epsilonMutationScore>
   <mutatedPeptidesSeparately>True</mutatedPeptidesSeparately>
   <proteogenomicPeptidesSeparately>True</proteogenomicPeptidesSeparately>
   <minDeltaScoreUnmodifiedPeptides>0</minDeltaScoreUnmodifiedPeptides>
   <minDeltaScoreModifiedPeptides>6</minDeltaScoreModifiedPeptides>
   <minScoreUnmodifiedPeptides>0</minScoreUnmodifiedPeptides>
   <minScoreModifiedPeptides>40</minScoreModifiedPeptides>
   <secondPeptide>True</secondPeptide>
   <matchBetweenRuns>{par["match_between_runs"]}</matchBetweenRuns>
   <matchUnidentifiedFeatures>False</matchUnidentifiedFeatures>
   <matchBetweenRunsFdr>False</matchBetweenRunsFdr>
   <dependentPeptides>False</dependentPeptides>
   <dependentPeptideFdr>0</dependentPeptideFdr>
   <dependentPeptideMassBin>0</dependentPeptideMassBin>
   <dependentPeptidesBetweenRuns>False</dependentPeptidesBetweenRuns>
   <dependentPeptidesWithinExperiment>False</dependentPeptidesWithinExperiment>
   <dependentPeptidesWithinParameterGroup>False</dependentPeptidesWithinParameterGroup>
   <dependentPeptidesRestrictFractions>False</dependentPeptidesRestrictFractions>
   <dependentPeptidesFractionDifference>0</dependentPeptidesFractionDifference>
   <ibaq>False</ibaq>
   <top3>False</top3>
   <independentEnzymes>False</independentEnzymes>
   <useDeltaScore>False</useDeltaScore>
   <splitProteinGroupsByTaxonomy>False</splitProteinGroupsByTaxonomy>
   <taxonomyLevel>Species</taxonomyLevel>
   <avalon>False</avalon>
   <nModColumns>3</nModColumns>
   <ibaqLogFit>False</ibaqLogFit>
   <ibaqChargeNormalization>False</ibaqChargeNormalization>
   <razorProteinFdr>True</razorProteinFdr>
   <deNovoSequencing>False</deNovoSequencing>
   <deNovoVarMods>False</deNovoVarMods>
   <deNovoCompleteSequence>False</deNovoCompleteSequence>
   <deNovoCalibratedMasses>False</deNovoCalibratedMasses>
   <deNovoMaxIterations>0</deNovoMaxIterations>
   <deNovoProteaseReward>0</deNovoProteaseReward>
   <deNovoProteaseRewardTof>0</deNovoProteaseRewardTof>
   <deNovoAgPenalty>0</deNovoAgPenalty>
   <deNovoGgPenalty>0</deNovoGgPenalty>
   <deNovoUseComplementScore>True</deNovoUseComplementScore>
   <deNovoUseProteaseScore>True</deNovoUseProteaseScore>
   <deNovoUseWaterLossScore>True</deNovoUseWaterLossScore>
   <deNovoUseAmmoniaLossScore>True</deNovoUseAmmoniaLossScore>
   <deNovoUseA2Score>True</deNovoUseA2Score>
   <massDifferenceSearch>False</massDifferenceSearch>
   <isotopeCalc>False</isotopeCalc>
   <writePeptidesForSpectrumFile></writePeptidesForSpectrumFile>
   <intensityPredictionsFile>
   </intensityPredictionsFile>
   <minPepLen>7</minPepLen>
   <psmFdrCrosslink>0.01</psmFdrCrosslink>
   <peptideFdr>0.01</peptideFdr>
   <proteinFdr>0.01</proteinFdr>
   <siteFdr>0.01</siteFdr>
   <minPeptideLengthForUnspecificSearch>8</minPeptideLengthForUnspecificSearch>
   <maxPeptideLengthForUnspecificSearch>25</maxPeptideLengthForUnspecificSearch>
   <useNormRatiosForOccupancy>True</useNormRatiosForOccupancy>
   <minPeptides>1</minPeptides>
   <minRazorPeptides>1</minRazorPeptides>
   <minUniquePeptides>0</minUniquePeptides>
   <useCounterparts>False</useCounterparts>
   <advancedSiteIntensities>True</advancedSiteIntensities>
   <customProteinQuantification>False</customProteinQuantification>
   <customProteinQuantificationFile></customProteinQuantificationFile>
   <minRatioCount>2</minRatioCount>
   <restrictProteinQuantification>True</restrictProteinQuantification>
   <restrictMods>
      <string>Oxidation (M)</string>
      <string>Acetyl (Protein N-term)</string>
   </restrictMods>
   <matchingTimeWindow>{match_between_runs_settings.at[par["match_between_runs"], "matchingTimeWindow"]}</matchingTimeWindow>
   <matchingIonMobilityWindow>{match_between_runs_settings.at[par["match_between_runs"], "matchingIonMobilityWindow"]}</matchingIonMobilityWindow>
   <alignmentTimeWindow>{match_between_runs_settings.at[par["match_between_runs"], "alignmentTimeWindow"]}</alignmentTimeWindow>
   <alignmentIonMobilityWindow>{match_between_runs_settings.at[par["match_between_runs"], "alignmentIonMobilityWindow"]}</alignmentIonMobilityWindow>
   <numberOfCandidatesMsms>15</numberOfCandidatesMsms>
   <compositionPrediction>0</compositionPrediction>
   <quantMode>1</quantMode>
   <massDifferenceMods>
   </massDifferenceMods>
   <mainSearchMaxCombinations>200</mainSearchMaxCombinations>
   <writeMsScansTable>{"msScans" in par["write_tables"]}</writeMsScansTable>
   <writeMsmsScansTable>{"msmsScans" in par["write_tables"]}</writeMsmsScansTable>
   <writePasefMsmsScansTable>{"pasefMsmsScans" in par["write_tables"]}</writePasefMsmsScansTable>
   <writeAccumulatedMsmsScansTable>{"accumulatedMsmsScans" in par["write_tables"]}</writeAccumulatedMsmsScansTable>
   <writeMs3ScansTable>{"ms3Scans" in par["write_tables"]}</writeMs3ScansTable>
   <writeAllPeptidesTable>{"allPeptides" in par["write_tables"]}</writeAllPeptidesTable>
   <writeMzRangeTable>{"mzRange" in par["write_tables"]}</writeMzRangeTable>
   <writeDiaFragmentTable>{"DIA fragments" in par["write_tables"]}</writeDiaFragmentTable>
   <writeDiaFragmentQuantTable>{"DIA fragments quant" in par["write_tables"]}</writeDiaFragmentQuantTable>
   <writeMzTab>{"mzTab" in par["write_tables"]}</writeMzTab>
   <disableMd5>False</disableMd5>
   <cacheBinInds>True</cacheBinInds>
   <etdIncludeB>False</etdIncludeB>
   <ms2PrecursorShift>0</ms2PrecursorShift>
   <complementaryIonPpm>20</complementaryIonPpm>
   <variationParseRule></variationParseRule>
   <variationMode>none</variationMode>
   <useSeriesReporters>False</useSeriesReporters>
   <name>session1</name>
   <maxQuantVersion>2.0.3.0</maxQuantVersion>
   <pluginFolder></pluginFolder>
   <numThreads>{par["num_cores"]}</numThreads>
   <emailAddress></emailAddress>
   <smtpHost></smtpHost>
   <emailFromAddress></emailFromAddress>
   <fixedCombinedFolder>{par["output"]}/</fixedCombinedFolder>
   <fullMinMz>-1.79769313486232E+308</fullMinMz>
   <fullMaxMz>1.79769313486232E+308</fullMaxMz>
   <sendEmail>False</sendEmail>
   <ionCountIntensities>False</ionCountIntensities>
   <verboseColumnHeaders>False</verboseColumnHeaders>
   <calcPeakProperties>True</calcPeakProperties>
   <showCentroidMassDifferences>False</showCentroidMassDifferences>
   <showIsotopeMassDifferences>False</showIsotopeMassDifferences>
   <useDotNetCore>True</useDotNetCore>
   <profilePerformance>False</profilePerformance>
   <filePaths>{''.join([ f"{endl}      <string>{file}</string>" for file in par["input"] ])}
   </filePaths>
   <experiments>{''.join([ f"{endl}      <string>{exp}</string>" for exp in experiment_names ])}
   </experiments>
   <fractions>{''.join([ f"{endl}      <short>32767</short>" for file in par["input"] ])}
   </fractions>
   <ptms>{''.join([ f"{endl}      <boolean>False</boolean>" for file in par["input"] ])}
   </ptms>
   <paramGroupIndices>{''.join([ f"{endl}      <int>0</int>" for file in par["input"] ])}
   </paramGroupIndices>
   <referenceChannel>{''.join([ f"{endl}      <string></string>" for file in par["input"] ])}
   </referenceChannel>
   <intensPred>False</intensPred>
   <intensPredModelReTrain>False</intensPredModelReTrain>
   <lfqTopNPeptides>0</lfqTopNPeptides>
   <diaJoinPrecChargesForLfq>False</diaJoinPrecChargesForLfq>
   <diaFragChargesForQuant>1</diaFragChargesForQuant>
   <timsRearrangeSpectra>False</timsRearrangeSpectra>
   <gridSpacing>0.5</gridSpacing>
   <proteinGroupingFile></proteinGroupingFile>
   <parameterGroups>
      <parameterGroup>
         <msInstrument>{ms_instrument_settings.at[par["ms_instrument"], "msInstrument"]}</msInstrument>
         <maxCharge>{ms_instrument_settings.at[par["ms_instrument"], "maxCharge"]}</maxCharge>
         <minPeakLen>{ms_instrument_settings.at[par["ms_instrument"], "minPeakLen"]}</minPeakLen>
         <diaMinPeakLen>{ms_instrument_settings.at[par["ms_instrument"], "diaMinPeakLen"]}</diaMinPeakLen>
         <useMs1Centroids>{ms_instrument_settings.at[par["ms_instrument"], "useMs1Centroids"]}</useMs1Centroids>
         <useMs2Centroids>{ms_instrument_settings.at[par["ms_instrument"], "useMs2Centroids"]}</useMs2Centroids>
         <cutPeaks>True</cutPeaks>
         <gapScans>1</gapScans>
         <minTime>NaN</minTime>
         <maxTime>NaN</maxTime>
         <matchType>MatchFromAndTo</matchType>
         <intensityDetermination>{ms_instrument_settings.at[par["ms_instrument"], "intensityDetermination"]}</intensityDetermination>
         <centroidMatchTol>{ms_instrument_settings.at[par["ms_instrument"], "centroidMatchTol"]}</centroidMatchTol>
         <centroidMatchTolInPpm>True</centroidMatchTolInPpm>
         <centroidHalfWidth>35</centroidHalfWidth>
         <centroidHalfWidthInPpm>True</centroidHalfWidthInPpm>
         <valleyFactor>{ms_instrument_settings.at[par["ms_instrument"], "valleyFactor"]}</valleyFactor>
         <isotopeValleyFactor>1.2</isotopeValleyFactor>
         <advancedPeakSplitting>{ms_instrument_settings.at[par["ms_instrument"], "advancedPeakSplitting"]}</advancedPeakSplitting>
         <intensityThresholdMs1>{ms_instrument_settings.at[par["ms_instrument"], "intensityThresholdMs1"]}</intensityThresholdMs1>
         <intensityThresholdMs2>{ms_instrument_settings.at[par["ms_instrument"], "intensityThresholdMs2"]}</intensityThresholdMs2>
         <labelMods>
            <string></string>
         </labelMods>
         <lcmsRunType>{par["lcms_run_type"]}</lcmsRunType>
         <reQuantify>False</reQuantify>
         <lfqMode>{"1" if par["lfq_mode"] == "LFQ" else "0"}</lfqMode>
         <lfqNormClusterSize>80</lfqNormClusterSize>
         <lfqMinEdgesPerNode>3</lfqMinEdgesPerNode>
         <lfqAvEdgesPerNode>6</lfqAvEdgesPerNode>
         <lfqMaxFeatures>100000</lfqMaxFeatures>
         <neucodeMaxPpm>{group_type_settings.at[par["lcms_run_type"], "neucodeMaxPpm"]}</neucodeMaxPpm>
         <neucodeResolution>{group_type_settings.at[par["lcms_run_type"], "neucodeResolution"]}</neucodeResolution>
         <neucodeResolutionInMda>{group_type_settings.at[par["lcms_run_type"], "neucodeResolutionInMda"]}</neucodeResolutionInMda>
         <neucodeInSilicoLowRes>{group_type_settings.at[par["lcms_run_type"], "neucodeInSilicoLowRes"]}</neucodeInSilicoLowRes>
         <fastLfq>True</fastLfq>
         <lfqRestrictFeatures>False</lfqRestrictFeatures>
         <lfqMinRatioCount>2</lfqMinRatioCount>
         <maxLabeledAa>{group_type_settings.at[par["lcms_run_type"], "maxLabeledAa"]}</maxLabeledAa>
         <maxNmods>5</maxNmods>
         <maxMissedCleavages>2</maxMissedCleavages>
         <multiplicity>1</multiplicity>
         <enzymeMode>0</enzymeMode>
         <complementaryReporterType>0</complementaryReporterType>
         <reporterNormalization>0</reporterNormalization>
         <neucodeIntensityMode>0</neucodeIntensityMode>
         <fixedModifications>
            <string>Carbamidomethyl (C)</string>
         </fixedModifications>
         <enzymes>
            <string>Trypsin/P</string>
         </enzymes>
         <enzymesFirstSearch>
         </enzymesFirstSearch>
         <enzymeModeFirstSearch>0</enzymeModeFirstSearch>
         <useEnzymeFirstSearch>False</useEnzymeFirstSearch>
         <useVariableModificationsFirstSearch>False</useVariableModificationsFirstSearch>
         <variableModifications>
            <string>Oxidation (M)</string>
            <string>Acetyl (Protein N-term)</string>
         </variableModifications>
         <useMultiModification>False</useMultiModification>
         <multiModifications>
         </multiModifications>
         <isobaricLabels>
         </isobaricLabels>
         <neucodeLabels>
         </neucodeLabels>
         <variableModificationsFirstSearch>
         </variableModificationsFirstSearch>
         <hasAdditionalVariableModifications>False</hasAdditionalVariableModifications>
         <additionalVariableModifications>
         </additionalVariableModifications>
         <additionalVariableModificationProteins>
         </additionalVariableModificationProteins>
         <doMassFiltering>True</doMassFiltering>
         <firstSearchTol>20</firstSearchTol>
         <mainSearchTol>{ms_instrument_settings.at[par["ms_instrument"], "mainSearchTol"]}</mainSearchTol>
         <searchTolInPpm>True</searchTolInPpm>
         <isotopeMatchTol>{ms_instrument_settings.at[par["ms_instrument"], "isotopeMatchTol"]}</isotopeMatchTol>
         <isotopeMatchTolInPpm>{ms_instrument_settings.at[par["ms_instrument"], "isotopeMatchTolInPpm"]}</isotopeMatchTolInPpm>
         <isotopeTimeCorrelation>0.6</isotopeTimeCorrelation>
         <theorIsotopeCorrelation>0.6</theorIsotopeCorrelation>
         <checkMassDeficit>{ms_instrument_settings.at[par["ms_instrument"], "checkMassDeficit"]}</checkMassDeficit>
         <recalibrationInPpm>True</recalibrationInPpm>
         <intensityDependentCalibration>{ms_instrument_settings.at[par["ms_instrument"], "intensityDependentCalibration"]}</intensityDependentCalibration>
         <minScoreForCalibration>{ms_instrument_settings.at[par["ms_instrument"], "minScoreForCalibration"]}</minScoreForCalibration>
         <matchLibraryFile>False</matchLibraryFile>
         <libraryFile></libraryFile>
         <matchLibraryMassTolPpm>0</matchLibraryMassTolPpm>
         <matchLibraryTimeTolMin>0</matchLibraryTimeTolMin>
         <matchLabelTimeTolMin>0</matchLabelTimeTolMin>
         <reporterMassTolerance>NaN</reporterMassTolerance>
         <reporterPif>{group_type_settings.at[par["lcms_run_type"], "reporterPif"]}</reporterPif>
         <filterPif>False</filterPif>
         <reporterFraction>{group_type_settings.at[par["lcms_run_type"], "reporterFraction"]}</reporterFraction>
         <reporterBasePeakRatio>{group_type_settings.at[par["lcms_run_type"], "reporterBasePeakRatio"]}</reporterBasePeakRatio>
         <timsHalfWidth>{group_type_settings.at[par["lcms_run_type"], "timsHalfWidth"]}</timsHalfWidth>
         <timsStep>{group_type_settings.at[par["lcms_run_type"], "timsStep"]}</timsStep>
         <timsResolution>{group_type_settings.at[par["lcms_run_type"], "timsResolution"]}</timsResolution>
         <timsMinMsmsIntensity>{group_type_settings.at[par["lcms_run_type"], "timsMinMsmsIntensity"]}</timsMinMsmsIntensity>
         <timsRemovePrecursor>True</timsRemovePrecursor>
         <timsIsobaricLabels>False</timsIsobaricLabels>
         <timsCollapseMsms>True</timsCollapseMsms>
         <crossLinkingType>0</crossLinkingType>
         <crossLinker></crossLinker>
         <minMatchXl>3</minMatchXl>
         <minPairedPepLenXl>6</minPairedPepLenXl>
         <minScore_Dipeptide>40</minScore_Dipeptide>
         <minScore_Monopeptide>0</minScore_Monopeptide>
         <minScore_PartialCross>10</minScore_PartialCross>
         <crosslinkOnlyIntraProtein>False</crosslinkOnlyIntraProtein>
         <crosslinkIntensityBasedPrecursor>True</crosslinkIntensityBasedPrecursor>
         <isHybridPrecDetermination>False</isHybridPrecDetermination>
         <topXcross>3</topXcross>
         <doesSeparateInterIntraProteinCross>False</doesSeparateInterIntraProteinCross>
         <crosslinkMaxMonoUnsaturated>0</crosslinkMaxMonoUnsaturated>
         <crosslinkMaxMonoSaturated>0</crosslinkMaxMonoSaturated>
         <crosslinkMaxDiUnsaturated>0</crosslinkMaxDiUnsaturated>
         <crosslinkMaxDiSaturated>0</crosslinkMaxDiSaturated>
         <crosslinkModifications>
         </crosslinkModifications>
         <crosslinkFastaFiles>
         </crosslinkFastaFiles>
         <crosslinkSites>
         </crosslinkSites>
         <crosslinkNetworkFiles>
         </crosslinkNetworkFiles>
         <crosslinkMode></crosslinkMode>
         <peakRefinement>False</peakRefinement>
         <isobaricSumOverWindow>True</isobaricSumOverWindow>
         <isobaricWeightExponent>0.75</isobaricWeightExponent>
         <collapseMsmsOnIsotopePatterns>False</collapseMsmsOnIsotopePatterns>
         <diaLibraryType>0</diaLibraryType>
         <diaLibraryPaths>
         </diaLibraryPaths>
         <diaPeptidePaths>
         </diaPeptidePaths>
         <diaEvidencePaths>
         </diaEvidencePaths>
         <diaMsmsPaths>
         </diaMsmsPaths>
         <diaInitialPrecMassTolPpm>20</diaInitialPrecMassTolPpm>
         <diaInitialFragMassTolPpm>20</diaInitialFragMassTolPpm>
         <diaCorrThresholdFeatureClustering>0.85</diaCorrThresholdFeatureClustering>
         <diaPrecTolPpmFeatureClustering>2</diaPrecTolPpmFeatureClustering>
         <diaFragTolPpmFeatureClustering>2</diaFragTolPpmFeatureClustering>
         <diaScoreN>7</diaScoreN>
         <diaMinScore>1.99</diaMinScore>
         <diaXgBoostBaseScore>0.4</diaXgBoostBaseScore>
         <diaXgBoostSubSample>0.9</diaXgBoostSubSample>
         <centroidPosition>0</centroidPosition>
         <diaQuantMethod>7</diaQuantMethod>
         <diaFeatureQuantMethod>2</diaFeatureQuantMethod>
         <lfqNormType>1</lfqNormType>
         <diaTopNForQuant>{ms_instrument_settings.at[par["ms_instrument"], "diaTopNForQuant"]}</diaTopNForQuant>
         <diaMinMsmsIntensityForQuant>0</diaMinMsmsIntensityForQuant>
         <diaTopMsmsIntensityQuantileForQuant>0.85</diaTopMsmsIntensityQuantileForQuant>
         <diaPrecursorFilterType>0</diaPrecursorFilterType>
         <diaMinFragmentOverlapScore>1</diaMinFragmentOverlapScore>
         <diaMinPrecursorScore>0.5</diaMinPrecursorScore>
         <diaMinProfileCorrelation>0</diaMinProfileCorrelation>
         <diaXgBoostMinChildWeight>9</diaXgBoostMinChildWeight>
         <diaXgBoostMaximumTreeDepth>12</diaXgBoostMaximumTreeDepth>
         <diaXgBoostEstimators>580</diaXgBoostEstimators>
         <diaXgBoostGamma>0.9</diaXgBoostGamma>
         <diaXgBoostMaxDeltaStep>3</diaXgBoostMaxDeltaStep>
         <diaGlobalMl>True</diaGlobalMl>
         <diaAdaptiveMassAccuracy>False</diaAdaptiveMassAccuracy>
         <diaMassWindowFactor>3.3</diaMassWindowFactor>
         <diaRtPrediction>False</diaRtPrediction>
         <diaRtPredictionSecondRound>False</diaRtPredictionSecondRound>
         <diaNoMl>False</diaNoMl>
         <diaPermuteRt>False</diaPermuteRt>
         <diaPermuteCcs>False</diaPermuteCcs>
         <diaBackgroundSubtraction>{ms_instrument_settings.at[par["ms_instrument"], "diaBackgroundSubtraction"]}</diaBackgroundSubtraction>
         <diaBackgroundSubtractionQuantile>{ms_instrument_settings.at[par["ms_instrument"], "diaBackgroundSubtractionQuantile"]}</diaBackgroundSubtractionQuantile>
         <diaBackgroundSubtractionFactor>4</diaBackgroundSubtractionFactor>
         <diaLfqWeightedMedian>{ms_instrument_settings.at[par["ms_instrument"], "diaLfqWeightedMedian"]}</diaLfqWeightedMedian>
         <diaTransferQvalue>0.3</diaTransferQvalue>
         <diaOnlyIsosForRecal>True</diaOnlyIsosForRecal>
         <diaMinPeaksForRecal>5</diaMinPeaksForRecal>
         <diaUseFragIntensForMl>False</diaUseFragIntensForMl>
         <diaUseFragMassesForMl>False</diaUseFragMassesForMl>
         <diaMaxTrainInstances>1000000</diaMaxTrainInstances>
      </parameterGroup>
   </parameterGroups>
   <msmsParamsArray>
      <msmsParams>
         <Name>FTMS</Name>
         <MatchTolerance>20</MatchTolerance>
         <MatchToleranceInPpm>True</MatchToleranceInPpm>
         <DeisotopeTolerance>7</DeisotopeTolerance>
         <DeisotopeToleranceInPpm>True</DeisotopeToleranceInPpm>
         <DeNovoTolerance>25</DeNovoTolerance>
         <DeNovoToleranceInPpm>True</DeNovoToleranceInPpm>
         <Deisotope>True</Deisotope>
         <Topx>12</Topx>
         <TopxInterval>100</TopxInterval>
         <HigherCharges>True</HigherCharges>
         <IncludeWater>True</IncludeWater>
         <IncludeAmmonia>True</IncludeAmmonia>
         <DependentLosses>True</DependentLosses>
         <Recalibration>False</Recalibration>
      </msmsParams>
      <msmsParams>
         <Name>ITMS</Name>
         <MatchTolerance>0.5</MatchTolerance>
         <MatchToleranceInPpm>False</MatchToleranceInPpm>
         <DeisotopeTolerance>0.15</DeisotopeTolerance>
         <DeisotopeToleranceInPpm>False</DeisotopeToleranceInPpm>
         <DeNovoTolerance>0.5</DeNovoTolerance>
         <DeNovoToleranceInPpm>False</DeNovoToleranceInPpm>
         <Deisotope>False</Deisotope>
         <Topx>8</Topx>
         <TopxInterval>100</TopxInterval>
         <HigherCharges>True</HigherCharges>
         <IncludeWater>True</IncludeWater>
         <IncludeAmmonia>True</IncludeAmmonia>
         <DependentLosses>True</DependentLosses>
         <Recalibration>False</Recalibration>
      </msmsParams>
      <msmsParams>
         <Name>TOF</Name>
         <MatchTolerance>40</MatchTolerance>
         <MatchToleranceInPpm>True</MatchToleranceInPpm>
         <DeisotopeTolerance>0.01</DeisotopeTolerance>
         <DeisotopeToleranceInPpm>False</DeisotopeToleranceInPpm>
         <DeNovoTolerance>25</DeNovoTolerance>
         <DeNovoToleranceInPpm>True</DeNovoToleranceInPpm>
         <Deisotope>True</Deisotope>
         <Topx>10</Topx>
         <TopxInterval>100</TopxInterval>
         <HigherCharges>True</HigherCharges>
         <IncludeWater>True</IncludeWater>
         <IncludeAmmonia>True</IncludeAmmonia>
         <DependentLosses>True</DependentLosses>
         <Recalibration>False</Recalibration>
      </msmsParams>
      <msmsParams>
         <Name>Unknown</Name>
         <MatchTolerance>20</MatchTolerance>
         <MatchToleranceInPpm>True</MatchToleranceInPpm>
         <DeisotopeTolerance>7</DeisotopeTolerance>
         <DeisotopeToleranceInPpm>True</DeisotopeToleranceInPpm>
         <DeNovoTolerance>25</DeNovoTolerance>
         <DeNovoToleranceInPpm>True</DeNovoToleranceInPpm>
         <Deisotope>True</Deisotope>
         <Topx>12</Topx>
         <TopxInterval>100</TopxInterval>
         <HigherCharges>True</HigherCharges>
         <IncludeWater>True</IncludeWater>
         <IncludeAmmonia>True</IncludeAmmonia>
         <DependentLosses>True</DependentLosses>
         <Recalibration>False</Recalibration>
      </msmsParams>
   </msmsParamsArray>
   <fragmentationParamsArray>
      <fragmentationParams>
         <Name>CID</Name>
         <Connected>False</Connected>
         <ConnectedScore0>1</ConnectedScore0>
         <ConnectedScore1>1</ConnectedScore1>
         <ConnectedScore2>1</ConnectedScore2>
         <InternalFragments>False</InternalFragments>
         <InternalFragmentWeight>1</InternalFragmentWeight>
         <InternalFragmentAas>KRH</InternalFragmentAas>
      </fragmentationParams>
      <fragmentationParams>
         <Name>HCD</Name>
         <Connected>False</Connected>
         <ConnectedScore0>1</ConnectedScore0>
         <ConnectedScore1>1</ConnectedScore1>
         <ConnectedScore2>1</ConnectedScore2>
         <InternalFragments>False</InternalFragments>
         <InternalFragmentWeight>1</InternalFragmentWeight>
         <InternalFragmentAas>KRH</InternalFragmentAas>
      </fragmentationParams>
      <fragmentationParams>
         <Name>ETD</Name>
         <Connected>False</Connected>
         <ConnectedScore0>1</ConnectedScore0>
         <ConnectedScore1>1</ConnectedScore1>
         <ConnectedScore2>1</ConnectedScore2>
         <InternalFragments>False</InternalFragments>
         <InternalFragmentWeight>1</InternalFragmentWeight>
         <InternalFragmentAas>KRH</InternalFragmentAas>
      </fragmentationParams>
      <fragmentationParams>
         <Name>PQD</Name>
         <Connected>False</Connected>
         <ConnectedScore0>1</ConnectedScore0>
         <ConnectedScore1>1</ConnectedScore1>
         <ConnectedScore2>1</ConnectedScore2>
         <InternalFragments>False</InternalFragments>
         <InternalFragmentWeight>1</InternalFragmentWeight>
         <InternalFragmentAas>KRH</InternalFragmentAas>
      </fragmentationParams>
      <fragmentationParams>
         <Name>ETHCD</Name>
         <Connected>False</Connected>
         <ConnectedScore0>1</ConnectedScore0>
         <ConnectedScore1>1</ConnectedScore1>
         <ConnectedScore2>1</ConnectedScore2>
         <InternalFragments>False</InternalFragments>
         <InternalFragmentWeight>1</InternalFragmentWeight>
         <InternalFragmentAas>KRH</InternalFragmentAas>
      </fragmentationParams>
      <fragmentationParams>
         <Name>ETCID</Name>
         <Connected>False</Connected>
         <ConnectedScore0>1</ConnectedScore0>
         <ConnectedScore1>1</ConnectedScore1>
         <ConnectedScore2>1</ConnectedScore2>
         <InternalFragments>False</InternalFragments>
         <InternalFragmentWeight>1</InternalFragmentWeight>
         <InternalFragmentAas>KRH</InternalFragmentAas>
      </fragmentationParams>
      <fragmentationParams>
         <Name>UVPD</Name>
         <Connected>False</Connected>
         <ConnectedScore0>1</ConnectedScore0>
         <ConnectedScore1>1</ConnectedScore1>
         <ConnectedScore2>1</ConnectedScore2>
         <InternalFragments>False</InternalFragments>
         <InternalFragmentWeight>1</InternalFragmentWeight>
         <InternalFragmentAas>KRH</InternalFragmentAas>
      </fragmentationParams>
      <fragmentationParams>
         <Name>Unknown</Name>
         <Connected>False</Connected>
         <ConnectedScore0>1</ConnectedScore0>
         <ConnectedScore1>1</ConnectedScore1>
         <ConnectedScore2>1</ConnectedScore2>
         <InternalFragments>False</InternalFragments>
         <InternalFragmentWeight>1</InternalFragmentWeight>
         <InternalFragmentAas>KRH</InternalFragmentAas>
      </fragmentationParams>
   </fragmentationParamsArray>
</MaxQuantParams>
"""

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