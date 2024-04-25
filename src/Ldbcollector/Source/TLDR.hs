{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE DeriveGeneric #-}
module Ldbcollector.Source.TLDR
  ( TLDRLicenseNamings (..),
  )
where

import Ldbcollector.Model
import Data.Aeson.Types (Parser)
import Data.ByteString.Lazy qualified as B
import Data.ByteString.Lazy.Char8 qualified as Char8
import Data.Char qualified as Char
import Data.Csv qualified as C
import Data.Vector qualified as V

data TLDRLicenseNaming = TLDRLicenseNaming
  { _id :: String
  , _shorthand :: Maybe LicenseName
  , _slug :: LicenseName
  , _title :: LicenseName
  }
  deriving (Generic, Eq, Show)
instance ToJSON TLDRLicenseNaming

instance C.FromNamedRecord TLDRLicenseNaming where
  parseNamedRecord r =
    TLDRLicenseNaming
      <$> r C..: "_id"
      <*> ((\case 
                "" -> Nothing
                shorthand -> Just $ newNLN "tldr" shorthand)  <$> r C..: "shorthand")
      <*> ((newNLN "tldr-slug") <$> r C..: "slug")
      <*> ((newNLN "tldr-title") <$> r C..: "title")

instance LicenseFactC TLDRLicenseNaming where
  getType _ = "TLDRNaming"
  getApplicableLNs (TLDRLicenseNaming id shorthand slug title) =
    case shorthand of
      Just shorthand -> (LN shorthand) `AlternativeLNs` [LN slug, LN title]
      Nothing -> (LN title) `AlternativeLNs` [LN slug]
  getImpliedStmts (TLDRLicenseNaming _ _ (LicenseName _ slug) _) =
    [LicenseUrl (Just "TLDR") $ "https://tldrlegal.com/license/" <> unpack slug]

data TLDRLicenseNamings = TLDRLicenseNamings FilePath

instance HasOriginalData TLDRLicenseNamings where
  getOriginalData (TLDRLicenseNamings csv) = FromFile csv NoPreservedOriginalData

instance Source TLDRLicenseNamings where
  getSource _ = Source "TLDRNamings"
  getFacts (TLDRLicenseNamings csv) = do
      csvContent <- B.readFile csv
      let rows = case (C.decodeByName csvContent :: Either String (C.Header, V.Vector TLDRLicenseNaming)) of
                          Right (_, rows) -> rows
                          Left err -> V.empty
      return (wrapFactV rows)
