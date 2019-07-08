{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE OverloadedStrings #-}
module Model.LicenseProperties.Compatibility
  ( LicenseCompatibilityStatement (..)
  , LicenseCompatibility (..)
  , isCompatibleToWhenDistributedUnderOther, isCompatibleToWhenDistributedUnderSelf, isCompatibleBothWays, isIncompatibleBothWays
  ) where

import qualified Prelude as P
import           MyPrelude

import qualified Data.Map as M

import Model.LicenseProperties.Base

data LicenseCompatibilityStatement
  = LicenseCompatibilityStatement
  { _isCompatibleToWhenDistributedUnderSelf :: Maybe Bool
  , _isCompatibleToWhenDistributedUnderOther :: Maybe Bool
  } deriving (Eq, Show, Generic)
instance ToJSON LicenseCompatibilityStatement


isCompatibleToWhenDistributedUnderOther = LicenseCompatibilityStatement Nothing (Just True)
isCompatibleToWhenDistributedUnderSelf = LicenseCompatibilityStatement (Just True) Nothing
isCompatibleBothWays = LicenseCompatibilityStatement (Just True) (Just True)
isIncompatibleBothWays = LicenseCompatibilityStatement (Just False) (Just False)

instance Semigroup LicenseCompatibilityStatement where
  lcs1 <> lcs2 = let
      mergeTernary :: Maybe Bool -> Maybe Bool -> Maybe Bool
      mergeTernary t1        Nothing   = t1
      mergeTernary Nothing   t2        = t2
      mergeTernary (Just b1) (Just b2) = Just (b1 == b2)
      icwdus1 = _isCompatibleToWhenDistributedUnderSelf lcs1
      icwdus2 = _isCompatibleToWhenDistributedUnderSelf lcs2
      icwduo1 = _isCompatibleToWhenDistributedUnderOther lcs1
      icwduo2 = _isCompatibleToWhenDistributedUnderOther lcs2
      icwdus = mergeTernary icwdus1 icwdus2
      icwduo = mergeTernary icwduo1 icwduo2
    in LicenseCompatibilityStatement icwdus icwduo

data LicenseCompatibility
  = LicenseCompatibility (Map LicenseName LicenseCompatibilityStatement)
  deriving (Eq, Show, Generic)
instance ToJSON LicenseCompatibility

instance Semigroup LicenseCompatibility where
  (LicenseCompatibility m1) <> (LicenseCompatibility m2) = LicenseCompatibility (M.unionWith (<>) m1 m2)

