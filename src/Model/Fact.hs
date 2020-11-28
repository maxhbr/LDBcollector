{-# LANGUAGE ExistentialQuantification #-}
{-# LANGUAGE TypeFamilies #-}
{-# LANGUAGE GADTs #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE DeriveGeneric #-}
module Model.Fact
  ( module X
  , LicenseFactVersion (..)
  , LFRaw (..), getImplicationJSONFromLFRaw
  , LicenseFact (..)
  , Facts
  ) where

import qualified Prelude as P
import           MyPrelude

import qualified Data.Map as M
import qualified Data.Maybe (maybeToList)
import qualified Data.List (nub)

import Model.Statement as X
import Model.LicenseProperties as X

data LicenseFactVersion
  = EmptyLFCVersion
  | LFVersion String
  deriving (Generic)

class (Show a, ToJSON a, LicenseFactClassifiable a) => LFRaw a where
  getLicenseFactVersion :: a -> LicenseFactVersion
  getLicenseFactVersion _ = EmptyLFCVersion
  mkSLSR :: (Show b, ToJSON b) => a -> b -> ScopedLicenseStatementResult b
  mkSLSR a = SLSR (getLicenseFactClassifier a)
  mkRLSR :: (Show b, ToJSON b) => a -> Rank -> b -> RankedLicenseStatementResult b
  mkRLSR a = RLSR (getLicenseFactClassifier a)
  -- Statements:
  getImpliedNames :: a -> CollectedLicenseStatementResult LicenseName
  getImpliedFullName :: a -> RankedLicenseStatementResult LicenseName
  getImpliedFullName _ = getEmptyLicenseStatement
  getImpliedId :: a -> RankedLicenseStatementResult LicenseName
  getImpliedId _ = getEmptyLicenseStatement
  getImpliedNonambiguousNames :: a -> [LicenseName]
  getImpliedNonambiguousNames a = let
    names           = unpackCLSR $ getImpliedNames a
    impliedId      = maybeToList . unpackRLSR $ getImpliedId a
    impliedFullName = maybeToList . unpackRLSR $ getImpliedFullName a
    in nub $ impliedId ++ names ++ impliedFullName
  getImpliedAmbiguousNames :: a -> CollectedLicenseStatementResult LicenseName
  getImpliedAmbiguousNames _ = getEmptyLicenseStatement
  getAllImpliedNames :: a -> [LicenseName]
  getAllImpliedNames a = let
    ambiguousNames  = unpackCLSR $ getImpliedAmbiguousNames a
    in nub $ getImpliedNonambiguousNames a ++ ambiguousNames
  getImpliedURLs :: a -> CollectedLicenseStatementResult (Maybe String, URL)
  getImpliedURLs _ = getEmptyLicenseStatement
  getImpliedText :: a -> RankedLicenseStatementResult Text
  getImpliedText _ = getEmptyLicenseStatement
  getImpliedDescription :: a -> RankedLicenseStatementResult String
  getImpliedDescription _ = getEmptyLicenseStatement
  getImpliedJudgement :: a -> ScopedLicenseStatementResult Judgement
  getImpliedJudgement _ = getEmptyLicenseStatement
  getImpliedComments :: a -> ScopedLicenseStatementResult [String]
  getImpliedComments _ = getEmptyLicenseStatement
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
  getImpliedCompatibilities :: a -> ScopedLicenseStatementResult LicenseCompatibility
  getImpliedCompatibilities _ = getEmptyLicenseStatement
  getImpliedIsOSIApproved :: a -> RankedLicenseStatementResult Bool
  getImpliedIsOSIApproved _ = getEmptyLicenseStatement
  getImpliedIsFSFFree :: a -> RankedLicenseStatementResult Bool
  getImpliedIsFSFFree _ = getEmptyLicenseStatement

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
    impliedComments = case getImpliedComments a of
      NoSLSR -> []
      icomments -> [ "__impliedComments" .= icomments ]
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
    impliedCompatibilities = case getImpliedCompatibilities a of
      NoSLSR -> []
      ics    -> [ "__impliedCompatibilities" .= ics ]
    impliedIsOSIApproved = case unpackRLSR (getImpliedIsOSIApproved a) of
      Just ioa -> [ "__isOsiApproved" .= ioa ]
      Nothing  -> []
    impliedIsFSFFree = case unpackRLSR (getImpliedIsFSFFree a) of
      Just iff -> [ "__isFsfFree" .= iff ]
      Nothing  -> []
  in mergeAesonL [ object $
                   impliedNames
                   ++ impliedAmbiguousNames
                   ++ impliedId
                   ++ impliedURLs
                   ++ impliedText
                   ++ impliedJudgement
                   ++ impliedComments
                   ++ copyleft
                   ++ ratingState
                   ++ patentHint
                   ++ impliedNonCommercial
                   ++ impliedCompatibilities
                   ++ impliedIsOSIApproved
                   ++ impliedIsFSFFree
                 , obligationsJ ]

data LicenseFact
  = forall a. (LFRaw a)
  => LicenseFact (Maybe URL) a

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
instance LicenseFactClassifiable LicenseFact where
  getLicenseFactClassifier (LicenseFact url raw)   = maybeAddUrl url $ getLicenseFactClassifier raw
instance LFRaw LicenseFact where
  getLicenseFactVersion (LicenseFact _ raw)        = getLicenseFactVersion raw
  getImpliedNames (LicenseFact _ raw)              =                                                             getImpliedNames raw
  getImpliedAmbiguousNames (LicenseFact _ raw)     =                                                             getImpliedAmbiguousNames raw
  getImpliedFullName lf@(LicenseFact _ raw)        = maybeUpdateClassifierInRLSR (getLicenseFactClassifier lf) $ getImpliedFullName raw
  getImpliedId lf@(LicenseFact _ raw)              = maybeUpdateClassifierInRLSR (getLicenseFactClassifier lf) $ getImpliedId raw
  getImpliedURLs (LicenseFact _ raw)               =                                                             getImpliedURLs raw
  getImpliedText lf@(LicenseFact _ raw)            = maybeUpdateClassifierInRLSR (getLicenseFactClassifier lf) $ getImpliedText raw
  getImpliedDescription (LicenseFact _ raw)        =                                                             getImpliedDescription raw
  getImpliedJudgement lf@(LicenseFact _ raw)       = maybeUpdateClassifierInSLSR (getLicenseFactClassifier lf) $ getImpliedJudgement raw
  getImpliedComments lf@(LicenseFact _ raw)        = maybeUpdateClassifierInSLSR (getLicenseFactClassifier lf) $ getImpliedComments raw
  getImpliedCopyleft (LicenseFact _ raw)           =                                                             getImpliedCopyleft raw
  getImpliedObligations lf@(LicenseFact _ raw)     = maybeUpdateClassifierInRLSR (getLicenseFactClassifier lf) $ getImpliedObligations raw
  getImpliedRatingState (LicenseFact _ raw)        =                                                             getImpliedRatingState raw
  getHasPatentnHint lf@(LicenseFact _ raw)         = maybeUpdateClassifierInRLSR (getLicenseFactClassifier lf) $ getHasPatentnHint raw
  getImpliedNonCommercial lf@(LicenseFact _ raw)   = maybeUpdateClassifierInRLSR (getLicenseFactClassifier lf) $ getImpliedNonCommercial raw
  getImpliedCompatibilities lf@(LicenseFact _ raw) = maybeUpdateClassifierInSLSR (getLicenseFactClassifier lf) $ getImpliedCompatibilities raw
  getImpliedIsOSIApproved (LicenseFact _ raw)      =                                                             getImpliedIsOSIApproved raw
  getImpliedIsFSFFree (LicenseFact _ raw)          =                                                             getImpliedIsFSFFree raw


type Facts
  = Vector LicenseFact
