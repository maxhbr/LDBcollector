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
  , CopyleftKind (..), pessimisticMergeCopyleft --, LicenseTaxonomy (..)
  ) where

import qualified Prelude as P
import           MyPrelude

import qualified Data.Text as T
import qualified Data.Vector as V
import qualified Data.Map as M

import Model.Statement as X

data Judgement
  = PositiveJudgement String
  | NegativeJudgement String
  | NeutralJudgement String
  deriving (Eq, Show, Generic)
instance ToJSON Judgement


{-
    CopyleftKind
     | \
     |  - Copyleft
     |     | \
     |     |  - StrongCopyleft
     |     |     \
     |     |      - SaaSCopyleft
     |     \
     |       - WeakCopyleft
     \
      - NoCopyleft
 -}
data CopyleftKind
  = StrongCopyleft
  | WeakCopyleft
  | SaaSCopyleft
  | Copyleft
  | NoCopyleft
  deriving (Eq, Show, Generic)
instance ToJSON CopyleftKind
instance Ord CopyleftKind where
  compare k1 k2 = let
      kOrder = M.fromList [ (StrongCopyleft, 5 :: Int)
                          , (WeakCopyleft, 4)
                          , (SaaSCopyleft, 3)
                          , (Copyleft, 2)
                          , (NoCopyleft, 1) ]
    in if k1 == k2
       then EQ
       else compare (kOrder M.! k1)  (kOrder M.! k2)
pessimisticMergeCopyleft :: CopyleftKind -> CopyleftKind -> CopyleftKind
-- pessimisticMergeCopyleft = max
pessimisticMergeCopyleft SaaSCopyleft _        = SaaSCopyleft
pessimisticMergeCopyleft _ SaaSCopyleft        = SaaSCopyleft
pessimisticMergeCopyleft StrongCopyleft _      = StrongCopyleft
pessimisticMergeCopyleft _ StrongCopyleft      = StrongCopyleft
pessimisticMergeCopyleft WeakCopyleft _        = WeakCopyleft
pessimisticMergeCopyleft _ WeakCopyleft        = WeakCopyleft
pessimisticMergeCopyleft Copyleft _            = Copyleft
pessimisticMergeCopyleft _ Copyleft            = Copyleft
pessimisticMergeCopyleft NoCopyleft NoCopyleft = NoCopyleft

{-
     License_Unknown
      | \
      |  - OpenSourceLicense_Unknown
      |     | \
      |     \  - OpenSourceLicense_NoCopyleft
      |      - OpenSourceLicense_Copyleft <CopyleftKind>
      \
       - NonOpenSourceLicense
          | | \
          | \  - PublicDomain
          \  - ProprietaryFreeLicense
           - CommercialLicense
-}
-- data LicenseTaxonomy
--   = License_Unknown
--   | OpenSourceLicense_Unknown
--   | OpenSourceLicense_Copyleft CopyleftKind
--   | OpenSourceLicense_NoCopyleft
--   | NonOpenSourceLicense
--   | PublicDomain
--   | ProprietaryFreeLicense
--   | CommercialLicense
--   deriving (Eq, Show, Generic)
-- instance ToJSON LicenseTaxonomy

type LicenseName
  = String

class (Show a, ToJSON a) => LFRaw a where
  getLicenseFactClassifier :: a -> LicenseFactClassifier
  -- Statements:
  getImpliedNames :: a -> CollectedLicenseStatementResult LicenseName
  getImpliedFullName :: a -> RankedLicenseStatementResult LicenseName
  getImpliedFullName _ = getEmptyLicenseStatement
  getImpliedId :: a -> RankedLicenseStatementResult LicenseName
  getImpliedId _ = getEmptyLicenseStatement
  getImpliedURLs :: a -> CollectedLicenseStatementResult (String, URL)
  getImpliedURLs _ = getEmptyLicenseStatement
  getImpliedText :: a -> RankedLicenseStatementResult Text
  getImpliedText _ = getEmptyLicenseStatement
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
    copyleft = let
        iCopyleft = getImpliedCopyleft a
      in case getCalculatedCopyleft a of
        Nothing        -> []
        Just cCopyleft -> [ "calculatedCopyleft" .= cCopyleft
                          , "impliedCopyleft" .= iCopyleft ]
  in object $ impliedNames ++ impliedId ++ impliedURLs ++ impliedText ++ impliedJudgement ++ copyleft

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
  getLicenseFactClassifier (LicenseFact _ raw) = getLicenseFactClassifier raw
  getImpliedNames (LicenseFact _ raw)          = getImpliedNames raw
  getImpliedFullName (LicenseFact _ raw)       = getImpliedFullName raw
  getImpliedId (LicenseFact _ raw)             = getImpliedId raw
  getImpliedURLs (LicenseFact _ raw)           = getImpliedURLs raw
  getImpliedText (LicenseFact _ raw)           = getImpliedText raw
  getImpliedJudgement (LicenseFact _ raw)      = getImpliedJudgement raw
  getImpliedCopyleft (LicenseFact _ raw)       = getImpliedCopyleft raw

type Facts
  = Vector LicenseFact
