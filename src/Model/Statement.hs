{-# LANGUAGE ExistentialQuantification #-}
{-# LANGUAGE TypeFamilies #-}
{-# LANGUAGE GADTs #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE DeriveGeneric #-}
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

class LicenseStatementResult a where
  mergeLicenseStatementResults :: a -> a -> a
  getEmptyLicenseStatement :: a
  mergeLicenseStatementResultList :: Vector a -> a
  mergeLicenseStatementResultList = V.foldl mergeLicenseStatementResults getEmptyLicenseStatement

type Rank
  = Int
data RankedLicenseStatementResult a where
  RLSR :: (Show a, ToJSON a) => Rank -> a -> RankedLicenseStatementResult a
  NoRLSR :: (Show a, ToJSON a) => RankedLicenseStatementResult a
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

data CollectedLicenseStatementResult a where
  CLSR :: (Show a, ToJSON a) => [a] -> CollectedLicenseStatementResult a
  NoCLSR :: (Show a, ToJSON a) => CollectedLicenseStatementResult a
unpackCLSR :: CollectedLicenseStatementResult a -> [a]
unpackCLSR (CLSR as) = as
unpackCLSR NoCLSR    = []
instance (Show a, ToJSON a) => Show (CollectedLicenseStatementResult a) where
  show = show . unpackCLSR
instance (Show a, ToJSON a) => LicenseStatementResult (CollectedLicenseStatementResult a) where
  mergeLicenseStatementResults NoCLSR s2             = s2
  mergeLicenseStatementResults s1 NoCLSR             = s1
  mergeLicenseStatementResults (CLSR ss1) (CLSR ss2) = CLSR (ss1 ++ ss2)
  getEmptyLicenseStatement                           = NoCLSR

data ScopedLicenseStatementResult a where
  SLSR :: (Show a, ToJSON a) => Map LicenseFactClassifier a -> ScopedLicenseStatementResult a
  NoSLSR :: (Show a, ToJSON a) => ScopedLicenseStatementResult a
unpackSLSR :: ScopedLicenseStatementResult a -> Map LicenseFactClassifier a
unpackSLSR (SLSR m) = m
unpackSLSR NoSLSR = M.empty
instance (Show a, ToJSON a) => Show (ScopedLicenseStatementResult a) where
  show = show . unpackSLSR
instance (Show a, ToJSON a) => LicenseStatementResult (ScopedLicenseStatementResult a) where
  mergeLicenseStatementResults NoSLSR s2           = s2
  mergeLicenseStatementResults s1 NoSLSR           = s1
  mergeLicenseStatementResults (SLSR m1) (SLSR m2) = SLSR (M.union m1 m2)
  getEmptyLicenseStatement                         = NoSLSR


