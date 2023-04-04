{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE GADTs #-}
{-# LANGUAGE DefaultSignatures #-}
module Ldbcollector.Model.LicenseFact
  ( Origin (..)
  , FactId
  , FromFact (..)
  , LicenseFact (..)
  , wrapFact, wrapFacts, wrapFactV
  , ApplicableLNs (..)
  , alternativesFromListOfLNs
  , LicenseFactC (..)
  ) where

import           MyPrelude hiding (ByteString)

import           Data.ByteString                  (ByteString)
import qualified Data.ByteString.Lazy.Char8        as C
import           Data.Aeson                        as A
import qualified Data.ByteString.Base16            as B16
import qualified Crypto.Hash.MD5 as MD5
import qualified Data.Map                          as Map
import qualified Data.Vector                       as V

import           Ldbcollector.Model.LicenseName
import           Ldbcollector.Model.LicenseStatement

newtype Origin = Origin String
   deriving (Eq, Show, Ord)

type FactId = String

data FromFact a
    = FromFact
    { originFacts :: [FactId]
    , unFF :: a
    }
deriving instance Show a => Show (FromFact a)
deriving instance Eq a => Eq (FromFact a)
instance (Eq a, Show a) => Ord (FromFact a) where
    compare a b = show a `compare` show b

data ApplicableLNs where
    LN :: LicenseName -> ApplicableLNs
    NLN :: LicenseName -> ApplicableLNs
    AlternativeLNs :: ApplicableLNs -> [ApplicableLNs] -> ApplicableLNs
    ImpreciseLNs :: ApplicableLNs -> [ApplicableLNs] -> ApplicableLNs
alternativesFromListOfLNs :: [LicenseName] -> ApplicableLNs
alternativesFromListOfLNs (best:others) = NLN best `AlternativeLNs` map LN others
alternativesFromListOfLNs [] = undefined


class (Eq a) => LicenseFactC a where
    getType :: a -> String
    getFactId :: a -> FactId
    default getFactId :: (ToJSON a) => a -> FactId
    getFactId a = let
        md5 = (C.unpack . C.fromStrict . B16.encode .  MD5.hashlazy . A.encode) a
        in getType a ++ "\n" ++ md5
    getApplicableLNs :: a -> ApplicableLNs
    getImpliedStmts :: a -> [LicenseStatement]
    getImpliedStmts _ = []
    getImpliedCompatibilities :: a -> [LicenseName]
    getImpliedCompatibilities _ = []

data LicenseFact where
    LicenseFact :: forall a. (Typeable a, ToJSON a, LicenseFactC a) => TypeRep -> a -> LicenseFact
instance Show LicenseFact where
wrapFact :: forall a. (Typeable a, ToJSON a, LicenseFactC a) => a -> LicenseFact
wrapFact a = LicenseFact (typeOf a) a
wrapFacts :: forall a. (Typeable a, ToJSON a, LicenseFactC a) => [a] -> [LicenseFact]
wrapFacts = map wrapFact
wrapFactV :: forall a. (Typeable a, ToJSON a, LicenseFactC a) => V.Vector a -> V.Vector LicenseFact
wrapFactV = V.map wrapFact

instance ToJSON LicenseFact where
    toJSON (LicenseFact _ v) = toJSON v
instance Eq LicenseFact where
    wv1 == wv2 = let
            (LicenseFact t1 _) = wv1
            (LicenseFact t2 _) = wv2
        in ((t1 == t2) && (toJSON wv1 == toJSON wv2))
instance Ord LicenseFact where
    wv1 <= wv2 = let
            (LicenseFact t1 _) = wv1
            (LicenseFact t2 _) = wv2
        in if t1 == t2
           then toJSON wv1 <= toJSON wv2
           else t1 <= t2
instance LicenseFactC LicenseFact where
    getType (LicenseFact _ a) = getType a
    getFactId (LicenseFact _ a) = getFactId a
    getApplicableLNs (LicenseFact _ a) = getApplicableLNs a
    getImpliedStmts (LicenseFact _ a) = getImpliedStmts a
    getImpliedCompatibilities (LicenseFact _ a) = getImpliedCompatibilities a
