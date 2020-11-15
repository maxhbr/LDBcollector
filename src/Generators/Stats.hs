{-# LANGUAGE OverloadedStrings #-}
module Generators.Stats
    ( writeStats
    ) where

import qualified Prelude as P
import           MyPrelude

import           Control.Monad
import qualified Data.Map as M
import qualified Data.Vector as V
import           GHC.IO.Encoding
import           System.Environment
import           System.IO

import           Model.License
import           Generators.FindClusters

writeStatsOnFacts :: Handle -> [LicenseFact] -> IO ()
writeStatsOnFacts handle fs = let
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

writeStatsOnLicenses :: Handle -> FilePath -> [(LicenseName, (License, a))] -> IO ()
writeStatsOnLicenses handle statsFolder lics = do
  hPutStrLn handle ("Number of Licenses: " ++ show (length lics))
  let fsOfLics = concatMap (\(_,(License fs, _)) ->  V.toList fs) lics
  writeStatsOnFacts handle fsOfLics
  hPutStrLn handle "#### based on facts from licenses"
  writeClusters handle (statsFolder </> "clusters_from_fatcs_from_lics.csv") (V.fromList fsOfLics)
  hPutStrLn handle "#### based on licenses"
  writeClustersFromLicenses handle (statsFolder </> "clusters_from_lics.csv") lics

writeStats :: FilePath -> Facts -> [(LicenseName, (License, a))] -> IO ()
writeStats outputFolder fs lics = do
  let statsFolder = outputFolder </> "_stats"
  createDirectoryIfNotExists statsFolder

  handle <- openFile (statsFolder </> "stats.txt") WriteMode
  hPutStrLn handle "## Stats:"
  hPutStrLn handle "### Stats on Facts:"
  writeStatsOnFacts handle (V.toList fs)
  writeClusters handle (statsFolder </> "clusters_from_all_facts.csv") fs
  hPutStrLn handle "### Stats on Licenses:"
  writeStatsOnLicenses handle statsFolder lics
  hClose handle

