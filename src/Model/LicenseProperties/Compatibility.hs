{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE OverloadedStrings #-}
module Model.LicenseProperties.Compatibility
  ( LicenseCompatibilityStatement (..)
  , LicenseCompatibility (..), singletonLicenseCompatibility
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

instance Semigroup LicenseCompatibilityStatement where
  (LicenseCompatibilityStatement icwdus1 icwduo1) <> (LicenseCompatibilityStatement icwdus2 icwduo2) = let
      mergeTernary :: Maybe Bool -> Maybe Bool -> Maybe Bool
      mergeTernary t1        Nothing   = t1
      mergeTernary Nothing   t2        = t2
      mergeTernary (Just b1) (Just b2) = Just (b1 == b2)
      icwdus = mergeTernary icwdus1 icwdus2
      icwduo = mergeTernary icwduo1 icwduo2
    in LicenseCompatibilityStatement icwdus icwduo

data LicenseCompatibility
  = LicenseCompatibility (Map LicenseName LicenseCompatibilityStatement)
  deriving (Eq, Show, Generic)
instance ToJSON LicenseCompatibility

instance Semigroup LicenseCompatibility where
  (LicenseCompatibility m1) <> (LicenseCompatibility m2) = LicenseCompatibility (M.unionWith (<>) m1 m2)

singletonLicenseCompatibility :: LicenseName -> LicenseCompatibilityStatement -> LicenseCompatibility
singletonLicenseCompatibility ln lcs = LicenseCompatibility (M.fromList [(ln, lcs)])

isCompatibleToWhenDistributedUnderOther, isCompatibleToWhenDistributedUnderSelf, isCompatibleBothWays, isIncompatibleBothWays :: LicenseName -> LicenseCompatibility
isCompatibleToWhenDistributedUnderOther ln = singletonLicenseCompatibility ln $ LicenseCompatibilityStatement Nothing (Just True)
isCompatibleToWhenDistributedUnderSelf ln = singletonLicenseCompatibility ln $ LicenseCompatibilityStatement (Just True) Nothing
isCompatibleBothWays ln = singletonLicenseCompatibility ln $ LicenseCompatibilityStatement (Just True) (Just True)
isIncompatibleBothWays ln = singletonLicenseCompatibility ln $ LicenseCompatibilityStatement (Just False) (Just False)
