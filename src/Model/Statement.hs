{-# LANGUAGE TypeFamilies #-}
{-# LANGUAGE GADTs #-}
{-#LANGUAGE StandaloneDeriving #-}
module Model.Statement
  ( LicenseStatementResult (..)
  , Rank, RankedLicenseStatementResult (..), unpackRLSR, unpackSourceFromRLSR, maybeUpdateClassifierInRLSR
  , CollectedLicenseStatementResult (..), unpackCLSR
  , ScopedLicenseStatementResult (..), unpackSLSR, maybeUpdateClassifierInSLSR
  , LicenseFactClassifier (..)
  ) where

import qualified Prelude as P
import           MyPrelude

import qualified Data.Vector as V
import qualified Data.Map as M

import Model.LicenseProperties

class (Eq a) => LicenseStatementResult a where
  mergeLicenseStatementResults :: a -> a -> a
  getEmptyLicenseStatement :: a
  isEmptyLicenseStatement :: a -> Bool
  isEmptyLicenseStatement = (getEmptyLicenseStatement ==)
  mergeLicenseStatementResultList :: Vector a -> a
  mergeLicenseStatementResultList = V.foldl mergeLicenseStatementResults getEmptyLicenseStatement . V.filter (not . isEmptyLicenseStatement)

type Rank
  = Int
data RankedLicenseStatementResult a where
  RLSR :: (Show a, ToJSON a) => LicenseFactClassifier -> Rank -> a -> RankedLicenseStatementResult a
  NoRLSR :: RankedLicenseStatementResult a
unpackRLSR :: RankedLicenseStatementResult a -> Maybe a
unpackRLSR (RLSR _ _ a) = Just a
unpackRLSR NoRLSR       = Nothing
unpackSourceFromRLSR :: RankedLicenseStatementResult a -> Maybe LicenseFactClassifier
unpackSourceFromRLSR (RLSR lfc _ _) = Just lfc
unpackSourceFromRLSR _              = Nothing
deriving instance (Eq a) => Eq (RankedLicenseStatementResult a)
instance (Show a, ToJSON a) => Show (RankedLicenseStatementResult a) where
  show = show . unpackRLSR
instance (Show a, ToJSON a, Eq a) => LicenseStatementResult (RankedLicenseStatementResult a) where
  mergeLicenseStatementResults NoRLSR s2                         = s2
  mergeLicenseStatementResults s1 NoRLSR                         = s1
  mergeLicenseStatementResults s1@(RLSR _ r1 _) s2@(RLSR _ r2 _) = if r2 > r1
                                                                   then s2
                                                                   else s1
  getEmptyLicenseStatement                                       = NoRLSR
instance (ToJSON a) => ToJSON (RankedLicenseStatementResult a) where
  toJSON = toJSON . unpackRLSR
maybeUpdateClassifierInRLSR :: LicenseFactClassifier -> RankedLicenseStatementResult a -> RankedLicenseStatementResult a
maybeUpdateClassifierInRLSR lfc rlsr@(RLSR oldLfc r a) | lfc == oldLfc = RLSR lfc r a
                                                       | otherwise     = rlsr
maybeUpdateClassifierInRLSR _ rlsr                                     = rlsr

data CollectedLicenseStatementResult a where
  CLSR :: (Show a, ToJSON a, Eq a) => [a] -> CollectedLicenseStatementResult a
  NoCLSR :: CollectedLicenseStatementResult a
unpackCLSR :: CollectedLicenseStatementResult a -> [a]
unpackCLSR (CLSR as) = as
unpackCLSR NoCLSR    = []
instance (Eq a) => Eq (CollectedLicenseStatementResult a) where
  NoCLSR == NoCLSR         = True
  (CLSR []) == NoCLSR      = True
  NoCLSR == (CLSR [])      = True
  (CLSR vs1) == (CLSR vs2) = vs1 == vs2 -- TODO: up to order?
  _ == _                   = False
instance (Show a, ToJSON a) => Show (CollectedLicenseStatementResult a) where
  show = show . unpackCLSR
instance (Show a, ToJSON a, Eq a) => LicenseStatementResult (CollectedLicenseStatementResult a) where
  mergeLicenseStatementResults NoCLSR (CLSR [])      = NoCLSR
  mergeLicenseStatementResults (CLSR []) NoCLSR      = NoCLSR
  mergeLicenseStatementResults NoCLSR s2             = s2
  mergeLicenseStatementResults s1 NoCLSR             = s1
  mergeLicenseStatementResults (CLSR ss1) (CLSR ss2) = CLSR (nub (ss1 ++ ss2))

  getEmptyLicenseStatement                           = NoCLSR

  isEmptyLicenseStatement NoCLSR                     = True
  isEmptyLicenseStatement (CLSR [])                  = True
  isEmptyLicenseStatement _                          = False
instance (ToJSON a) => ToJSON (CollectedLicenseStatementResult a) where
  toJSON = toJSON . unpackCLSR

data ScopedLicenseStatementResult a where
  SLSR :: (Show a, ToJSON a) => LicenseFactClassifier -> a -> ScopedLicenseStatementResult a
  SLSRMap :: (Show a, ToJSON a) => Map LicenseFactClassifier a -> ScopedLicenseStatementResult a
  NoSLSR :: ScopedLicenseStatementResult a
unpackSLSR :: ScopedLicenseStatementResult a -> Map LicenseFactClassifier a
unpackSLSR (SLSR lfc a) = M.singleton lfc a
unpackSLSR (SLSRMap m)  = m
unpackSLSR NoSLSR       = M.empty
instance (Eq a) => Eq (ScopedLicenseStatementResult a) where
  slsr1 == slsr2 = unpackSLSR slsr1 == unpackSLSR slsr2
instance (Show a, ToJSON a) => Show (ScopedLicenseStatementResult a) where
  show = show . unpackSLSR
instance (Show a, ToJSON a, Eq a) => LicenseStatementResult (ScopedLicenseStatementResult a) where
  mergeLicenseStatementResults NoSLSR s2 = s2
  mergeLicenseStatementResults s1 NoSLSR = s1
  mergeLicenseStatementResults s1 s2     = SLSRMap (M.union (unpackSLSR s1) (unpackSLSR s2))
  getEmptyLicenseStatement               = NoSLSR
instance (ToJSON a) => ToJSON (ScopedLicenseStatementResult a) where
  toJSON = toJSON . unpackSLSR
maybeUpdateClassifierInSLSR :: LicenseFactClassifier -> ScopedLicenseStatementResult a -> ScopedLicenseStatementResult a
maybeUpdateClassifierInSLSR lfc slsr@(SLSR oldLfc a) | lfc == oldLfc = SLSR lfc a
                                                     | otherwise     = slsr
maybeUpdateClassifierInSLSR _ slsr                                   = slsr


