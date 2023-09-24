{-# LANGUAGE OverloadedStrings #-}

module Ldbcollector.Model.LicenseName
  ( LicenseName (..),
    newLN,
    newNLN,
    setNS,
    unsetNS,
    fromText,
    LicenseNameRelation (..),
  )
where

import Data.String (IsString (..))
import Data.Text as T
import MyPrelude
import Text.Blaze qualified as H

data LicenseName where
  LicenseName :: Maybe Text -> Text -> LicenseName

-- LicenseFullName :: LicenseName -> LicenseName
-- LicenseShortName :: LicenseName -> LicenseName
newLN :: Text -> LicenseName
newLN = LicenseName Nothing

newNLN :: Text -> Text -> LicenseName
newNLN ns = LicenseName (Just ns)

setNS :: Text -> LicenseName -> LicenseName
setNS ns (LicenseName _ n) = LicenseName (Just ns) n

unsetNS :: LicenseName -> LicenseName
unsetNS (LicenseName _ n) = LicenseName Nothing n

licenseNameToText :: LicenseName -> Text
licenseNameToText (LicenseName Nothing ln) = ln
licenseNameToText (LicenseName (Just ns) ln) = ns <> ":" <> ln

instance Eq LicenseName where
  (==) x y = toCaseFold (licenseNameToText x) == toCaseFold (licenseNameToText y)

instance Ord LicenseName where
  compare x y = compare (toCaseFold (licenseNameToText x)) (toCaseFold (licenseNameToText y))

instance Show LicenseName where
  show = unpack . licenseNameToText

fromText :: Text -> LicenseName
fromText t = case T.splitOn ":" t of
  [] -> undefined
  [ln] -> LicenseName Nothing ln
  ns : lns -> LicenseName (Just ns) (T.intercalate ":" lns)

instance IsString LicenseName where
  fromString = fromText . T.pack

instance FromJSON LicenseName where
  parseJSON = withText "LicenseName" $ return . fromString . unpack

instance ToJSON LicenseName where
  toJSON = String . pack . show

instance H.ToMarkup LicenseName where
  toMarkup = H.toMarkup . show

data LicenseNameRelation where
  Same :: LicenseNameRelation
  Better :: LicenseNameRelation
  SupersededBy :: LicenseNameRelation
  -- Potentially  :: LicenseNameRelation -> LicenseNameRelation
  deriving (Show, Eq, Ord)
