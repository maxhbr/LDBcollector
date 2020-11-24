{-# LANGUAGE OverloadedStrings #-}
module Lib
  ( module X
  , readFacts
  , calculateLicenses, calculateSPDXLicenses
  , writeLicenseJSONs
  , writeFactsLicenses
  , cleanupAndMakeOutputFolder
  , Configuration (..)
  , runLDBCore
  ) where

import qualified Prelude as P
import           MyPrelude

import qualified Data.Vector as V
import qualified Data.Map as M
import qualified Data.ByteString as B
import qualified Data.ByteString.Lazy as BL
import qualified Data.Text as T
import qualified Data.Text.IO as T
import           Data.Aeson.Encode.Pretty (encodePretty)
import           GHC.IO.Encoding (setLocaleEncoding, utf8)
import           System.Environment
import           Network.Download (openURI)

import           Model.License as X
import           Model.Query as X
import           Model.LicenseClusterer as X

import           Collectors.SPDX as X
import           Collectors.BlueOak as X
import           Collectors.Cavil as X
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
  licensesByName <- (case args of
    [] -> calculateSPDXLicenses
    _  -> calculateLicenses (V.fromList args)) facts

  let pages = toPages (cRatingRules configuration) licensesByName

  outputFolder <- handler facts pages

  writeStats outputFolder facts licensesByName

data Configuration
  = Configuration
  { cLFCs        :: [LicenseFactClassifier]
  , cRatingRules :: RatingRules
  , cOverrides   :: [Override]
  }

mkCollectors :: Configuration -> [(LicenseFactClassifier, IO Facts)]
mkCollectors conf = (overrideLFC, loadOverrideFacts (cOverrides conf)) : filter (\(lfc,_) -> lfc `elem` cLFCs conf)
  [ (spdxLFC, loadSPDXFacts)
  , (blueOakLFC, loadBlueOakFacts)
  , (cavilLFC, loadCavilFacts)
  , (ocptLFC, loadOCPTFacts)
  , (scancodeLFC, loadScancodeFacts)
  , (osadlLFC, loadOsadlFacts)
  , (calLFC, loadChooseALicenseFacts)
  , (fedoraLFC, loadFedoraFacts)
  , (osiLFC, loadOSIFacts)
  , (oslcLFC, loadOslcFacts)
  , (wikipediaLFC, loadWikipediaFacts)
  , (googleLFC, loadGoogleFacts)
  , (okfnLFC, loadOkfnFacts)
  , (gnuLFC, loadGnuFacts)
  , (dfsgLFC, loadDFSGFacts)
  , (ifrOSSLFC, loadIfrOSSFacts)
  ]

readFacts :: Configuration -> IO Facts
readFacts conf = do
  let collectors = mkCollectors conf
  hPutStrLn stderr "chosen collectors:"
  mapM_ (hPutStrLn stderr . show . fst) collectors
  hPutStrLn stderr "start collecting data ..."
  facts <- fmap V.concat $ mapM P.snd collectors
  hPutStrLn stderr "... done with collecting data"
  return facts

calculateLicenses :: Vector LicenseName -> Facts -> IO [(LicenseName, (License, LicenseClusterTree))]
calculateLicenses ids facts = do
  let licenses = getLicensesFromFacts ids facts
  hPutStrLn stderr "... done with calculating licenses"

  return $ V.toList licenses

calculateLicensesBySelector :: (LicenseFact -> Bool) -> Facts -> IO [(LicenseName, (License, LicenseClusterTree))]
calculateLicensesBySelector filterForIds facts = let
  factsToTakeIDsFrom = V.filter filterForIds facts
  ids = V.map head . V.filter (/= []) . V.map (unpackCLSR . getImpliedNames) $ factsToTakeIDsFrom
  in calculateLicenses ids facts

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

writeFactsLicenses :: FilePath -> Facts -> [(LicenseName, License)] -> IO ()
writeFactsLicenses outputFolder facts licenses = let
    lfls :: [(Text, LicenseFactLicense)]
    lfls = (V.toList . V.uniq . V.map (\lfc -> (extractBrc lfc, extractLFL lfc)) . V.map getLicenseFactClassifier) facts
    licenseMap = M.fromList licenses
  in do
  mapM_ (\tpl@(_, lfl) ->let
            licensename = extractLFLName lfl
            outfile = outputFolder </> "LICENSE." ++ licensename
            in do
            print tpl
            when (licensename /= "") $
              case licensename `M.lookup` licenseMap of
                Just lic -> case unpackRLSR (getImpliedText lic) of
                  Just text -> T.writeFile outfile text
                  _         -> hPutStrLn stderr ("... found no text for: " ++ licensename)
                _         -> hPutStrLn stderr ("... found no license for: " ++ licensename)
           ) lfls

cleanupAndMakeOutputFolder :: FilePath -> IO FilePath
cleanupAndMakeOutputFolder outputFolder = do
  dirExists <- doesDirectoryExist outputFolder
  when dirExists $
    removeDirectoryRecursive outputFolder
  createDirectory outputFolder
  return outputFolder

