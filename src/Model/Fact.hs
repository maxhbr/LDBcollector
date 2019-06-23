{-# LANGUAGE ExistentialQuantification #-}
{-# LANGUAGE TypeFamilies #-}
{-# LANGUAGE GADTs #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE DeriveGeneric #-}
module Model.Fact
  ( module X
  , LicenseName
  , LFRaw (..), getImplicationJSONFromLFRaw
  , URL, LicenseFact (..), extractLicenseFactClassifier
  , Facts
  , Judgement (..)
  ) where

import qualified Prelude as P
import           MyPrelude

import qualified Data.Text as T
import qualified Data.Vector as V

import Model.Statement as X

data Judgement
  = PositiveJudgement String
  | NegativeJudgement String
  | NeutralJudgement String
  deriving (Eq, Show, Generic)
instance ToJSON Judgement

type LicenseName
  = String

class (Show a, ToJSON a) => LFRaw a where
  getLicenseFactClassifier :: a -> LicenseFactClassifier
  -- Statements:
  getImpliedNames :: a -> CollectedLicenseStatementResult LicenseName
  getImpliedNames _ = NoCLSR
  getImpliedId :: a -> RankedLicenseStatementResult LicenseName
  getImpliedId _ = NoRLSR
  getImpliedURLs :: a -> CollectedLicenseStatementResult (String, URL)
  getImpliedURLs _ = NoCLSR
  getImpliedText :: a -> RankedLicenseStatementResult Text
  getImpliedText _ = NoRLSR
  getImpliedJudgement :: a -> ScopedLicenseStatementResult Judgement
  getImpliedJudgement _ = NoSLSR

getImplicationJSONFromLFRaw :: (LFRaw a) => a -> Value
getImplicationJSONFromLFRaw a = let
    impliedNames = case getImpliedNames a of
      NoCLSR -> []
      ins    -> [ "impliedNames" .= ins ]
    impliedId = case getImpliedId a of
      NoRLSR -> []
      iid    -> [ "impliedId" .= iid ]
    impliedURLs = case getImpliedURLs a of
      NoCLSR -> []
      iurls  -> [ "impliedURLs" .= iurls ]
    impliedText = case getImpliedText a of
      NoRLSR -> []
      itext  -> [ "impliedText" .= itext ]
    impliedJudgement = case getImpliedJudgement a of
      NoSLSR -> []
      ijudge -> [ "impliedJudgement" .= ijudge ]
  in object $ impliedNames ++ impliedId ++ impliedURLs ++ impliedText ++ impliedJudgement

type URL
  = String
data LicenseFact
  = forall a. (LFRaw a)
  => LicenseFact (Maybe URL) a
extractLicenseFactClassifier :: LicenseFact -> LicenseFactClassifier
extractLicenseFactClassifier (LicenseFact _ a)         = getLicenseFactClassifier a

instance Show LicenseFact where
  show (LicenseFact _ a) = show a
instance ToJSON LicenseFact where
  toJSON (LicenseFact (Just url) a) = let
      lfc = getLicenseFactClassifier a
    in object [ tShow lfc .= mergeAesonL [ toJSON a
                                         , object [ "_sourceURL" .= toJSON url ]
                                         , object [ "implications" .= getImplicationJSONFromLFRaw a ]]]
  toJSON (LicenseFact Nothing a) = let
      lfc = getLicenseFactClassifier a
    in object [ tShow lfc .= mergeAesonL [ toJSON a
                                         , object [ "implications" .= getImplicationJSONFromLFRaw a ]]]
instance LFRaw LicenseFact where
  getLicenseFactClassifier (LicenseFact _ raw)         = getLicenseFactClassifier raw
  getImpliedNames (LicenseFact _ raw)                  = getImpliedNames raw

type Facts
  = Vector LicenseFact
