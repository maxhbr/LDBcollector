{-# LANGUAGE DeriveGeneric #-}
module Reports.PermissiveReport
  ( mkPermissiveReport
  ) where

import           GHC.Generics
import           Data.Csv as C
import qualified Data.ByteString.Lazy as B
import           Data.ByteString.Lazy (ByteString)
import qualified Data.ByteString.Lazy.Char8 as Char8

import Lib

data PRRow
  = PRRow
  { spdxId :: LicenseShortname
  } deriving (Show, Generic)
instance ToRecord PRRow

convertToRow :: (LicenseShortname, License) -> PRRow
convertToRow (sid, l) = PRRow sid

mkPermissiveReport :: [(LicenseShortname, License)] -> ByteString
mkPermissiveReport input = C.encode (map convertToRow input)
