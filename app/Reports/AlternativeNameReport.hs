{-# LANGUAGE DeriveGeneric #-}
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
  { shortname :: LicenseShortname
  , alternativeNames :: [String]
  } deriving (Show, Generic)
instance ToRecord ANRRow where
  toRecord (ANRRow shortname' alternativeNames') = let
      str = "[" ++ (intercalate "," (nub alternativeNames')) ++ "]"
    in record [toField shortname', toField str]

convertToRow :: (LicenseShortname, License) -> ANRRow
convertToRow (sid, (License fs)) = ANRRow sid (concatMap getImpliedShortnames (V.toList fs))

mkAlternativeNameReport :: [(LicenseShortname, License)] -> ByteString
mkAlternativeNameReport input = C.encode (map convertToRow input)
