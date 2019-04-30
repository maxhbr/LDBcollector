{-# LANGUAGE ExistentialQuantification #-}
{-# LANGUAGE TypeFamilies #-}
{-# LANGUAGE GADTs #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE DeriveGeneric #-}
module Model.License
  ( module X
  , LicenseShortnameFactRaw (..), mkLicenseShortnameFact
  , LicenseFullnameFactRaw (..), mkLicenseFullnameFact
  , LicenseTextFactRaw (..), mkLicenseTextFact
  , getLicenseFromFacts
  , containsFactOfType
  , getFactData
  , License (..)
  , Licenses
  ) where

import           Data.List (intersect)
import qualified Data.Text as T
import           Data.Text (Text)
import           Data.Char (toUpper)
import qualified Data.Vector as V
import           Data.Vector (Vector)
import           Text.JSON
import           Data.Aeson
import           GHC.Generics
import qualified Data.ByteString.Lazy as B
import           Data.ByteString.Lazy (ByteString)
import qualified Data.ByteString.Lazy.Char8 as Char8
import           Debug.Trace (trace)
import qualified Data.HashMap.Lazy as HML

import Model.Fact as X

newtype License
  = License Facts
  deriving Generic
type Licenses
  = [License]

instance ToJSON License where
  toJSON (License fs) = let
      -- copied from: https://stackoverflow.com/a/44409320
      -- answered by: Willem Van Onsem
      -- cc-by-sa 3.0
      mergeAeson :: ToJSON a => V.Vector a -> Value
      mergeAeson = Object . HML.unions . map (\(Object x) -> x) . V.toList . V.map toJSON
    in mergeAeson fs
instance Show License where
  show (License fs) = "\n" ++ unlines (map show (V.toList fs)) ++ "\n"

--------------------------------------------------------------------------------
-- first basic facts
data LicenseShortnameFactRaw =
  LicenseShortnameFactRaw LicenseShortname [LicenseShortname]
  deriving (Show, Generic)
instance ToJSON LicenseShortnameFactRaw
instance LFRaw LicenseShortnameFactRaw where
  getImpliedShortnames (LicenseShortnameFactRaw s os) = s : os
  getType              _                              = "LicenseShortname"

mkLicenseShortnameFact :: LicenseShortname -> [LicenseShortname] -> LicenseFact
mkLicenseShortnameFact s os = mkLicenseFact defaultLicenseFactScope (LicenseShortnameFactRaw s os)

data LicenseFullnameFactRaw =
  LicenseFullnameFactRaw String String
  deriving (Show, Generic)
instance ToJSON LicenseFullnameFactRaw
instance LFRaw LicenseFullnameFactRaw where
  getImpliedShortnames (LicenseFullnameFactRaw s _) = [s]
  getType              _                            = "LicenseFullname"

mkLicenseFullnameFact :: String -> String -> LicenseFact
mkLicenseFullnameFact s f = mkLicenseFact defaultLicenseFactScope (LicenseFullnameFactRaw s f)

data LicenseTextFactRaw =
  LicenseTextFactRaw String Text
  deriving (Show, Generic)
instance ToJSON LicenseTextFactRaw
instance LFRaw LicenseTextFactRaw where
  getImpliedShortnames (LicenseTextFactRaw s _) = [s]
  getType              _                        = "LicenseText"

mkLicenseTextFact :: String -> Text -> LicenseFact
mkLicenseTextFact s t = mkLicenseFact defaultLicenseFactScope (LicenseTextFactRaw s t)

--------------------------------------------------------------------------------
-- get license from facts
getLicenseFromFacts :: LicenseShortname -> [LicenseShortname] -> Facts -> License
getLicenseFromFacts shortname otherShortnames fs = let
    allShortnames = map (map toUpper) $ shortname : otherShortnames
    shortnamefilter f = let
        impliedShortnames = map (map toUpper) $ getImpliedShortnames f
      in not (null (allShortnames `intersect` impliedShortnames))
  in License $ mkLicenseShortnameFact shortname otherShortnames `V.cons` V.filter shortnamefilter fs

containsFactOfType :: License -> String -> Bool
containsFactOfType (License fs) t = (\f -> getType f == t) `any` fs

getFactData :: License -> LicenseFactClassifier -> LFData
getFactData (License fs) classifier = case V.find (\f -> _licenseFactClassifier f == classifier) fs of
  Just a  -> getParsedData a
  Nothing -> LFnone
