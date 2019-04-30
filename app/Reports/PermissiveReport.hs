{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE OverloadedStrings #-}
module Reports.PermissiveReport
  ( mkPermissiveReport
  ) where

import           GHC.Generics
import           Data.Csv as C
import           Data.Text (Text)
import qualified Data.Text as T
import qualified Data.Vector as V
import           Data.Maybe
import qualified Data.ByteString.Lazy as B
import           Data.ByteString.Lazy (ByteString)
import qualified Data.ByteString.Lazy.Char8 as Char8

import Lib

getFromScancode,getFromBlueOak,getFromOCPT :: License -> Maybe Text
getFromScancode = queryLicense ("Scancode", "ScancodeData") (key "category" . _String)
getFromBlueOak = queryLicense ("BlueOak", "BOEntry") (key "BlueOakRating" . _String)
getFromOCPT l = let
    ocptClassifier = ("OpenChainPolicyTemplate", "OCPTRow")
    ocptType = queryLicense ocptClassifier (key "licenseType" . _String) l
    ocptCopyleft = queryLicense ocptClassifier (key "typeCopyleft" . _String) l
  in case ocptType of
    Just t -> Just $ fromMaybe T.empty ocptCopyleft `T.append` " (" `T.append` t `T.append` ")"
    Nothing -> Nothing


data PRRow
  = PRRow
  { spdxId :: LicenseName
  , scancode :: Maybe Text
  , blueOak :: Maybe Text
  , ocpt :: Maybe Text
  } deriving (Show, Generic)
instance ToNamedRecord PRRow

convertToRow :: (LicenseName, License) -> PRRow
convertToRow (sid, l) = PRRow sid
                              (getFromScancode l)
                              (getFromBlueOak l)
                              (getFromOCPT l)

mkPermissiveReport :: [(LicenseName, License)] -> ByteString
mkPermissiveReport input = C.encodeByName (V.fromList ["spdxId","scancode","blueOak","ocpt"]) (map convertToRow input)
