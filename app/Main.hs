{-# LANGUAGE OverloadedStrings #-}
module Main where

import qualified Prelude as P
import           MyPrelude

import           Control.Monad
import qualified Data.Map as M
import qualified Data.Vector as V
import           GHC.IO.Encoding
import           System.Environment

import Lib
import FindClusters (findClusters, writeClusters)

echoStatsOnFacts :: [LicenseFact] -> IO ()
echoStatsOnFacts = let
    counts :: [LicenseFactClassifier] -> Map LicenseFactClassifier Int
    counts = let
        countsFun :: Map LicenseFactClassifier Int -> LicenseFactClassifier -> Map LicenseFactClassifier Int
        countsFun m lfc = M.insertWith (+) lfc 1 m
      in foldl' countsFun M.empty
  in mapM_ ( putStrLn
             . (\(k,n) -> "    " ++ show k ++ ": " ++ show n))
     . M.assocs
     . counts
     . map getLicenseFactClassifier

echoStatsOnLicenses :: [(LicenseName, License)] -> IO ()
echoStatsOnLicenses lics = do
  putStrLn ("Number of Licenses: " ++ show (length lics))
  echoStatsOnFacts (concatMap (\(_,License fs) ->  V.toList fs) lics)

echoStats :: Facts -> [(LicenseName, License)] -> IO ()
echoStats fs lics = do
  putStrLn "## Stats:"
  putStrLn "### Stats on Facts:"
  echoStatsOnFacts (V.toList fs)
  putStrLn "### Stats on Licenses:"
  echoStatsOnLicenses lics

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
  writeClusters outputFolder facts

  -- calculate licenses
  licenses <- case args of
    [] -> calculateSPDXLicenses facts
    _  -> calculateLicenses (V.fromList args) facts
  writeLicenseJSONs outputFolder licenses
  writePandocs outputFolder licenses

  -- echo some stats
  echoStats facts licenses
