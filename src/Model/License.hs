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
  , License (..)
  , getFactJSON
  , Licenses
  , containsFactOfClass
  ) where

import qualified Prelude as P
import           MyPrelude

import           Data.List (intersect)
import qualified Data.Text as T
import           Data.Char (toUpper)
import qualified Data.Vector as V
import           Data.ByteString.Lazy (ByteString)
import           Data.Typeable
import           Debug.Trace (trace)

import Model.Fact as X

newtype License
  = License Facts
  deriving Generic
type Licenses
  = [License]

instance ToJSON License where
  toJSON l@(License fs) = mergeAesonL [ object [ "facts" .= mergeAeson fs ]
                                      , getImplicationJSONFromLFRaw l ]
instance Show License where
  show (License fs) = "\n" ++ unlines (map show (V.toList fs)) ++ "\n"
instance LicenseFactClassifiable License where
  getLicenseFactClassifier _ = EmptyLFC
instance LFRaw License where
  getImpliedNames (License fs)           = mergeLicenseStatementResultList $ V.map getImpliedNames fs
  getImpliedAmbiguousNames (License fs)  = mergeLicenseStatementResultList $ V.map getImpliedAmbiguousNames fs
  getImpliedFullName (License fs)        = mergeLicenseStatementResultList $ V.map getImpliedFullName fs
  getImpliedId (License fs)              = mergeLicenseStatementResultList $ V.map getImpliedId fs
  getImpliedURLs (License fs)            = mergeLicenseStatementResultList $ V.map getImpliedURLs fs
  getImpliedText (License fs)            = mergeLicenseStatementResultList $ V.map getImpliedText fs
  getImpliedDescription (License fs)     = mergeLicenseStatementResultList $ V.map getImpliedDescription fs
  getImpliedJudgement (License fs)       = mergeLicenseStatementResultList $ V.map getImpliedJudgement fs
  getImpliedComments (License fs)        = mergeLicenseStatementResultList $ V.map getImpliedComments fs
  getImpliedCopyleft (License fs)        = mergeLicenseStatementResultList $ V.map getImpliedCopyleft fs
  getImpliedObligations (License fs)     = mergeLicenseStatementResultList $ V.map getImpliedObligations fs
  getImpliedRatingState (License fs)     = mergeLicenseStatementResultList $ V.map getImpliedRatingState fs
  getHasPatentnHint (License fs)         = mergeLicenseStatementResultList $ V.map getHasPatentnHint fs
  getImpliedNonCommercial (License fs)   = mergeLicenseStatementResultList $ V.map getImpliedNonCommercial fs
  getImpliedCompatibilities (License fs) = mergeLicenseStatementResultList $ V.map getImpliedCompatibilities fs
  getImpliedIsOSIApproved (License fs)   = mergeLicenseStatementResultList $ V.map getImpliedIsOSIApproved fs
  getImpliedIsFSFFree (License fs)       = mergeLicenseStatementResultList $ V.map getImpliedIsFSFFree fs

--------------------------------------------------------------------------------
-- first basic facts
data LicenseShortnameFactRaw =
  LicenseShortnameFactRaw LicenseName [LicenseName]
  deriving (Show, Generic)
instance ToJSON LicenseShortnameFactRaw where
  toJSON (LicenseShortnameFactRaw mainLicenseName otherNames) = object [ "shortname" .= mainLicenseName
                                                                       , "otherNames" .= toJSON otherNames ]
instance LicenseFactClassifiable LicenseShortnameFactRaw where
  getLicenseFactClassifier _ = LFC "LicenseName"
instance LFRaw LicenseShortnameFactRaw where
  getImpliedNames (LicenseShortnameFactRaw s os) = CLSR (s : os)
  getImpliedId f@(LicenseShortnameFactRaw s _)   = mkRLSR f 30 s

mkLicenseShortnameFact :: LicenseName -> [LicenseName] -> LicenseFact
mkLicenseShortnameFact s os = LicenseFact Nothing (LicenseShortnameFactRaw s os)

data LicenseFullnameFactRaw =
  LicenseFullnameFactRaw String String
  deriving (Show, Generic)
instance ToJSON LicenseFullnameFactRaw
instance LicenseFactClassifiable LicenseFullnameFactRaw where
  getLicenseFactClassifier _ = LFC "LicenseFullname"
instance LFRaw LicenseFullnameFactRaw where
  getImpliedId f@(LicenseFullnameFactRaw s _)        = mkRLSR f 50 s
  getImpliedNames (LicenseFullnameFactRaw s fn)      = CLSR [s, fn]
  getImpliedFullName f@(LicenseFullnameFactRaw _ fn) = mkRLSR f 100 fn

mkLicenseFullnameFact :: String -> String -> LicenseFact
mkLicenseFullnameFact s f = LicenseFact Nothing (LicenseFullnameFactRaw s f)

data LicenseTextFactRaw =
  LicenseTextFactRaw String Text
  deriving (Show, Generic)
instance ToJSON LicenseTextFactRaw
instance LicenseFactClassifiable LicenseTextFactRaw where
  getLicenseFactClassifier _ = LFC "LicenseText"
instance LFRaw LicenseTextFactRaw where
  getImpliedNames (LicenseTextFactRaw s _)  = CLSR [s]
  getImpliedText f@(LicenseTextFactRaw _ t) = mkRLSR f 70 t

mkLicenseTextFact :: String -> Text -> LicenseFact
mkLicenseTextFact s t = LicenseFact Nothing (LicenseTextFactRaw s t)

--------------------------------------------------------------------------------
-- get license from facts
getLicenseFromFacts :: LicenseName -> [LicenseName] -> Facts -> License
getLicenseFromFacts shortname otherShortnames fs = let
    allShortnames = map (map toUpper) $ shortname : otherShortnames
    shortnamefilter f = let
        impliedNames = map (map toUpper) $ getImpliedNonambiguousNames f
      in not (null (allShortnames `intersect` impliedNames))
  in License $ mkLicenseShortnameFact shortname otherShortnames `V.cons` V.filter shortnamefilter fs

containsFactOfClass :: License -> LicenseFactClassifier -> Bool
containsFactOfClass (License fs) t = (\f -> getLicenseFactClassifier f == t) `any` fs

getFactJSON :: License -> LicenseFactClassifier -> Maybe ByteString
getFactJSON (License fs) classifier = fmap encode (V.find (\f -> getLicenseFactClassifier f == classifier) fs)

