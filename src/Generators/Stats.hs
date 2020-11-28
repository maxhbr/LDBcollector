{-# LANGUAGE OverloadedStrings #-}
module Generators.Stats
    ( writeStats
    ) where

import qualified Prelude as P
import           MyPrelude

import qualified Data.ByteString.Lazy as BL
import           Control.Monad
import qualified Data.Csv as C
import qualified Data.Map as M
import qualified Data.Vector as V
import           GHC.IO.Encoding
import           System.Environment
import           System.IO
-- -
-- -import qualified Data.ByteString
-- -import qualified Data.Csv as C
-- -import           Data.Set (Set)
-- -import qualified Data.Set as S
-- -import           Data.Map (Map)
-- -import qualified Data.Map as M
-- -import qualified Data.Vector as V


import           Model.License
import           Generators.FindClusters

{- #############################################################################
   ## stas on facts ############################################################
   ########################################################################## -}

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

{- #############################################################################
   ## stas on licenses #########################################################
   ########################################################################## -}

writeStatsOnLicenses :: Handle -> FilePath -> [(LicenseName, (License, a))] -> IO ()
writeStatsOnLicenses handle statsFolder lics = do
  hPutStrLn handle ("Number of Licenses: " ++ show (length lics))
  let fsOfLics = concatMap (\(_,(License fs, _)) ->  V.toList fs) lics
  writeStatsOnFacts handle fsOfLics
  hPutStrLn handle "#### based on facts from licenses"
  writeClusters handle (statsFolder </> "clusters_from_fatcs_from_lics.csv") (V.fromList fsOfLics)
  hPutStrLn handle "#### based on licenses"
  writeClustersFromLicenses handle (statsFolder </> "clusters_from_lics.csv") lics

{- #############################################################################
   ## stas on gaps #############################################################
   ########################################################################## -}
  
data FactRepresentation
  = FactRep LicenseFact
unRep :: FactRepresentation -> LicenseFact
unRep (FactRep f) = f
instance Eq FactRepresentation where
  (FactRep f1) == (FactRep f2) = and [ getLicenseFactClassifier f1 == getLicenseFactClassifier f2
                                     , getImpliedNonambiguousNames f1 == getImpliedNonambiguousNames f2
                                     ]
instance C.ToNamedRecord FactRepresentation where
  toNamedRecord (FactRep f) =
    C.namedRecord [ "lfc" C..= show (getLicenseFactClassifier f)
                  , "names" C..= show (getImpliedNonambiguousNames f)
                  , "ambiguousNames"  C..= show (getImpliedAmbiguousNames f)
                  ]
instance C.DefaultOrdered FactRepresentation where
  headerOrder _ = V.fromList ["lfc", "names", "ambiguousNames"]
hasNames :: FactRepresentation -> Bool
hasNames (FactRep f) = let
    hasNoNameButSC :: [LicenseName] -> Bool
    hasNoNameButSC []   = True
    hasNoNameButSC [ln] = any (`isPrefixOf` ln) ["scancode://", "The License of ", "The License by "]
    hasNoNameButSC _    = False
    in not (hasNoNameButSC (getImpliedNonambiguousNames f) && getImpliedAmbiguousNames f == NoCLSR)

writeStatsOnGaps :: Handle -> FilePath -> Facts -> [(LicenseName, (License, a))] -> IO ()
writeStatsOnGaps handle statsFolder facts licenses = let
    factRefs = V.map FactRep facts
    factRefsFromLicenses = (V.map FactRep . V.concat .  map (\(_, (License fs, _)) -> fs)) licenses
    leftoverFactRefs = V.toList $ V.filter (\f -> not (f `V.elem` factRefsFromLicenses)) factRefs
    leftoverFactRefsWithNames = filter hasNames leftoverFactRefs
  in do
  writeStatsOnFacts handle (map unRep leftoverFactRefs)

  BL.writeFile (statsFolder </> "gaps.csv") (C.encodeDefaultOrderedByName leftoverFactRefsWithNames)

{- #############################################################################
   ## general ##################################################################
   ########################################################################## -}

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
  hPutStrLn handle "### Stats on Gaps:"
  writeStatsOnGaps handle statsFolder fs lics
  hClose handle

