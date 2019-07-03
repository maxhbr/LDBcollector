{-# LANGUAGE OverloadedStrings #-}
module Lib
  ( module X
  , readFacts
  , calculateLicenses, calculateSPDXLicenses
  , writeLicenseJSONs
  ) where

import qualified Prelude as P
import           MyPrelude

import qualified Data.Vector as V
import qualified Data.Map as M
import qualified Data.List as L
import qualified Data.ByteString.Lazy as BL
import           Data.Aeson.Encode.Pretty (encodePretty)

import           Model.License as X
import           Model.Query as X

import           Collectors.SPDX as X
import           Collectors.BlueOak as X
import           Collectors.DFSG as X
import           Collectors.OpenChainPolicyTemplate as X
import           Collectors.Scancode as X
import           Collectors.OSADL as X
import           Collectors.ChooseALicense as X
import           Collectors.FedoraProjectWiki as X
import           Collectors.OSI as X
import           Collectors.Wikipedia as X
import           Collectors.OSLC as X
import           Collectors.Google as X
import           Collectors.OKFN as X
import           Collectors.Gnu as X
import           Collectors.IfrOSS as X
import           Collectors.Override as X

import           Processors.Rating as X

import           Generators.PandocWriter as X

readFacts :: FilePath -> IO Facts
readFacts dataDir = let
    prependDataDir = (dataDir </>)
  in do
    factsFromSPDX <- loadSPDXFacts $ prependDataDir "./spdx-license-list-data/"
    factsFromBlueOak <- loadBlueOakFacts $ prependDataDir "./blue-oak-council-license-list.json"
    factsFromOCPT <- loadOCPTFacts $ prependDataDir "./OpenChainPolicyTemplate/Table.csv"
    factsFromScancode <- loadScancodeFacts $ prependDataDir "./nexB_scancode-toolkit_license_list/"
    factsFromOsadl <- loadOsadlFacts $ prependDataDir "./OSADL/"
    factsFromChooseALicense <- loadChooseALicenseFacts $ prependDataDir "./choosealicense.com/"
    factsFromFedora <- loadFedoraFacts $ prependDataDir "./Fedora_Project_Wiki/"
    factsFromOSI <- loadOSIFacts
    factsFromOSLC <- loadOslcFacts $ prependDataDir "./OSLC-handbook"
    factsFromWikipedia <- loadWikipediaFacts
    factsFromGoogle <- loadGoogleFacts
    factsFromOkfn <- loadOkfnFacts $ prependDataDir "./okfn-licenses.csv"
    factsFromGnu <- loadGnuFacts $ prependDataDir "./gnu.org"
    factsFromDFSG <- loadDFSGFacts
    factsFromIfrOSS <- loadIfrOSSFacts
    factsFromOverride <- loadOverrideFacts
    let facts = V.concat [ factsFromSPDX
                         , factsFromBlueOak
                         , factsFromOCPT
                         , factsFromScancode
                         , factsFromOsadl
                         , factsFromChooseALicense
                         , factsFromFedora
                         , factsFromOSI
                         , factsFromOSLC
                         , factsFromWikipedia
                         , factsFromGoogle
                         , factsFromOkfn
                         , factsFromGnu
                         , factsFromDFSG
                         , factsFromIfrOSS
                         , factsFromOverride
                         ]
    hPutStrLn stderr "... done with collecting data"
    return facts

getLicensesFromFacts :: Vector LicenseName -> Int -> Map LicenseName [LicenseName] -> Facts -> Vector (LicenseName, License)
getLicensesFromFacts ids 0 mapping facts = V.map (\i -> (i, getLicenseFromFacts i (M.findWithDefault [] i mapping) facts)) ids
getLicensesFromFacts ids i mapping facts = let
    lics = getLicensesFromFacts ids 0 mapping facts
    newMapping = M.fromList . V.toList $ V.map (\(name,License fs) -> (name, L.nub (concatMap (unpackCLSR . getImpliedNames) (V.toList fs)))) lics
  in getLicensesFromFacts ids (i - 1) newMapping facts

calculateLicenses :: (Vector LicenseName) -> Facts -> IO [(LicenseName, License)]
calculateLicenses ids facts = do
  let licenses = getLicensesFromFacts ids 1 (M.empty) facts
  hPutStrLn stderr "... done with calculating licenses"

  return $ V.toList licenses

calculateLicensesBySelector :: (LicenseFact -> Bool) -> Facts -> IO [(LicenseName, License)]
calculateLicensesBySelector filterForIds facts = do

  let factsToTakeIDsFrom = V.filter filterForIds facts
      ids = V.map head . V.filter (/= []) . V.map (unpackCLSR . getImpliedNames) $ factsToTakeIDsFrom

  calculateLicenses ids facts

calculateSPDXLicenses :: Facts -> IO [(LicenseName, License)]
calculateSPDXLicenses = calculateLicensesBySelector (\f -> getLicenseFactClassifier f == LFC "SPDX")

writeLicenseJSONs :: FilePath -> [(LicenseName, License)] -> IO ()
writeLicenseJSONs outputFolder licenses = do
  let jsonOutputFolder = outputFolder </> "json"
  createDirectory jsonOutputFolder
  jsons <- mapM (\(i,l) -> let
                    outputFile = i ++ ".json"
                    pOutputFile = i ++ ".pretty.json"
                in do
                   BL.writeFile (jsonOutputFolder </> outputFile) (encode l)
                   BL.writeFile (jsonOutputFolder </> pOutputFile) (encodePretty l)
                   return outputFile) licenses
  BL.writeFile (jsonOutputFolder </> "_all.json") (encodePretty licenses)
  BL.writeFile (jsonOutputFolder </> "_index.json") (encodePretty jsons)

