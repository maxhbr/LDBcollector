{-# LANGUAGE ExistentialQuantification #-}
{-# LANGUAGE TypeFamilies #-}
{-# LANGUAGE GADTs #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE DeriveGeneric #-}
module Model.Fact
  ( LicenseStatementType
  , FSRaw (..)
  , FactStatement (..), extractLicenseStatementLabel
  , Statements
  , LicenseName
  , LicenseFactClassifier (..)
  , LFRaw (..)
  , LicenseFact (..), extractLicenseFactClassifier
  , LicenseStatementType
  , Facts
  ) where

import qualified Prelude as P
import           MyPrelude

import qualified Data.Text as T
import qualified Data.Vector as V

type LicenseStatementType
  = String
  {-
    is permissive: yes (bla bla bla)
    ------+------  -+-  -----+-----
           \         \        \
            \         \        \---- description
             \         \------------ value
              \--------------------- label
  -}
class FSRaw a where
  getStatementLabel :: a -> Text
  getStatementContent :: a -> Value
  unRawStatement :: a -> Maybe Text -> LicenseFactClassifier -> FactStatement
  unRawStatement = FactStatement

data FactStatement
  = forall a. (FSRaw a)
  => FactStatement
  { _rawFactStatement :: a
  , _factDescription :: Maybe Text
  , _factSourceClassifier :: LicenseFactClassifier
  }
instance ToJSON FactStatement where
  toJSON (FactStatement a desc lfc) = let
      lbl = getStatementLabel a
      val = getStatementContent a
    in object [ lbl .= (case desc of
                           Just d ->  object [ "value" .= val, "source" .= tShow lfc, "description" .= d ]
                           Nothing -> object [ "value" .= val, "source" .= tShow lfc ])]
extractLicenseStatementLabel :: FactStatement -> Text
extractLicenseStatementLabel (FactStatement a _ _) = getStatementLabel a

type Statements
  = Vector FactStatement

type LicenseName
  = String
class (Show a, ToJSON a) => LFRaw a where
  getLicenseFactClassifier :: a -> LicenseFactClassifier
  getImpliedNames          :: a -> [LicenseName]
  getImpliedStatements     :: a -> Vector (LicenseFactClassifier -> FactStatement)
  getImpliedStatements _ = V.empty
  computeImpliedStatements :: a -> Vector FactStatement
  computeImpliedStatements a = let
      thunks = getImpliedStatements a
    in V.map (\t -> t (getLicenseFactClassifier a)) thunks

newtype LicenseFactClassifier
  = LFC [Text]
  deriving (Eq, Generic)
instance Show LicenseFactClassifier where
  show (LFC brc) = T.unpack $ T.intercalate "/" brc
instance ToJSON LicenseFactClassifier where
  toJSON lfc = toJSON $ show lfc

data LicenseFact
  = forall a. (LFRaw a) => LicenseFact String a
  | forall a. (LFRaw a) => LicenseFactWithoutURL a
extractLicenseFactClassifier :: LicenseFact -> LicenseFactClassifier
extractLicenseFactClassifier (LicenseFact _ a)         = getLicenseFactClassifier a
extractLicenseFactClassifier (LicenseFactWithoutURL a) = getLicenseFactClassifier a

instance Show LicenseFact where
  show (LicenseFact _ a) = show a
  show (LicenseFactWithoutURL a) = show a
instance ToJSON LicenseFact where
  toJSON (LicenseFact url a) = let
      lfc = getLicenseFactClassifier a
    in object [ tShow lfc .= (mergeAesonL [toJSON a
                                          , object [ "_sourceURL" .= (toJSON url) ]]) ]
  toJSON (LicenseFactWithoutURL a) = let
      lfc = getLicenseFactClassifier a
    in object [ tShow lfc .= (toJSON a) ]
instance LFRaw LicenseFact where
  getLicenseFactClassifier (LicenseFact _ raw)         = getLicenseFactClassifier raw
  getLicenseFactClassifier (LicenseFactWithoutURL raw) = getLicenseFactClassifier raw
  getImpliedNames (LicenseFact _ raw)                  = getImpliedNames raw
  getImpliedNames (LicenseFactWithoutURL raw)          = getImpliedNames raw
  getImpliedStatements (LicenseFact _ raw)             = getImpliedStatements raw
  getImpliedStatements (LicenseFactWithoutURL raw)     = getImpliedStatements raw

type Facts
  = Vector LicenseFact
