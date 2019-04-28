module Main where

import System.IO (hPutStrLn, stderr)
import qualified Data.Vector as V
import           Data.Aeson
import qualified Data.ByteString.Lazy as B
import           Data.ByteString.Lazy (ByteString)
import           System.Directory (createDirectory, removeDirectoryRecursive, doesDirectoryExist)
import           System.FilePath
import           Control.Monad

import Lib

main :: IO ()
main = do
  factsFromSPDX <- loadSPDXFacts "./data/spdx-license-list-data/"
  factsFromBlueOak <- loadBlueOakFacts "./data/Blue_Oak_Council/blue-oak-council-license-list.json"
  factsFromOCPT <- loadOSPTFacts "./data/OpenChainPolicyTemplate/Table.csv"
  factsFromScancode <- loadScancodeFacts "./data/nexB_scancode-toolkit_license_list/"
  let facts = V.concat [factsFromSPDX, factsFromBlueOak, factsFromOCPT, factsFromScancode]

  hPutStrLn stderr "... done with collecting data"

  let ids = concatMap (\(LicenseFact _ a _) -> getImpliedShortnames a) $ V.toList factsFromSPDX

  let outputFolder = "_output/"
  dirExists <- doesDirectoryExist outputFolder
  when dirExists $ do
    removeDirectoryRecursive outputFolder
  createDirectory outputFolder
  hPutStrLn stderr "... done with calculating licenses"
  mapM_ (\i -> do
            let l = getLicenseFromFacts i [] facts
            B.writeFile (outputFolder </> i ++ ".json") (encode l)
        ) ids
