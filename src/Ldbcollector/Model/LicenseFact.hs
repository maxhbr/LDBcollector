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
    licenseFactUrl,
    ApplicableLNs (..),
    LicenseNameCluster (..),
    alternativesFromListOfLNs,
    LicenseFactC (..),
    licenseFactsImplicationsToMarkup,
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

instance H.ToMarkup SourceRef where
  toMarkup = H.toMarkup . show

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

instance H.ToMarkup FactId where
  toMarkup = H.toMarkup . show

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
    H.ul $ do
      H.li $ do
        H.b "this:"
        H.ul H.! A.class_ "capsulUl clearfix" $ (H.li . H.toMarkup) name
      unless (null sameNames) . H.li $ do
        H.b (fromString ("other LicenseNames (" ++ show (length sameNames) ++ "):"))
        H.ul H.! A.class_ "capsulUl clearfix" $ mapM_ (H.li . H.toMarkup) (sort sameNames)
      unless (null otherNames) . H.li $ do
        H.b (fromString ("other LicenseName Hints (" ++ show (length otherNames) ++ "):"))
        H.ul H.! A.class_ "capsulUl clearfix" $ mapM_ (H.li . H.toMarkup) (sort otherNames)

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
  getImpliedLicenseTags :: a -> [LicenseTag]
  getImpliedLicenseTags =
    let filterFun [] = []
        filterFun (LicenseTag t : stmts) = t : filterFun stmts
        filterFun (_ : stmts) = filterFun stmts
     in filterFun . flattenStatements . getImpliedStmts
  getAllImpliedLicenseTags :: a -> [LicenseTag]
  getAllImpliedLicenseTags a = getImpliedLicenseTags a ++ (map tagFromLicenseRating (getImpliedLicenseRatings a))
  getImpliedLicenseRatings :: a -> [LicenseRating]
  getImpliedLicenseRatings =
    let filterFun [] = []
        filterFun (LicenseRating r : stmts) = r : filterFun stmts
        filterFun (_ : stmts) = filterFun stmts
     in filterFun . flattenStatements . getImpliedStmts
  getImpliedLicenseComments :: a -> [LicenseComment]
  getImpliedLicenseComments =
    let filterFun [] = []
        filterFun (LicenseComment c : stmts) = c : filterFun stmts
        filterFun (_ : stmts) = filterFun stmts
     in filterFun . flattenStatements . getImpliedStmts
  getImpliedLicenseUrls :: a -> [(Maybe String, String)]
  getImpliedLicenseUrls =
    let filterFun [] = []
        filterFun (LicenseUrl scope url : stmts) = (scope, url) : filterFun stmts
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
  getImpliedLicenseRules :: a -> [Text]
  getImpliedLicenseRules =
    let filterFun [] = []
        filterFun (LicenseRule r : stmts) = r : filterFun stmts
        filterFun (_ : stmts) = filterFun stmts
     in filterFun . flattenStatements . getImpliedStmts
  getImpliedPlainLicenseStatements :: a -> [(String, Maybe Text)]
  getImpliedPlainLicenseStatements =
    let filterFun [] = []
        filterFun (LicenseStatement r : stmts) = (r, Nothing) : filterFun stmts
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

licenseFactUrl :: LicenseFact -> H.Markup -> H.Markup
licenseFactUrl fact markup = do
  let factId@(FactId ty hash) = getFactId fact
  H.a H.! A.href (H.toValue $ "/fact" </> ty </> hash) $ markup

licenseFactOriginToMarkup :: LicenseFact -> H.Markup
licenseFactOriginToMarkup fact =
  let desc = H.toValue $ show $ getFactId fact
   in H.span H.! A.title desc $ do
        H.toMarkup ("[" :: String)
        licenseFactUrl fact (H.toMarkup $ getType fact)
        H.toMarkup ("]" :: String)

createProvidedBy :: (LicenseFact -> Bool) -> [LicenseFact] -> H.Markup
createProvidedBy f facts = do
  let providingFacts = filter f facts
  H.span H.! A.class_ "provided-by" $ do
    "(provided by: "
    mapM_ licenseFactOriginToMarkup providingFacts
    ")"

licenseFactsImplicationsToMarkup :: [LicenseFact] -> LicenseNameCluster -> Markup
licenseFactsImplicationsToMarkup facts cluster = do
  -- TODO: shouldn't it be possible to compute the cluster from the facts? Isn' that consistent with the use in Server.hs?
  H.div H.! A.class_ "two-columns-grid" $ do
    H.div $ do
      H.h2 "LicenseNames"
      H.toMarkup cluster
    H.div $ do
      let implicationsToList :: (Eq a, H.ToMarkup a) => H.Html -> (LicenseFact -> [a]) -> Markup
          implicationsToList title getter = do
            let implications = nub $ concatMap getter facts
            unless (null implications) $ do
              H.h2 title
              H.ul $
                mapM_
                  ( \i -> do
                      H.li $ do
                        H.toMarkup i
                        createProvidedBy ((i `elem`) . getter) facts
                  )
                  implications

      implicationsToList "License Types" getImpliedLicenseTypes
      implicationsToList "License Ratings" getImpliedLicenseRatings
      implicationsToList "License Tags" getImpliedLicenseTags
      implicationsToList "License Comments" getImpliedLicenseComments
      let urls = nub $ concatMap getImpliedLicenseUrls facts
      unless (null urls) $ do
        H.h3 "URLs"
        H.ul $
          mapM_
            ( H.li
                . ( \(ns, url) -> do
                      case ns of
                        Just ns' -> do
                          H.toMarkup ns'
                          ": "
                        Nothing -> pure ()
                      H.a H.! A.href (H.toValue url) H.! A.target "_blank" $ H.toMarkup url
                  )
            )
            urls
      let strStmts = nub $ concatMap getImpliedPlainLicenseStatements facts
      unless (null strStmts) $ do
        H.h3 "Other Statements"
        H.ul $
          mapM_
            ( H.li
                . ( \case
                      (stmt, Just desc) -> do
                        H.toMarkup stmt
                        H.br
                        H.toMarkup desc
                      (stmt, Nothing) -> H.toMarkup stmt
                  )
            )
            strStmts
  let texts = nub $ concatMap getImpliedLicenseTexts facts
  unless (null texts) $ do
    H.h3 "Texts"
    H.ul $
      mapM_
        ( \text ->
            H.li $ do
              H.details $ do
                H.summary "Text:"
                H.pre (H.toMarkup text)
        )
        texts

instance LicenseFactC LicenseFact where
  getType (LicenseFact _ a) = getType a
  getFactId (LicenseFact _ a) = getFactId a
  getApplicableLNs (LicenseFact _ a) = getApplicableLNs a
  getImpliedStmts (LicenseFact _ a) = getImpliedStmts a
  toMarkup fact@(LicenseFact _ a) = do
    toMarkup a
    licenseFactsImplicationsToMarkup [fact] (getLicenseNameCluster a)
