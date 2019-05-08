{-# LANGUAGE OverloadedStrings #-}
module Main where

import qualified Prelude as P
import           MyPrelude

import qualified Data.Vector as V
import qualified Data.ByteString.Lazy as B
import           Control.Monad
import qualified Data.Map as M
import qualified Data.List as L

import Lib
import Reports.PermissiveReport (mkPermissiveReport)
import Reports.AlternativeNameReport (mkAlternativeNameReport)

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
  ]

getLicensesFromFacts :: Vector LicenseName -> Int -> Map LicenseName [LicenseName] -> Facts -> Vector (LicenseName, License)
getLicensesFromFacts ids 0 mapping facts = V.map (\i -> (i, getLicenseFromFacts i (M.findWithDefault [] i mapping) facts)) ids
getLicensesFromFacts ids i mapping facts = let
    lics = getLicensesFromFacts ids 0 mapping facts
    newMapping = M.fromList . V.toList $ V.map (\(name,License fs) -> (name, L.nub (concatMap getImpliedNames (V.toList fs)))) lics
  in getLicensesFromFacts ids (i - 1) newMapping facts

readFacts :: IO Facts
readFacts = do
  factsFromSPDX <- loadSPDXFacts "./data/spdx-license-list-data/"
  factsFromBlueOak <- loadBlueOakFacts "./data/blue-oak-council-license-list.json"
  factsFromOCPT <- loadOSPTFacts "./data/OpenChainPolicyTemplate/Table.csv"
  factsFromScancode <- loadScancodeFacts "./data/nexB_scancode-toolkit_license_list/"
  factsFromOsadl <- loadOsadlFacts "./data/OSADL/"
  factsFromChooseALicense <- loadChooseALicenseFacts "./data/choosealicense.com/"
  factsFromFedora <- loadFedoraFacts "./data/Fedora_Project_Wiki/"
  factsFromOSI <- loadOSIFacts
  factsFromOSLC <- loadOslcFacts "./data/OSLC-handbook"
  factsFromWikipedia <- loadWikipediaFacts
  let facts = V.concat [ factsFromSPDX
                       , factsFromBlueOak
                       , factsFromOCPT
                       , factsFromScancode
                       , factsFromOsadl
                       , factsFromChooseALicense
                       , factsFromFedora
                       , factsFromOSI
                       , factsFromWikipedia
                       , factsFromOSLC
                       ]
  hPutStrLn stderr "... done with collecting data"
  return facts

calculateLicenses :: (LicenseFact -> Bool) -> Facts -> IO [(LicenseName, License)]
calculateLicenses filterForIds facts = do

  let factsToTakeIDsFrom = V.filter filterForIds facts
      ids = V.map head . V.filter (/= []) . V.map getImpliedNames $ factsToTakeIDsFrom

  let licenses = getLicensesFromFacts ids 1 initialLicenseMapping facts
  hPutStrLn stderr "... done with calculating licenses"

  return $ V.toList licenses

calculateSPDXLicenses :: Facts -> IO [(LicenseName, License)]
calculateSPDXLicenses = calculateLicenses (\f -> getLicenseFactClassifier f == (LFC ["SPDX", "SPDXEntry"]))

cleanupAndMakeOutputFolder :: IO FilePath
cleanupAndMakeOutputFolder = do
  let outputFolder = "_generated/"
  dirExists <- doesDirectoryExist outputFolder
  when dirExists $
    removeDirectoryRecursive outputFolder
  createDirectory outputFolder

  return outputFolder

writeLicenseJSONs :: FilePath -> [(LicenseName, License)] -> IO ()
writeLicenseJSONs outputFolder licenses = do
  jsons <- mapM (\(i,l) -> let
                    outputFile = i ++ ".json"
                in do
                   B.writeFile (outputFolder </> outputFile) (encode l)
                   return outputFile) licenses
  B.writeFile (outputFolder </> "_all.json") (encode licenses)
  B.writeFile (outputFolder </> "_index.json") (encode jsons)

writeReports :: FilePath -> [(LicenseName, License)] -> IO ()
writeReports outputFolder licenses = do
  let reportDirectory = outputFolder </> "reports"
  createDirectory reportDirectory
  B.writeFile (reportDirectory </> "PermissiveReport.csv") (mkPermissiveReport licenses)
  B.writeFile (reportDirectory </> "AlternativeNameReport.csv") (mkAlternativeNameReport licenses)

main :: IO ()
main = do
  facts <- readFacts
  licenses <- calculateSPDXLicenses facts

  outputFolder <- cleanupAndMakeOutputFolder

  writeLicenseJSONs outputFolder licenses
  writeReports outputFolder licenses
