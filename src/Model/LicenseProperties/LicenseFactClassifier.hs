{-# LANGUAGE ExistentialQuantification #-}
{-# LANGUAGE TypeFamilies #-}
{-# LANGUAGE GADTs #-}
{-# LANGUAGE OverloadedStrings #-}
{-#LANGUAGE DeriveGeneric #-}
{-#LANGUAGE StandaloneDeriving #-}
module Model.LicenseProperties.LicenseFactClassifier
    where

import qualified Prelude as P
import           MyPrelude

import qualified Data.Text as T
import qualified Text.Pandoc as P
import qualified Text.Pandoc.Builder as P

import           Model.LicenseProperties.Base

data LicenseFactClassifier
  = EmptyLFC
  | LFC Text
  | LFCWithURL URL Text
  deriving (Generic)
extractBrc :: LicenseFactClassifier -> Text
extractBrc (EmptyLFC)         = ""
extractBrc (LFC brc)          = brc
extractBrc (LFCWithURL _ brc) = brc
instance Eq LicenseFactClassifier where
  lfc1 == lfc2 = extractBrc lfc1 == extractBrc lfc2
instance Show LicenseFactClassifier where
  show = T.unpack . extractBrc
instance Ord LicenseFactClassifier where
  compare lfc1 lfc2 = compare (show lfc1) (show lfc2)
instance ToJSON LicenseFactClassifier where
  toJSON lfc = toJSON $ show lfc
instance ToJSONKey LicenseFactClassifier

instance Inlineable LicenseFactClassifier where
  toInline lfc@(LFC _)            = P.text (show lfc)
  toInline lfc@(LFCWithURL url _) = P.link url (show lfc) (P.text (show lfc))

maybeAddUrl :: Maybe URL -> LicenseFactClassifier -> LicenseFactClassifier
maybeAddUrl Nothing lfc            = lfc
maybeAddUrl _ lfc@(LFCWithURL _ _) = lfc
maybeAddUrl (Just url) (LFC brc)   = LFCWithURL url brc
