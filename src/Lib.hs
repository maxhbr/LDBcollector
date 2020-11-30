{-# LANGUAGE OverloadedStrings #-}
module Lib
  ( module X
  , readFacts
  , calculateLicenses, calculateSPDXLicenses
  , cleanupAndMakeOutputFolder
  , Configuration (..)
  , runLDBCore
  ) where

import qualified Prelude as P
import           MyPrelude

import qualified Data.Vector as V
import qualified Data.Map as M
import qualified Data.ByteString.Lazy as BL
import qualified Data.Text.IO as T
import           Data.Aeson.Encode.Pretty (encodePretty)
import           GHC.IO.Encoding (setLocaleEncoding, utf8)
import           System.Environment

import           Model.License as X
import           Model.Query as X
import           Model.LicenseClusterer as X

import           Collectors as X

import           Processors.Rating as X
import           Processors.ToPage as X

import           Generators.PandocWriter as X
import           Generators.DetailsWriter as X
import           Generators.GraphizWriter as X
import           Generators.Stats as X
import           Generators.FindClusters as X
import           Generators.FactLicenses as X
import           Generators.LicenseJsonsWriter as X
import           Generators.FactJsonsWriter as X

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
  writeFactsLicenses outputFolder facts licensesByName

data Configuration
  = Configuration
  { cLFCs        :: [LicenseFactClassifier]
  , cRatingRules :: RatingRules
  , cOverrides   :: [Override]
  }

mkCollectors :: Configuration -> [(LicenseFactClassifier, IO Facts)]
mkCollectors conf@Configuration{cLFCs = chosenLFCs} =
  (overrideLFC, loadOverrideFacts (cOverrides conf)) :
  filter (\(lfc,_) -> chosenLFCs == [] || lfc `elem` chosenLFCs)
  allCollectors

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

cleanupAndMakeOutputFolder :: FilePath -> IO FilePath
cleanupAndMakeOutputFolder outputFolder = do
  dirExists <- doesDirectoryExist outputFolder
  when dirExists $
    removeDirectoryRecursive outputFolder
  createDirectory outputFolder
  return outputFolder

