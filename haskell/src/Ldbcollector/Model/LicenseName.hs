{-# LANGUAGE OverloadedStrings #-}
module Ldbcollector.Model.LicenseName
  ( LicenseName
  , newLN, newNLN
  ) where

import           Data.Text as T
import           MyPrelude

data LicenseName where
    LicenseName :: Maybe Text -> Text -> LicenseName
newLN :: Text -> LicenseName
newLN = LicenseName Nothing

newNLN :: Text -> Text -> LicenseName
newNLN ns = LicenseName (Just ns)

licenseNameToText :: LicenseName -> Text
licenseNameToText (LicenseName Nothing ln)   = ln
licenseNameToText (LicenseName (Just ns) ln) = ns <> ":" <> ln

instance Eq LicenseName where
    (==) x y = toCaseFold (licenseNameToText x) == toCaseFold (licenseNameToText y)

instance Ord LicenseName where
    compare x y = compare (toCaseFold (licenseNameToText x)) (toCaseFold (licenseNameToText y))

instance Show LicenseName where
    show = unpack . licenseNameToText
