{-# LANGUAGE ExistentialQuantification #-}
{-# LANGUAGE TypeFamilies #-}
{-# LANGUAGE GADTs #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE DeriveGeneric #-}
module Model.Statement
  ( LicenseStatementResult
  , Rank, RankedLicenseStatementResult (..), unpackRLSR
  , CollectedLicenseStatementResult (..), unpackCLSR
  ) where

import qualified Prelude as P
import           MyPrelude

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
data CollectedLicenseStatementResult a where
  CLSR :: (Show a, ToJSON a) => [a] -> CollectedLicenseStatementResult a
  NoCLSR :: (Show a, ToJSON a) => CollectedLicenseStatementResult a
unpackCLSR :: CollectedLicenseStatementResult a -> [a]
unpackCLSR (CLSR as) = as
unpackCLSR NoCLSR    = []
instance (Show a, ToJSON a) => Show (CollectedLicenseStatementResult a) where
  show = show . unpackCLSR

class LicenseStatementResult a where
  mergeLicenseStatementResults :: a -> a -> a
instance LicenseStatementResult (RankedLicenseStatementResult a) where
  mergeLicenseStatementResults NoRLSR s2                     = s2
  mergeLicenseStatementResults s1 NoRLSR                     = s1
  mergeLicenseStatementResults s1@(RLSR r1 _) s2@(RLSR r2 _) = if r1 > r2
                                                               then s1
                                                               else s2
instance LicenseStatementResult (CollectedLicenseStatementResult a) where
  mergeLicenseStatementResults NoCLSR s2             = s2
  mergeLicenseStatementResults s1 NoCLSR             = s1
  mergeLicenseStatementResults (CLSR ss1) (CLSR ss2) = CLSR (ss1 ++ ss2)
