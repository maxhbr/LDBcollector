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

initialLicenseMapping :: Map LicenseName [LicenseName]
initialLicenseMapping = M.fromList
  [ ("GPL-1.0-only", ["GPL-1.0", "GPL1.0", "GPL1"])
  , ("GPL-2.0-only", ["GPL-2.0", "GPL2.0", "GPL2", "GPL (v2)"])
  , ("GPL-3.0-only", ["GPL-3.0", "GPL3.0", "GPL3", "GPL (v3)"])
  , ("LGPL-2.1-only", ["LGPL-2.1", "LGPL2.1", "LGPL2.1", "LGPL (v2.1)"])
  , ("LGPL-3.0-only", ["LGPL-3.0", "LGPL-3", "LGPL3.0", "LGPL3", "LGPL (v3.0)", "LGPL (v3)"])
  , ("AGPL-3.0-only", ["AGPL-3.0", "AGPL3.0", "AGPL3", "AGPL (v3)"])
  , ("GPL-1.0-or-later", ["GPL-1.0+", "GPL1.0+", "GPL1+"])
  , ("GPL-2.0-or-later", ["GPL-2.0+", "GPL2.0+", "GPL2+", "GPL (v2 or later)"])
  , ("GPL-3.0-or-later", ["GPL-3.0+", "GPL3.0+", "GPL3+", "GPL (v3 or later)"])
  , ("LGPL-2.1-or-later", ["LGPL-2.1+", "LGPL2.1+", "LGPL2.1+", "LGPL (v2.1 or later)"])
  , ("LGPL-3.0-or-later", ["LGPL-3.0+", "LGPL-3+", "LGPL3.0+", "LGPL3", "LGPL (v3.0)", "LGPL (v3 or later)"])
  , ("AGPL-3.0-or-later", ["AGPL-3.0+", "AGPL3.0+", "AGPL3+", "AGPL (v3 or later)"])
  , ("BSL-1.0", ["BSL (v1.0)"])
  , ("Zlib", ["zlib/libpng"])
  , ("Apache-1.0", ["Apache (v1.0)", "Apache Software License 1.0", "ASL 1.0"])
  , ("Apache-1.1", ["Apache (v1.1)", "Apache Software License 1.1", "ASL 1.1"])
  , ("Apache-2.0", ["Apache (v2.0)", "Apache Software License 2.0", "ASL 2.0"])
  , ("BSL-1.0", ["BSL (v1)"])
  , ("BSD-2-Clause", ["BSD (2 clause)"])
  , ("BSD-3-Clause", ["BSD (3 clause)"])
  , ("MIT", ["MIT license (also X11)"])
  , ("Sleepycat", ["Berkeley Database License", "Sleepycat Software Product License"])
  ]

echoStatsOnFacts :: [LicenseFact] -> IO ()
echoStatsOnFacts = let
    counts :: [LicenseFactClassifier] -> Map LicenseFactClassifier Int
    counts = let
        countsFun :: Map LicenseFactClassifier Int -> LicenseFactClassifier -> Map LicenseFactClassifier Int
        countsFun m lfc = M.insertWith (+) lfc 1 m
      in foldl' countsFun M.empty
  in mapM_ print . M.assocs . counts . map getLicenseFactClassifier

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

  -- calculate licenses
  licenses <- case args of
    [] -> calculateSPDXLicenses initialLicenseMapping facts
    _  -> calculateLicenses initialLicenseMapping (V.fromList args) facts

  -- write output
  outputFolder <- cleanupAndMakeOutputFolder
  writeLicenseJSONs outputFolder licenses
  writeMarkdowns outputFolder licenses

  -- echo some stats
  echoStats facts licenses
