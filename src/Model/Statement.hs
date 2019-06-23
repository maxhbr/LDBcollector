{-# LANGUAGE ExistentialQuantification #-}
{-# LANGUAGE TypeFamilies #-}
{-# LANGUAGE GADTs #-}
{-# LANGUAGE OverloadedStrings #-}
{-#LANGUAGE DeriveGeneric #-}
{-#LANGUAGE StandaloneDeriving #-}
module Model.Statement
  ( LicenseStatementResult (..)
  , Rank, RankedLicenseStatementResult (..), unpackRLSR
  , CollectedLicenseStatementResult (..), unpackCLSR
  , ScopedLicenseStatementResult (..), unpackSLSR
  , LicenseFactClassifier (..)
  ) where

import qualified Prelude as P
import           MyPrelude

import qualified Data.Vector as V
import qualified Data.Map as M
import qualified Data.Text as T

newtype LicenseFactClassifier
  = LFC [Text]
  deriving (Eq, Generic)
instance Show LicenseFactClassifier where
  show (LFC brc) = T.unpack $ T.intercalate "/" brc
instance Ord LicenseFactClassifier where
  compare lfc1 lfc2 = compare (show lfc1) (show lfc2)
instance ToJSON LicenseFactClassifier where
  toJSON lfc = toJSON $ show lfc
instance ToJSONKey LicenseFactClassifier

class LicenseStatementResult a where
  mergeLicenseStatementResults :: a -> a -> a
  getEmptyLicenseStatement :: a
  mergeLicenseStatementResultList :: Vector a -> a
  mergeLicenseStatementResultList = V.foldl mergeLicenseStatementResults getEmptyLicenseStatement

type Rank
  = Int
data RankedLicenseStatementResult a where
  RLSR :: (Show a, ToJSON a) => Rank -> a -> RankedLicenseStatementResult a
  NoRLSR :: RankedLicenseStatementResult a
unpackRLSR :: RankedLicenseStatementResult a -> Maybe a
unpackRLSR (RLSR _ a) = Just a
unpackRLSR NoRLSR     = Nothing
instance (Show a, ToJSON a) => Show (RankedLicenseStatementResult a) where
  show = show . unpackRLSR
instance (Show a, ToJSON a) => LicenseStatementResult (RankedLicenseStatementResult a) where
  mergeLicenseStatementResults NoRLSR s2                     = s2
  mergeLicenseStatementResults s1 NoRLSR                     = s1
  mergeLicenseStatementResults s1@(RLSR r1 _) s2@(RLSR r2 _) = if r1 > r2
                                                               then s1
                                                               else s2
  getEmptyLicenseStatement                                   = NoRLSR
instance (ToJSON a) => ToJSON (RankedLicenseStatementResult a) where
  toJSON = toJSON . unpackRLSR
deriving instance (Eq a) => Eq (RankedLicenseStatementResult a)

data CollectedLicenseStatementResult a where
  CLSR :: (Show a, ToJSON a, Eq a) => [a] -> CollectedLicenseStatementResult a
  NoCLSR :: CollectedLicenseStatementResult a
unpackCLSR :: CollectedLicenseStatementResult a -> [a]
unpackCLSR (CLSR as) = as
unpackCLSR NoCLSR    = []
instance (Show a, ToJSON a) => Show (CollectedLicenseStatementResult a) where
  show = show . unpackCLSR
instance (Show a, ToJSON a, Eq a) => LicenseStatementResult (CollectedLicenseStatementResult a) where
  mergeLicenseStatementResults NoCLSR (CLSR [])      = NoCLSR
  mergeLicenseStatementResults (CLSR []) NoCLSR      = NoCLSR
  mergeLicenseStatementResults NoCLSR s2             = s2
  mergeLicenseStatementResults s1 NoCLSR             = s1
  mergeLicenseStatementResults (CLSR ss1) (CLSR ss2) = CLSR (nub (ss1 ++ ss2))
  getEmptyLicenseStatement                           = NoCLSR
instance (ToJSON a) => ToJSON (CollectedLicenseStatementResult a) where
  toJSON = toJSON . unpackCLSR
instance (Eq a) => Eq (CollectedLicenseStatementResult a) where
  NoCLSR == NoCLSR         = True
  (CLSR []) == NoCLSR      = True
  NoCLSR == (CLSR [])      = True
  (CLSR vs1) == (CLSR vs2) = vs1 == vs2 -- TODO: up to order?
  _ == _                   = False

data ScopedLicenseStatementResult a where
  SLSR :: (Show a, ToJSON a) => LicenseFactClassifier -> a -> ScopedLicenseStatementResult a
  SLSRMap :: (Show a, ToJSON a) => Map LicenseFactClassifier a -> ScopedLicenseStatementResult a
  NoSLSR :: ScopedLicenseStatementResult a
unpackSLSR :: ScopedLicenseStatementResult a -> Map LicenseFactClassifier a
unpackSLSR (SLSR lfc a) = M.singleton lfc a
unpackSLSR (SLSRMap m)  = m
unpackSLSR NoSLSR       = M.empty
instance (Show a, ToJSON a) => Show (ScopedLicenseStatementResult a) where
  show = show . unpackSLSR
instance (Show a, ToJSON a) => LicenseStatementResult (ScopedLicenseStatementResult a) where
  mergeLicenseStatementResults NoSLSR s2 = s2
  mergeLicenseStatementResults s1 NoSLSR = s1
  mergeLicenseStatementResults s1 s2     = SLSRMap (M.union (unpackSLSR s1) (unpackSLSR s2))
  getEmptyLicenseStatement               = NoSLSR
instance (ToJSON a) => ToJSON (ScopedLicenseStatementResult a) where
  toJSON = toJSON . unpackSLSR


