{-# LANGUAGE OverloadedStrings #-}
module Lib
  ( module X
  , readFacts
  , calculateLicenses, calculateSPDXLicenses
  , writeLicenseJSONs
  , cleanupAndMakeOutputFolder
  , Configuration (..)
  , runLDBCore
  ) where

import qualified Prelude as P
import           MyPrelude

import qualified Data.Vector as V
import qualified Data.Map as M
import qualified Data.ByteString.Lazy as BL
import           Data.Aeson.Encode.Pretty (encodePretty)
import           GHC.IO.Encoding (setLocaleEncoding, utf8)
import           System.Environment

import           Model.License as X
import           Model.Query as X
import           Model.LicenseClusterer as X

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
import           Processors.ToPage as X

import           Generators.PandocWriter as X
import           Generators.DetailsWriter as X
import           Generators.GraphizWriter as X
import           Generators.Stats as X
import           Generators.FindClusters as X

runLDBCore :: Configuration -> (Facts -> [(LicenseName, License, Page, LicenseClusterTree)] -> IO FilePath) -> IO ()
runLDBCore configuration handler = do
  setLocaleEncoding utf8
  args <- getArgs

  facts <- readFacts configuration
  licensesByName <- case args of
    [] -> calculateSPDXLicenses facts
    _  -> calculateLicenses (V.fromList args) facts

  let pages = toPages (cRatingRules configuration) licensesByName

  outputFolder <- handler facts pages

  writeStats outputFolder facts licensesByName

data Configuration
  = Configuration
  { cRatingRules  :: RatingRules
  , cOverrides    :: [Override]
  }

readFacts :: Configuration -> IO Facts
readFacts conf = do
  factsFromSPDX <- loadSPDXFacts
  factsFromBlueOak <- loadBlueOakFacts
  factsFromOCPT <- loadOCPTFacts
  factsFromScancode <- loadScancodeFacts
  factsFromOsadl <- loadOsadlFacts
  factsFromChooseALicense <- loadChooseALicenseFacts
  factsFromFedora <- loadFedoraFacts
  factsFromOSI <- loadOSIFacts
  factsFromOSLC <- loadOslcFacts
  factsFromWikipedia <- loadWikipediaFacts
  factsFromGoogle <- loadGoogleFacts
  factsFromOkfn <- loadOkfnFacts
  factsFromGnu <- loadGnuFacts
  factsFromDFSG <- loadDFSGFacts
  factsFromIfrOSS <- loadIfrOSSFacts
  factsFromOverride <- loadOverrideFacts (cOverrides conf)
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

calculateLicenses :: Vector LicenseName -> Facts -> IO [(LicenseName, (License, LicenseClusterTree))]
calculateLicenses ids facts = do
  let licenses = getLicensesFromFacts ids facts
  hPutStrLn stderr "... done with calculating licenses"

  return $ V.toList licenses

calculateLicensesBySelector :: (LicenseFact -> Bool) -> Facts -> IO [(LicenseName, (License, LicenseClusterTree))]
calculateLicensesBySelector filterForIds facts = do

  let factsToTakeIDsFrom = V.filter filterForIds facts
      ids = V.map head . V.filter (/= []) . V.map (unpackCLSR . getImpliedNames) $ factsToTakeIDsFrom

  calculateLicenses ids facts

calculateSPDXLicenses :: Facts -> IO [(LicenseName, (License, LicenseClusterTree))]
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

cleanupAndMakeOutputFolder :: FilePath -> IO FilePath
cleanupAndMakeOutputFolder outputFolder = do
  dirExists <- doesDirectoryExist outputFolder
  when dirExists $
    removeDirectoryRecursive outputFolder
  createDirectory outputFolder
  return outputFolder

