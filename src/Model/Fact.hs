{-# LANGUAGE ExistentialQuantification #-}
{-# LANGUAGE TypeFamilies #-}
{-# LANGUAGE GADTs #-}
{-# LANGUAGE OverloadedStrings #-}
module Model.Fact
  ( LFData (..)
  , LicenseShortname
  , LFRaw (..)
  , LicenseFactClassifier
  , LicenseFact (..)
  , mkLicenseFact
  , defaultLicenseFactScope
  , Facts
  ) where

import           Data.List (intersect)
import qualified Data.Text as T
import           Data.Text (Text)
import qualified Data.Vector as V
import           Data.Vector (Vector)
import           Text.JSON hiding (encode)
import           Data.Aeson
import qualified Data.ByteString.Lazy as B
import           Data.ByteString.Lazy (ByteString)

data LFData
  = LFnone
  | LFjson (JSObject JSValue)
  | LFtext Text
  | LFbytestring ByteString
  | LFstring String
  deriving (Show, Eq)

type LicenseShortname
  = String
class (Show a, ToJSON a) => LFRaw a where
  getImpliedShortnames :: a -> [LicenseShortname]
  getParsedData        :: a -> LFData
  getParsedData = LFbytestring . encode
  getType              :: a -> String

type LicenseFactClassifier
  = ( String -- Scope
    , String -- Type
    )

data LicenseFact
  = forall a. (LFRaw a) => LicenseFact
  { _licenseFactClassifier :: LicenseFactClassifier
  , _rawLicenseFactData    :: a
  , _licenseFactData       :: !LFData
  }
instance ToJSON LicenseFact where
  toJSON lf@(LicenseFact _ a _) = let
      (c,t) = _licenseFactClassifier lf
      key = T.pack $ if c == defaultLicenseFactScope
        then t
        else (c ++ ":" ++ t)
    in object [ key .= toJSON a ]
instance LFRaw LicenseFact where
  getImpliedShortnames (LicenseFact _ raw _) = getImpliedShortnames raw
  getParsedData (LicenseFact _ _ parsed)     = parsed
  getType       (LicenseFact _ raw _)        = getType raw

mkLicenseFact :: (LFRaw a) =>
                 String -> a -> LicenseFact
mkLicenseFact lfScope raw = LicenseFact (lfScope, getType raw) raw (getParsedData raw)

defaultLicenseFactScope :: String
defaultLicenseFactScope = "<default>"

instance Show LicenseFact where
  show (LicenseFact (s, t) _ d) = "* " ++ s ++ ":" ++ t ++ "\n" ++ show d

type Facts
  = Vector LicenseFact
