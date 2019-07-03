module FindClusters
  ( findClusters
  , writeClusters
  ) where

import qualified Prelude as P
import           MyPrelude

import           Data.Set (Set)
import qualified Data.Set as S
import qualified Data.Vector as V
import           Data.List
import           Data.Ord

import Lib

findClusters :: Facts -> [Set LicenseName]
findClusters = let
    -- fix :: (a -> a) -> a
    -- fix f = x where x = f x

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
  in sortOn (Down . S.size)
   . filter (\s -> S.size s /= 0)
   . findClusters'
   . nub
   . V.toList
   . V.map S.fromList
   . V.map (\f -> maybeToList (unpackRLSR (getImpliedId f)) ++ unpackCLSR (getImpliedNames f))

writeClusters :: FilePath -> Facts -> IO ()
writeClusters outDir fs = let
    clusters = findClusters fs
    rowToLine :: Set LicenseName -> String
    rowToLine = concat . intersperse ";" . S.elems
  in writeFile (outDir </> "clusters.csv") (unlines (map rowToLine clusters))
