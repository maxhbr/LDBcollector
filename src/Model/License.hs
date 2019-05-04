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
  , containsFactOfClass, containsFactOfType
  , getFactJSON, getFactData
  , License (..)
  , Licenses
  ) where

import qualified Prelude as P
import           MyPrelude

import           Data.List (intersect)
import qualified Data.Text as T
import           Data.Char (toUpper)
import qualified Data.Vector as V
import qualified Data.ByteString.Lazy as B
import           Data.ByteString.Lazy (ByteString)
import qualified Data.ByteString.Lazy.Char8 as Char8

import Model.Fact as X
import Model.StatementTypes as X
import Model.Utils
import Model.StatementTypes

newtype License
  = License Facts
  deriving Generic
type Licenses
  = [License]

instance ToJSON License where
  toJSON l@(License fs) = let
      stms = getStatementsFromLicense l
    in object [ "facts" .= mergeAeson fs
              , "statements" .= toJSON stms ]
instance Show License where
  show (License fs) = "\n" ++ unlines (map show (V.toList fs)) ++ "\n"

--------------------------------------------------------------------------------
-- first basic facts
data LicenseShortnameFactRaw =
  LicenseShortnameFactRaw LicenseName [LicenseName]
  deriving (Show, Generic)
instance ToJSON LicenseShortnameFactRaw
instance LFRaw LicenseShortnameFactRaw where
  getLicenseFactClassifier _                         = LFC ["LicenseName"]
  getImpliedNames (LicenseShortnameFactRaw s os)     = s : os
  getImpliedStatements (LicenseShortnameFactRaw s _) = V.singleton $ FactStatement (HasShortname (T.pack s)) Nothing

mkLicenseShortnameFact :: LicenseName -> [LicenseName] -> LicenseFact
mkLicenseShortnameFact s os = LicenseFact (LicenseShortnameFactRaw s os)

data LicenseFullnameFactRaw =
  LicenseFullnameFactRaw String String
  deriving (Show, Generic)
instance ToJSON LicenseFullnameFactRaw
instance LFRaw LicenseFullnameFactRaw where
  getLicenseFactClassifier _                   = LFC ["LicenseFullname"]
  getImpliedNames (LicenseFullnameFactRaw s _) = [s]

mkLicenseFullnameFact :: String -> String -> LicenseFact
mkLicenseFullnameFact s f = LicenseFact (LicenseFullnameFactRaw s f)

data LicenseTextFactRaw =
  LicenseTextFactRaw String Text
  deriving (Show, Generic)
instance ToJSON LicenseTextFactRaw
instance LFRaw LicenseTextFactRaw where
  getLicenseFactClassifier _                         = LFC ["LicenseText"]
  getImpliedNames (LicenseTextFactRaw s _)           = [s]
  getImpliedStatements ltfr@(LicenseTextFactRaw _ t) = V.singleton $ FactStatement (HasLicenseText t) Nothing

mkLicenseTextFact :: String -> Text -> LicenseFact
mkLicenseTextFact s t = LicenseFact (LicenseTextFactRaw s t)

--------------------------------------------------------------------------------
-- get license from facts
getLicenseFromFacts :: LicenseName -> [LicenseName] -> Facts -> License
getLicenseFromFacts shortname otherShortnames fs = let
    allShortnames = map (map toUpper) $ shortname : otherShortnames
    shortnamefilter f = let
        impliedShortnames = map (map toUpper) $ getImpliedNames f
      in not (null (allShortnames `intersect` impliedShortnames))
  in License $ mkLicenseShortnameFact shortname otherShortnames `V.cons` V.filter shortnamefilter fs

containsFactOfClass :: License -> LicenseFactClassifier -> Bool
containsFactOfClass (License fs) t = (\f -> getLicenseFactClassifier f == t) `any` fs
containsFactOfType :: License -> Text -> Bool
containsFactOfType (License fs) t = (\f -> case getLicenseFactClassifier f of
                                        LFC []  -> False
                                        LFC bcs -> last bcs == t) `any` fs

getFactJSON :: License -> LicenseFactClassifier -> Maybe ByteString
getFactJSON (License fs) classifier = fmap encode (V.find (\f -> getLicenseFactClassifier f == classifier) fs)

getFactData :: License -> LicenseFactClassifier -> Value
getFactData (License fs) classifier = case V.find (\f -> getLicenseFactClassifier f == classifier) fs of
  Just a  -> toJSON a
  Nothing -> object []

getStatementsFromLicense :: License -> Vector FactStatement
getStatementsFromLicense (License fs) = V.concatMap computeImpliedStatements fs

