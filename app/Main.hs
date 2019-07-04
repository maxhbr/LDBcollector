{-# LANGUAGE OverloadedStrings #-}
module Main where

import qualified Prelude as P
import           MyPrelude

import           Control.Monad
import qualified Data.Map as M
import qualified Data.Vector as V
import           GHC.IO.Encoding
import           System.Environment
import           System.IO

import Lib
import FindClusters

echoStatsOnFacts :: Handle -> [LicenseFact] -> IO ()
echoStatsOnFacts handle fs = let
    counts :: [LicenseFactClassifier] -> Map LicenseFactClassifier Int
    counts = let
        countsFun :: Map LicenseFactClassifier Int -> LicenseFactClassifier -> Map LicenseFactClassifier Int
        countsFun m lfc = M.insertWith (+) lfc 1 m
      in foldl' countsFun M.empty
  in do
    hPutStrLn handle ("Number of facts: " ++ show (length fs))
    mapM_ (hPutStrLn handle
            . (\(k,n) -> "    " ++ show k ++ ": " ++ show n))
      . M.assocs
      . counts
      $ map getLicenseFactClassifier fs

echoStatsOnLicenses :: Handle -> FilePath -> [(LicenseName, License)] -> IO ()
echoStatsOnLicenses handle statsFolder lics = do
  hPutStrLn handle ("Number of Licenses: " ++ show (length lics))
  let fsOfLics = (concatMap (\(_,License fs) ->  V.toList fs) lics)
  echoStatsOnFacts handle fsOfLics
  writeClusters handle (statsFolder </> "clusters_from_fatcs_from_lics.csv") (V.fromList fsOfLics)
  writeClustersFromLicenses handle (statsFolder </> "clusters_from_lics.csv") lics

writeStats :: FilePath -> Facts -> [(LicenseName, License)] -> IO ()
writeStats outputFolder fs lics = do
  let statsFolder = outputFolder </> "_stats"
  createDirectory statsFolder


  handle <- openFile (statsFolder </> "stats.txt") WriteMode
  hPutStrLn handle "## Stats:"
  hPutStrLn handle "### Stats on Facts:"
  echoStatsOnFacts handle (V.toList fs)
  writeClusters handle (statsFolder </> "clusters_from_all_facts.csv") fs
  hPutStrLn handle "### Stats on Licenses:"
  echoStatsOnLicenses handle statsFolder lics
  hClose handle

cleanupAndMakeOutputFolder :: IO FilePath
cleanupAndMakeOutputFolder = do
  let outputFolder = "_generated/"
  dirExists <- doesDirectoryExist outputFolder
  when dirExists $
    removeDirectoryRecursive outputFolder
  createDirectory outputFolder

  return outputFolder

main :: IO ()
main = do
  setLocaleEncoding utf8

  args <- getArgs

  -- harvest facts
  facts <- readFacts "./data"

  -- write output
  outputFolder <- cleanupAndMakeOutputFolder

  -- calculate licenses
  licenses <- case args of
    [] -> calculateSPDXLicenses facts
    _  -> calculateLicenses (V.fromList args) facts
  writeLicenseJSONs outputFolder licenses
  writePandocs outputFolder licenses

  -- echo some stats
  writeStats outputFolder facts licenses
