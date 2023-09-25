{-# LANGUAGE DefaultSignatures #-}
{-# LANGUAGE GADTs #-}
{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE OverloadedStrings #-}

module Ldbcollector.Model.LicenseFact
  ( SourceRef (..),
    FactId (..),
    Qualified (..),
    LicenseFact (..),
    wrapFact,
    wrapFacts,
    wrapFactV,
    ApplicableLNs (..),
    LicenseNameCluster (..),
    alternativesFromListOfLNs,
    LicenseFactC (..),
  )
where

import Crypto.Hash.MD5 qualified as MD5
import Data.Aeson as A
import Data.ByteString (ByteString)
import Data.ByteString.Base16 qualified as B16
import Data.ByteString.Lazy.Char8 qualified as C
import Data.Map qualified as Map
import Data.Text.Encoding qualified as Enc
import Data.Vector qualified as V
import Ldbcollector.Model.LicenseName
import Ldbcollector.Model.LicenseStatement
import MyPrelude hiding (ByteString)
import Text.Blaze qualified as H
import Text.Blaze.Html5 qualified as H
import Text.Blaze.Html5.Attributes qualified as A

newtype SourceRef = Source String
  deriving (Eq, Ord)

instance Show SourceRef where
  show (Source s) = s

instance IsString SourceRef where
  fromString = Source

data FactId
  = FactId String String
  deriving (Eq, Generic)

data Qualified a = Qualified
  { qFactId :: FactId,
    -- , qSource :: SourceRef
    qValue :: a
  }

instance Show FactId where
  show (FactId ty hash) = ty ++ ":" ++ hash

instance ToJSON FactId where
  toJSON (FactId ty hash) = toJSON [ty, hash]

data ApplicableLNs where
  LN :: LicenseName -> ApplicableLNs
  AlternativeLNs :: ApplicableLNs -> [ApplicableLNs] -> ApplicableLNs
  ImpreciseLNs :: ApplicableLNs -> [ApplicableLNs] -> ApplicableLNs
  deriving (Eq, Show, Generic)

alternativesFromListOfLNs :: [LicenseName] -> ApplicableLNs
alternativesFromListOfLNs (best : others) = LN best `AlternativeLNs` map LN others
alternativesFromListOfLNs [] = undefined

instance ToJSON ApplicableLNs

data LicenseNameCluster = LicenseNameCluster
  { name :: LicenseName,
    sameNames :: [LicenseName],
    otherNames :: [LicenseName]
  }

instance ToJSON LicenseNameCluster where
  toJSON (LicenseNameCluster name sameNames otherNames) =
    A.object
      [ (fromString . show) name
          A..= A.object
            [ "same" A..= sameNames,
              "other" A..= otherNames
            ]
      ]

instance H.ToMarkup LicenseNameCluster where
  toMarkup (LicenseNameCluster name sameNames otherNames) = do
    H.div H.! A.class_ "two-columns-grid" $ do
      H.div $ do
        H.b (fromString ("LicenseNames for " ++ show name))
        H.ul H.! A.class_ "capsulUl clearfix" $ mapM_ (H.li . H.toMarkup) sameNames
      unless (null otherNames) $ do
        H.div $ do
          H.b (fromString ("LicenseName Hints towards " ++ show name))
          H.ul H.! A.class_ "capsulUl clearfix" $ mapM_ (H.li . H.toMarkup) otherNames

applicableLNsToLicenseNameCluster :: ApplicableLNs -> LicenseNameCluster
applicableLNsToLicenseNameCluster (LN ln) = LicenseNameCluster ln [] []
applicableLNsToLicenseNameCluster (AlternativeLNs aln alns) =
  let (LicenseNameCluster ln same other) = applicableLNsToLicenseNameCluster aln
      alnsClusters = map applicableLNsToLicenseNameCluster alns
      samesFromAlnsClusters = concatMap (\(LicenseNameCluster ln' same' _) -> ln' : same') alnsClusters
      othersFromAlnsClusters = concatMap (\(LicenseNameCluster _ _ other') -> other') alnsClusters
   in LicenseNameCluster ln (same ++ samesFromAlnsClusters) (other ++ othersFromAlnsClusters)
applicableLNsToLicenseNameCluster (ImpreciseLNs aln alns) =
  let (LicenseNameCluster ln same other) = applicableLNsToLicenseNameCluster aln
      alnsClusters = map applicableLNsToLicenseNameCluster alns
      othersFromAlnsClusters = concatMap (\(LicenseNameCluster ln' same' other') -> ln' : same' ++ other') alnsClusters
   in LicenseNameCluster ln same (other ++ othersFromAlnsClusters)

class (Eq a) => LicenseFactC a where
  getType :: a -> String
  getFactId :: a -> FactId
  default getFactId :: (ToJSON a) => a -> FactId
  getFactId a =
    let md5 = (C.unpack . C.fromStrict . B16.encode . MD5.hashlazy . A.encode) a
     in FactId (getType a) md5
  getApplicableLNs :: a -> ApplicableLNs
  getImpliedStmts :: a -> [LicenseStatement]
  getImpliedStmts _ = []
  toMarkup :: a -> Markup
  toMarkup _ = mempty

  {-
   - helper functions
   -}
  getLicenseNameCluster :: a -> LicenseNameCluster
  getLicenseNameCluster = applicableLNsToLicenseNameCluster . getApplicableLNs
  getMainLicenseName :: a -> LicenseName
  getMainLicenseName = (\(LicenseNameCluster ln _ _) -> ln) . getLicenseNameCluster
  getImpliedLicenseRatings :: a -> [LicenseRating]
  getImpliedLicenseRatings =
    let filterFun [] = []
        filterFun (LicenseRating r : stmts) = r : filterFun stmts
        filterFun (_ : stmts) = filterFun stmts
     in filterFun . flattenStatements . getImpliedStmts
  getImpliedLicenseUrls :: a -> [String]
  getImpliedLicenseUrls =
    let filterFun [] = []
        filterFun (LicenseUrl url : stmts) = url : filterFun stmts
        filterFun (_ : stmts) = filterFun stmts
     in filterFun . flattenStatements . getImpliedStmts
  getImpliedLicenseTypes :: a -> [LicenseType]
  getImpliedLicenseTypes =
    let filterFun [] = []
        filterFun (LicenseType ty : stmts) = ty : filterFun stmts
        filterFun (_ : stmts) = filterFun stmts
     in filterFun . flattenStatements . getImpliedStmts
  getImpliedLicenseTexts :: a -> [Text]
  getImpliedLicenseTexts =
    let filterFun [] = []
        filterFun (LicenseText txts : stmts) = txts : filterFun stmts
        filterFun (_ : stmts) = filterFun stmts
     in filterFun . flattenStatements . getImpliedStmts

data LicenseFact where
  LicenseFact :: forall a. (Show a, Typeable a, ToJSON a, LicenseFactC a) => TypeRep -> a -> LicenseFact

instance Show LicenseFact where
  show (LicenseFact _ a) = show a

instance NFData LicenseFact where
  rnf (LicenseFact _t a) = rwhnf a

wrapFact :: forall a. (Show a, Typeable a, ToJSON a, LicenseFactC a) => a -> LicenseFact
wrapFact a = LicenseFact (typeOf a) a

wrapFacts :: forall a. (Show a, Typeable a, ToJSON a, LicenseFactC a) => [a] -> [LicenseFact]
wrapFacts = map wrapFact

wrapFactV :: forall a. (Show a, Typeable a, ToJSON a, LicenseFactC a) => V.Vector a -> V.Vector LicenseFact
wrapFactV = V.map wrapFact

instance ToJSON LicenseFact where
  toJSON (LicenseFact _ v) =
    object
      [ "type" .= getType v,
        "id" .= getFactId v,
        "applicableLNs" .= getApplicableLNs v,
        "impliedStmts" .= getImpliedStmts v,
        "raw" .= v
      ]

instance Eq LicenseFact where
  wv1 == wv2 =
    let (LicenseFact t1 _) = wv1
        (LicenseFact t2 _) = wv2
     in ((t1 == t2) && (toJSON wv1 == toJSON wv2))

instance Ord LicenseFact where
  wv1 <= wv2 =
    let (LicenseFact t1 _) = wv1
        (LicenseFact t2 _) = wv2
     in if t1 == t2
          then toJSON wv1 <= toJSON wv2
          else t1 <= t2

instance LicenseFactC LicenseFact where
  getType (LicenseFact _ a) = getType a
  getFactId (LicenseFact _ a) = getFactId a
  getApplicableLNs (LicenseFact _ a) = getApplicableLNs a
  getImpliedStmts (LicenseFact _ a) = getImpliedStmts a
  toMarkup (LicenseFact _ a) = do
    toMarkup a
    H.div $ do
      H.h3 "Names"
      (H.toMarkup . getLicenseNameCluster) a
    H.div H.! A.class_ "two-columns-grid" $ do
      let ratings = getImpliedLicenseRatings a
      unless (null ratings) $ do
        H.div $ do
          H.h3 "Ratings"
          H.ul $ mapM_ (H.li . H.toMarkup) ratings
      let urls = getImpliedLicenseUrls a
      unless (null urls) $ do
        H.div $ do
          H.h3 "URLs"
          H.ul $ mapM_ (H.li . H.toMarkup) urls
