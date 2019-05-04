{-# LANGUAGE ExistentialQuantification #-}
{-# LANGUAGE TypeFamilies #-}
{-# LANGUAGE GADTs #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE DeriveGeneric #-}
module Model.Fact
  ( LicenseName
  , LicenseFactClassifier (..)
  , LFRaw (..)
  , LicenseFact (..)
  , LicenseStatementType
  , FSRaw (..)
  , FactStatement (..)
  , Facts
  ) where

import qualified Prelude as P
import           MyPrelude

import qualified Data.Text as T
import qualified Data.Vector as V
import qualified Data.ByteString.Lazy as B



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
  = forall a. (LFRaw a)
  => LicenseFact a
instance Show LicenseFact where
  show (LicenseFact a) = show a
instance ToJSON LicenseFact where
  toJSON (LicenseFact a) = let
      lfc = getLicenseFactClassifier a
    in object [ tShow lfc .= toJSON a ]
instance LFRaw LicenseFact where
  getLicenseFactClassifier (LicenseFact raw) = getLicenseFactClassifier raw
  getImpliedNames (LicenseFact raw)          = getImpliedNames raw
  getImpliedStatements (LicenseFact raw)     = getImpliedStatements raw

type Facts
  = Vector LicenseFact
