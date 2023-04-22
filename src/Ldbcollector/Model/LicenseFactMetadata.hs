{-# LANGUAGE DefaultSignatures #-}
{-# LANGUAGE GADTs             #-}
{-# LANGUAGE LambdaCase        #-}
{-# LANGUAGE OverloadedStrings #-}
module Ldbcollector.Model.LicenseFactMetadata
  ( OriginalData (..)
  , originallyFromUrl
  , getOriginalDataText
  , getOriginalDataUrl
  , HasOriginalData (..)
--   , LicenseFactMetadata (..)
  ) where

import           MyPrelude                           hiding (ByteString)

import qualified Crypto.Hash.MD5                     as MD5
import           Data.Aeson                          as A
import           Data.ByteString                     (ByteString)
import qualified Data.ByteString.Base16              as B16
import qualified Data.ByteString.Lazy.Char8          as C
import qualified Data.ByteString.Lazy          as BL
import qualified Data.Map                            as Map
import qualified Data.Vector                         as V
import qualified Data.Text.Encoding            as Enc

import           Ldbcollector.Model.LicenseName
import           Ldbcollector.Model.LicenseStatement
import qualified Text.Blaze                          as H
import qualified Text.Blaze.Html5                    as H
import qualified Text.Blaze.Html5.Attributes   as A
import Text.Blaze (ToMarkup)


data OriginalData
    = OriginalBSData ByteString
    | OriginalJsonData A.Value
    | OriginalTextData Text
    | FromFile FilePath OriginalData
    | FromUrl String OriginalData
    | NoPreservedOriginalData
    deriving (Eq)
originallyFromUrl :: String -> OriginalData
originallyFromUrl = (`FromUrl` NoPreservedOriginalData)
instance ToJSON OriginalData where
    toJSON (OriginalBSData bs) = toJSON $ bsToText bs
    toJSON (OriginalJsonData v) = v
    toJSON (OriginalTextData t) = toJSON t
    toJSON (FromFile fn od) = object [ "fileName" .= fn
                                     , "content" .= od
                                     ]
    toJSON (FromUrl url od) = object [ "url" .= url
                                     , "content" .= od
                                     ]
    toJSON NoPreservedOriginalData = object []
instance ToMarkup OriginalData where
    toMarkup (OriginalBSData bs)  = H.ul . H.li $ H.toMarkup $ bsToText bs
    toMarkup (OriginalJsonData v) = H.ul . H.li $ H.pre (H.toMarkup (bsToText (BL.toStrict (encodePretty v))))
    toMarkup (OriginalTextData t) = H.ul . H.li $ H.toMarkup t
    toMarkup (FromFile fn od)     = H.ul . H.li $ do
        H.toMarkup fn
        H.toMarkup od
    toMarkup (FromUrl url od)     = H.ul . H.li $ do
        H.a H.! A.href (H.toValue url) $ H.toMarkup url
        H.toMarkup od
    toMarkup NoPreservedOriginalData = mempty
getOriginalDataText :: OriginalData -> Maybe Text
getOriginalDataText (OriginalBSData bs) = (Just . bsToText) bs
getOriginalDataText (OriginalJsonData _) = Nothing
getOriginalDataText (OriginalTextData t) = Just t
getOriginalDataText (FromFile _ od) = getOriginalDataText od
getOriginalDataText (FromUrl _ od) = getOriginalDataText od
getOriginalDataText _ = Nothing
getOriginalDataUrl :: OriginalData -> Maybe String
getOriginalDataUrl (FromUrl url _) = Just url
getOriginalDataUrl (FromFile _ od) = getOriginalDataUrl od
getOriginalDataUrl _ = Nothing

class HasOriginalData a where
    getOriginalData :: a -> OriginalData
    getOriginalData _ = NoPreservedOriginalData

-- data LicenseFactMetadata
--     = LicenseFactMetadata
--     { lfmUrl :: Maybe String
--     , lfmOriginalData :: OriginalData
--     }