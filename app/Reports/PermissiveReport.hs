{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE OverloadedStrings #-}
module Reports.PermissiveReport
  ( mkPermissiveReport
  ) where

import           GHC.Generics
import           Data.Csv as C
import           Data.Text (Text)
import           Data.Aeson
import qualified Data.Text as T
import qualified Data.Vector as V
import           Data.Maybe
import qualified Data.ByteString.Lazy as B
import           Data.ByteString.Lazy (ByteString)
import qualified Data.ByteString.Lazy.Char8 as Char8
import           Debug.Trace (trace)

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
getFromOSI l = let
    keywords = queryLicense ("OpenSourceInitiative", "OSILicense") (key "keywords" . _Array) l
    osiToString True = "permissive"
    osiToString False = "non-permissive"
  in case keywords of
    Just ks -> Just . osiToString $ "permissive" `V.elem` (V.map (\case
                                                                     String  t -> t
                                                                     _         -> "") ks)
    Nothing -> Nothing


data PRRow
  = PRRow
  { spdxId :: LicenseName
  , scancode :: Maybe Text
  , blueOak :: Maybe Text
  , ocpt :: Maybe Text
  , osi :: Maybe String
  } deriving (Show, Generic)
instance ToNamedRecord PRRow

convertToRow :: (LicenseName, License) -> PRRow
convertToRow (sid, l) = PRRow sid
                              (getFromScancode l)
                              (getFromBlueOak l)
                              (getFromOCPT l)
                              (getFromOSI l)

mkPermissiveReport :: [(LicenseName, License)] -> ByteString
mkPermissiveReport input = C.encodeByName (V.fromList ["spdxId","scancode","blueOak","ocpt","osi"]) (map convertToRow input)
