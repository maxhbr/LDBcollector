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
  mkRLSR :: (Show b, ToJSON b) => a -> Rank -> b -> RankedLicenseStatementResult b
  mkRLSR a = RLSR (getLicenseFactClassifier a)
  -- Statements:
  getImpliedNames :: a -> CollectedLicenseStatementResult LicenseName
  getImpliedAmbiguousNames :: a -> CollectedLicenseStatementResult LicenseName
  getImpliedAmbiguousNames _ = getEmptyLicenseStatement
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
  getHasPatentnHint :: a -> RankedLicenseStatementResult Bool
  getHasPatentnHint _ = getEmptyLicenseStatement
  getImpliedNonCommercial :: a -> RankedLicenseStatementResult Bool
  getImpliedNonCommercial _ = getEmptyLicenseStatement

getImplicationJSONFromLFRaw :: (LFRaw a) => a -> Value
getImplicationJSONFromLFRaw a = let
    impliedNames = case getImpliedNames a of
      NoCLSR -> []
      ins    -> [ "__impliedNames" .= ins ]
    impliedAmbiguousNames = case getImpliedAmbiguousNames a of
      NoCLSR -> []
      ins    -> [ "__impliedAmbiguousNames" .= ins ]
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
    patentHint = case getHasPatentnHint a of
      NoRLSR -> []
      hPatentHint -> [ "__hasPatentHint" .= hPatentHint ]
    impliedNonCommercial = case getImpliedNonCommercial a of
      NoRLSR -> []
      nc     -> [ "__impliedNonCommercial" .= nc ]
  in mergeAesonL [ object $
                   impliedNames
                   ++ impliedAmbiguousNames
                   ++ impliedId
                   ++ impliedURLs
                   ++ impliedText
                   ++ impliedJudgement
                   ++ copyleft
                   ++ ratingState
                   ++ patentHint
                   ++ impliedNonCommercial
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
  getImpliedNames (LicenseFact _ raw)            =                                                             getImpliedNames raw
  getImpliedAmbiguousNames (LicenseFact _ raw)   =                                                             getImpliedAmbiguousNames raw
  getImpliedFullName lf@(LicenseFact _ raw)      = maybeUpdateClassifierInRLSR (getLicenseFactClassifier lf) $ getImpliedFullName raw
  getImpliedId lf@(LicenseFact _ raw)            = maybeUpdateClassifierInRLSR (getLicenseFactClassifier lf) $ getImpliedId raw
  getImpliedURLs (LicenseFact _ raw)             =                                                             getImpliedURLs raw
  getImpliedText lf@(LicenseFact _ raw)          = maybeUpdateClassifierInRLSR (getLicenseFactClassifier lf) $ getImpliedText raw
  getImpliedDescription (LicenseFact _ raw)      =                                                             getImpliedDescription raw
  getImpliedJudgement lf@(LicenseFact _ raw)     = maybeUpdateClassifierInSLSR (getLicenseFactClassifier lf) $ getImpliedJudgement raw
  getImpliedCopyleft (LicenseFact _ raw)         =                                                             getImpliedCopyleft raw
  getImpliedObligations lf@(LicenseFact _ raw)   = maybeUpdateClassifierInRLSR (getLicenseFactClassifier lf) $ getImpliedObligations raw
  getImpliedRatingState (LicenseFact _ raw)      =                                                             getImpliedRatingState raw
  getHasPatentnHint lf@(LicenseFact _ raw)       = maybeUpdateClassifierInRLSR (getLicenseFactClassifier lf) $ getHasPatentnHint raw
  getImpliedNonCommercial lf@(LicenseFact _ raw) = maybeUpdateClassifierInRLSR (getLicenseFactClassifier lf) $ getImpliedNonCommercial raw


type Facts
  = Vector LicenseFact