{-# LANGUAGE ExistentialQuantification #-}
{-# LANGUAGE TypeFamilies #-}
{-# LANGUAGE GADTs #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE DeriveGeneric #-}
module Model.Fact
  ( module X
  , LFRaw (..), getImplicationJSONFromLFRaw
  , LicenseFact (..), extractLicenseFactClassifier
  , Facts
  ) where

import qualified Prelude as P
import           MyPrelude

import qualified Data.Map as M

import Model.Statement as X
import Model.LicenseProperties as X

class (Show a, ToJSON a) => LFRaw a where
  getLicenseFactClassifier :: a -> LicenseFactClassifier
  mkSLSR :: (Show b, ToJSON b) => a -> b -> ScopedLicenseStatementResult b
  mkSLSR a = SLSR (getLicenseFactClassifier a)
  -- Statements:
  getImpliedNames :: a -> CollectedLicenseStatementResult LicenseName
  getImpliedFullName :: a -> RankedLicenseStatementResult LicenseName
  getImpliedFullName _ = getEmptyLicenseStatement
  getImpliedId :: a -> RankedLicenseStatementResult LicenseName
  getImpliedId _ = getEmptyLicenseStatement
  getImpliedURLs :: a -> CollectedLicenseStatementResult (Maybe String, URL)
  getImpliedURLs _ = getEmptyLicenseStatement
  getImpliedText :: a -> RankedLicenseStatementResult Text
  getImpliedText _ = getEmptyLicenseStatement
  getImpliedDescription :: a -> RankedLicenseStatementResult String
  getImpliedDescription _ = getEmptyLicenseStatement
  getImpliedJudgement :: a -> ScopedLicenseStatementResult Judgement
  getImpliedJudgement _ = getEmptyLicenseStatement
  getImpliedCopyleft :: a -> ScopedLicenseStatementResult CopyleftKind
  getImpliedCopyleft _ = getEmptyLicenseStatement
  getCalculatedCopyleft :: a -> Maybe CopyleftKind
  getCalculatedCopyleft = let
      fun :: Maybe CopyleftKind -> Maybe CopyleftKind -> Maybe CopyleftKind
      fun Nothing o = o
      fun o Nothing = o
      fun (Just k1) (Just k2) = Just (pessimisticMergeCopyleft k1 k2)
    in foldl' fun Nothing . map Just . M.elems . unpackSLSR . getImpliedCopyleft
  getImpliedObligations :: a -> RankedLicenseStatementResult LicenseObligations
  getImpliedObligations _ = getEmptyLicenseStatement
  getImpliedRatingState :: a -> ScopedLicenseStatementResult RatingState
  getImpliedRatingState _ = getEmptyLicenseStatement

getImplicationJSONFromLFRaw :: (LFRaw a) => a -> Value
getImplicationJSONFromLFRaw a = let
    impliedNames = case getImpliedNames a of
      NoCLSR -> []
      ins    -> [ "__impliedNames" .= ins ]
    impliedId = case getImpliedId a of
      NoRLSR -> []
      iid    -> [ "__impliedId" .= iid ]
    impliedURLs = case getImpliedURLs a of
      NoCLSR -> []
      iurls  -> [ "__impliedURLs" .= iurls ]
    impliedText = case getImpliedText a of
      NoRLSR -> []
      itext  -> [ "__impliedText" .= itext ]
    impliedJudgement = case getImpliedJudgement a of
      NoSLSR -> []
      ijudge -> [ "__impliedJudgement" .= ijudge ]
    copyleft = let
        iCopyleft = getImpliedCopyleft a
      in case getCalculatedCopyleft a of
        Nothing        -> []
        Just cCopyleft -> [ "__calculatedCopyleft" .= cCopyleft
                          , "__impliedCopyleft" .= iCopyleft ]
    obligationsJ = case unpackRLSR (getImpliedObligations a) of
      Just os -> object [ "__obligations" .= toJSON os ]
      Nothing -> object []
    ratingState = case getImpliedRatingState a of
      NoSLSR -> []
      iRatingState -> [ "__impliedRatingState" .= iRatingState ]
  in mergeAesonL [ object $ impliedNames ++ impliedId ++ impliedURLs ++ impliedText ++ impliedJudgement ++ copyleft ++ ratingState
                 , obligationsJ ]

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
                                         , object [ "_implications" .= getImplicationJSONFromLFRaw a ]]]
  toJSON (LicenseFact Nothing a) = let
      lfc = getLicenseFactClassifier a
    in object [ tShow lfc .= mergeAesonL [ toJSON a
                                         , object [ "implications" .= getImplicationJSONFromLFRaw a ]]]
instance LFRaw LicenseFact where
  getLicenseFactClassifier (LicenseFact url raw) = maybeAddUrl url $ getLicenseFactClassifier raw
  getImpliedNames (LicenseFact _ raw)            = getImpliedNames raw
  getImpliedFullName (LicenseFact _ raw)         = getImpliedFullName raw
  getImpliedId (LicenseFact _ raw)               = getImpliedId raw
  getImpliedURLs (LicenseFact _ raw)             = getImpliedURLs raw
  getImpliedText (LicenseFact _ raw)             = getImpliedText raw
  getImpliedDescription (LicenseFact _ raw)      = getImpliedDescription raw
  getImpliedJudgement lf@(LicenseFact _ raw)     = maybeUpdateClassifierInSLSR (getLicenseFactClassifier lf) $ getImpliedJudgement raw
  getImpliedCopyleft (LicenseFact _ raw)         = getImpliedCopyleft raw
  getImpliedObligations (LicenseFact _ raw)      = getImpliedObligations raw
  getImpliedRatingState (LicenseFact _ raw)      = getImpliedRatingState raw


type Facts
  = Vector LicenseFact
