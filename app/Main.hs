module Main where

import System.IO (hPutStrLn, stderr)
import qualified Data.Vector as V
import           Data.Aeson
import qualified Data.ByteString.Lazy as B
import           Data.ByteString.Lazy (ByteString)
import           System.Directory (createDirectory, removeDirectoryRecursive, doesDirectoryExist)
import           System.FilePath
import           Control.Monad
import qualified Data.Map as M
import           Data.Map (Map)
import qualified Data.List as L

import Lib
import Reports.PermissiveReport (mkPermissiveReport)
import Reports.AlternativeNameReport (mkAlternativeNameReport)

additionalShortnames :: Map LicenseName [LicenseName]
additionalShortnames = M.fromList
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
  , ("Apache-2.0", ["Apache (v2.0)"])
  , ("BSL-1.0", ["BSL (v1)"])
  , ("BSD-2-Clause", ["BSD (2 clause)"])
  , ("BSD-3-Clause", ["BSD (3 clause)"])
  ]

writeLicenseJSONs :: FilePath -> [(LicenseName, License)] -> IO ()
writeLicenseJSONs outputFolder licenses = do
  jsons <- mapM (\(i,l) -> let
                    outputFile = i ++ ".json"
                in do
                   B.writeFile (outputFolder </> outputFile) (encode l)
                   return outputFile) licenses
  B.writeFile (outputFolder </> "_all.json") (encode jsons)

getLicensesFromFacts :: [LicenseName] -> Int -> Map LicenseName [LicenseName] -> Facts -> [(LicenseName, License)]
getLicensesFromFacts ids 0 mapping facts = map (\i -> (i, getLicenseFromFacts i (M.findWithDefault [] i additionalShortnames) facts)) ids
getLicensesFromFacts ids i mapping facts = let
    lics = getLicensesFromFacts ids 0 mapping facts
    newMapping = M.fromList $ map (\(i,License fs) -> (i, (concatMap getImpliedNames (V.toList fs)))) lics
  in getLicensesFromFacts ids (i - 1) newMapping facts


main :: IO ()
main = do
  factsFromSPDX <- loadSPDXFacts "./data/spdx-license-list-data/"
  factsFromBlueOak <- loadBlueOakFacts "./data/Blue_Oak_Council/blue-oak-council-license-list.json"
  factsFromOCPT <- loadOSPTFacts "./data/OpenChainPolicyTemplate/Table.csv"
  factsFromScancode <- loadScancodeFacts "./data/nexB_scancode-toolkit_license_list/"
  factsFromOsadl <- loadOsadlFacts "./data/OSADL/"
  factsFromChooseALicense <- loadChooseALicenseFacts "./data/choosealicense.com/"
  let facts = V.concat [ factsFromSPDX
                       , factsFromBlueOak
                       , factsFromOCPT
                       , factsFromScancode
                       , factsFromOsadl
                       , factsFromChooseALicense
                       ]

  hPutStrLn stderr "... done with collecting data"

  let ids = map head . filter (/= []) . map (\(LicenseFact _ a _) -> getImpliedNames a) $ V.toList factsFromSPDX

  let licenses = getLicensesFromFacts ids 1 additionalShortnames facts
  hPutStrLn stderr "... done with calculating licenses"

  let outputFolder = "_generated/"
  dirExists <- doesDirectoryExist outputFolder
  when dirExists $ do
    removeDirectoryRecursive outputFolder
  createDirectory outputFolder

  writeLicenseJSONs outputFolder licenses
  let reportDirectory = outputFolder </> "reports"
  createDirectory reportDirectory
  B.writeFile (reportDirectory </> "PermissiveReport.csv") (mkPermissiveReport licenses)
  B.writeFile (reportDirectory </> "AlternativeNameReport.csv") (mkAlternativeNameReport licenses)
