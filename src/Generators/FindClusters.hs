module Generators.FindClusters
  ( findClusters
  , writeClusters
  , writeClustersFromLicenses
  ) where

import qualified Prelude as P
import           MyPrelude

import           Data.Set (Set)
import qualified Data.Set as S
import qualified Data.Vector as V
import           Data.Ord
import           System.IO

import           Model.License

getNamesFromFact f = maybeToList (unpackRLSR (getImpliedId f)) ++ unpackCLSR (getImpliedNames f)

findClusters :: Facts -> [Set LicenseName]
findClusters = let
    findClusters'' :: [Set LicenseName] -> Set LicenseName -> [Set LicenseName]
    findClusters'' [] n = [n]
    findClusters'' (s:ss) n = if S.disjoint s n
                              then s : findClusters'' ss n
                              else (s `S.union` n) : ss
    findClusters' :: [Set LicenseName] -> [Set LicenseName]
    findClusters' old = let
        new = foldl' findClusters'' [] old
      in if new == old
         then new
         else findClusters' new
  in findClusters'
   . nub
   . V.toList
   . V.map S.fromList
   . V.map getNamesFromFact

findClustersFromLicenses :: [(LicenseName, License)] -> [Set LicenseName]
findClustersFromLicenses = map S.fromList . map (\(ln, License fs) -> ln : (concat . V.toList . V.map getNamesFromFact) fs)


-- based on: https://hackage.haskell.org/package/MissingH-1.4.2.1/docs/src/Data.CSV.html#genCsvFile (BSD-3-Clause)
genCsvFile :: Int -> [[String]] -> String
genCsvFile width = let
    makeToWidth :: [String] -> [String]
    makeToWidth ls = ls ++ replicate (width - length ls) ""
    csvline :: [String] -> String
    csvline = intercalate "," . map csvcells
    csvcells :: String -> String
    csvcells "" = ""
    csvcells c = '"' : convcell c ++ "\""
    convcell :: String -> String
    convcell = concatMap convchar
    convchar '"' = "\"\""
    convchar x = [x]
  in unlines . map (csvline . makeToWidth)

writeClusters' :: Handle -> FilePath -> [Set LicenseName] -> IO()
writeClusters' handle outFile clusters = let
    sortedClusters = (map (sortOn length . S.elems) . sortOn (Down . S.size) . filter (\s -> S.size s /= 0)) clusters
    width = length (head sortedClusters)
  in do
    hPutStrLn handle ("Number of clusters: " ++ show (length sortedClusters))
    writeFile outFile (genCsvFile width (replicate width "" : sortedClusters))

writeClusters :: Handle -> FilePath -> Facts -> IO ()
writeClusters handle outFile fs = writeClusters' handle outFile (findClusters fs)

writeClustersFromLicenses :: Handle -> FilePath -> [(LicenseName, License)] -> IO ()
writeClustersFromLicenses handle outFile lics = writeClusters' handle outFile (findClustersFromLicenses lics)
