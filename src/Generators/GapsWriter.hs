{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE QuasiQuotes #-}
{-# LANGUAGE TemplateHaskell #-}
module Generators.GapsWriter
  ( writeGaps
  ) where

import qualified Prelude as P
import           MyPrelude

import qualified Data.ByteString
import qualified Data.ByteString.Lazy as BL
import qualified Data.Csv as C
import           Data.Set (Set)
import qualified Data.Set as S
import           Data.Map (Map)
import qualified Data.Map as M
import qualified Data.Vector as V

import           Model.License

data FactRepresentation
  = FactRep LicenseFact
instance Eq FactRepresentation where
  (FactRep f1) == (FactRep f2) = and [ getLicenseFactClassifier f1 == getLicenseFactClassifier f2
                                     , getImpliedNames f1 == getImpliedNames f2
                                     ]
instance C.ToNamedRecord FactRepresentation where
  toNamedRecord (FactRep f) =
    C.namedRecord [ "lfc" C..= show (getLicenseFactClassifier f)
                  , "names" C..= show (getImpliedNames f)
                  , "ambiguousNames"  C..= show (getImpliedAmbiguousNames f)
                  ]
instance C.DefaultOrdered FactRepresentation where
  headerOrder _ = V.fromList ["lfc", "names", "ambiguousNames"]

writeGaps :: FilePath -> Facts -> [(LicenseName, (License, a))] -> IO ()
writeGaps outputFolder facts licenses = let
    gapsFolder = outputFolder </> "_gaps"
    factRefs = (V.map FactRep facts)
    factRefsFromLicenses = (V.map FactRep . V.concat .  map (\(_, (License fs, _)) -> fs)) licenses
    leftoverFactRefs = V.toList $ V.filter (\f -> not (f `V.elem` factRefsFromLicenses)) factRefs
  in do

  hPutStrLn stderr $ "### numOfFacts: " ++ show (V.length facts)
    ++ " numOfLicenseFacs: " ++ show (V.length factRefsFromLicenses)
    ++ " numOfLeftover: " ++ show (length leftoverFactRefs)

  createDirectoryIfNotExists gapsFolder
  BL.writeFile (gapsFolder </> "gaps.csv") (C.encodeDefaultOrderedByName leftoverFactRefs)
  BL.writeFile (gapsFolder </> "all.csv") (C.encodeDefaultOrderedByName (V.toList factRefs))
  BL.writeFile (gapsFolder </> "lic.csv") (C.encodeDefaultOrderedByName (V.toList factRefsFromLicenses))
