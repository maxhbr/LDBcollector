{-# LANGUAGE CPP #-}
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
import qualified Data.Hashable.Class.Hashable (Hashable)

import           Model.LicenseProperties.Base

{- #############################################################################
 - LicenseFactLicense
 -}
data LicenseFactLicense
  = EmptyLFL
  | LFL LicenseName
  | LFLWithURL URL LicenseName
  deriving (Generic)
instance Show LicenseFactLicense where
  show EmptyLFL = ""
  show (LFL name) = name
  show (LFLWithURL url name) = name ++ " (" ++ url ++ ")"
instance ToJSON LicenseFactLicense
instance ToJSONKey LicenseFactLicense

instance Inlineable LicenseFactLicense where
  toInline EmptyLFL              = mempty
  toInline (LFL name)            = P.text name
  toInline (LFLWithURL url name) = P.link url name (P.text name)

{- #############################################################################
 - LicenseFactClassifier
 -}
data LicenseFactClassifier
  = EmptyLFC
  | LFC Text
  | LFCWithURL URL Text
  | LFCWithLicense LicenseFactLicense Text
  | LFCWithURLAndLicense URL LicenseFactLicense Text
  deriving (Generic)
extractBrc :: LicenseFactClassifier -> Text
extractBrc EmptyLFC                       = ""
extractBrc (LFC brc)                      = brc
extractBrc (LFCWithURL _ brc)             = brc
extractBrc (LFCWithLicense _ brc)         = brc
extractBrc (LFCWithURLAndLicense _ _ brc) = brc
extractLFL :: LicenseFactClassifier -> LicenseFactLicense
extractLFL (LFCWithLicense lfl _)         = lfl
extractLFL (LFCWithURLAndLicense _ lfl _) = lfl
extractLFL _                              = EmptyLFL
instance Eq LicenseFactClassifier where
  lfc1 == lfc2 = extractBrc lfc1 == extractBrc lfc2
instance Show LicenseFactClassifier where
  show = T.unpack . extractBrc
instance Ord LicenseFactClassifier where
  compare lfc1 lfc2 = compare (show lfc1) (show lfc2)
instance ToJSON LicenseFactClassifier where
  toJSON lfc = toJSON $ show lfc
instance ToJSONKey LicenseFactClassifier
instance Hashable LicenseFactClassifier

urlify :: URL -> String -> Inlines
urlify url text = P.link url text (P.text text)
licensify :: Inlineable a =>  LicenseFactLicense -> a -> Inlines
#if true
licensify _ inl = toInline inl
#else
licensify lic inl = toInline inl <> P.space <> P.text "(" <> toInline lic <> P.text ")"
#endif

instance Inlineable LicenseFactClassifier where
  toInline EmptyLFC                           = mempty
  toInline lfc@(LFC _)                        = P.text (show lfc)
  toInline lfc@(LFCWithURL url _)             = urlify url (show lfc)
  toInline (LFCWithLicense lic brc)           = licensify lic (LFC brc)
  toInline (LFCWithURLAndLicense url lic brc) = licensify lic (LFCWithURL url brc)

maybeAddUrl :: Maybe URL -> LicenseFactClassifier -> LicenseFactClassifier
maybeAddUrl _ EmptyLFC                          = EmptyLFC
maybeAddUrl Nothing lfc                         = lfc
maybeAddUrl _ lfc@LFCWithURL {}                 = lfc
maybeAddUrl _ lfc@LFCWithURLAndLicense {}       = lfc
maybeAddUrl (Just url) (LFC brc)                = LFCWithURL url brc
maybeAddUrl (Just url) (LFCWithLicense lfl brc) = LFCWithURLAndLicense url lfl brc

maybeAddLicense :: Maybe LicenseFactLicense -> LicenseFactClassifier -> LicenseFactClassifier
maybeAddLicense _ EmptyLFC                      = EmptyLFC
maybeAddLicense Nothing lfc                     = lfc
maybeAddLicense _ lfc@LFCWithLicense {}         = lfc
maybeAddLicense _ lfc@LFCWithURLAndLicense {}   = lfc
maybeAddLicense (Just lfl) (LFC brc)            = LFCWithLicense lfl brc
maybeAddLicense (Just lfl) (LFCWithURL url brc) = LFCWithURLAndLicense url lfl brc

{- #############################################################################
 - WithSource
 -}
class LicenseFactClassifiable a where
  getLicenseFactClassifier :: a -> LicenseFactClassifier
getLicenseFactLicense :: LicenseFactClassifiable a => a -> LicenseFactLicense
getLicenseFactLicense = extractLFL . getLicenseFactClassifier
