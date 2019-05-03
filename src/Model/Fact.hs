{-# LANGUAGE ExistentialQuantification #-}
{-# LANGUAGE TypeFamilies #-}
{-# LANGUAGE GADTs #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE DeriveGeneric #-}
module Model.Fact
  ( LFData (..)
  , LicenseName
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
  getStatementDescription :: a -> Maybe Text
  getStatementDescription _ = Nothing
  unRawStatement :: LicenseFactClassifier -> a -> FactStatement
  unRawStatement = FactStatement

data FactStatement
  = forall a. (FSRaw a)
  => FactStatement
  {_factSourceClassifier :: LicenseFactClassifier
  , _rawFactStatement :: a
  }
instance ToJSON FactStatement where
  toJSON (FactStatement lfc a) = let
      lbl = getStatementLabel a
      desc = getStatementDescription a
      val = getStatementContent a
    in object [ tShow lfc .= object [ lbl .= val
                                    , "description" .= desc ] ]

data LFData
  = LFnone
  | LFtext Text
  | LFbytestring ByteString
  | LFstring String
  deriving (Show, Eq)

type LicenseName
  = String
class (Show a, ToJSON a) => LFRaw a where
  getLicenseFactClassifier :: a -> LicenseFactClassifier
  getImpliedNames          :: a -> [LicenseName]
  getImpliedStatements     :: a -> Vector FactStatement
  getImpliedStatements _ = V.empty

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
