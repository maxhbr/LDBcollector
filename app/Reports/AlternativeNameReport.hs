{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE OverloadedStrings #-}
module Reports.AlternativeNameReport
  ( mkAlternativeNameReport
  ) where

import           GHC.Generics
import           Data.Csv as C
import           Data.List (intercalate,nub)
import qualified Data.Vector as V
import           Data.Vector (Vector)
import qualified Data.ByteString.Lazy as B
import           Data.ByteString.Lazy (ByteString)
import qualified Data.ByteString.Lazy.Char8 as Char8

import Lib

data ANRRow
  = ANRRow
  { shortname :: LicenseName
  , alternativeNames :: [String]
  } deriving (Show, Generic)
instance ToNamedRecord ANRRow where
  toNamedRecord (ANRRow shortname' alternativeNames') = let
      str = "[" ++ (intercalate "," (nub alternativeNames')) ++ "]"
    in namedRecord ["shortname" C..= shortname', "other names" C..= str]

convertToRow :: (LicenseName, License) -> ANRRow
convertToRow (sid, (License fs)) = ANRRow sid (concatMap getImpliedNames (V.toList fs))

mkAlternativeNameReport :: [(LicenseName, License)] -> ByteString
mkAlternativeNameReport input = C.encodeByName (V.fromList ["shortname", "other names"]) (map convertToRow input)
