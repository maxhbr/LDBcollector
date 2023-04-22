{-# LANGUAGE DeriveGeneric     #-}
{-# LANGUAGE OverloadedStrings #-}
module Ldbcollector.Source.Scancode
  ( ScancodeLicenseDB (..)
  ) where

import           Ldbcollector.Model    hiding (ByteString)

import           Data.ByteString       (ByteString)
import qualified Data.ByteString.Char8 as Char8
import qualified Data.Vector           as V

data ScancodeData
  = ScancodeData
  { _key         :: !String
  , _shortName   :: !String
  , _name        :: !String
  , _category    :: Maybe String
  , _spdxId      :: Maybe String
  , _owner       :: Maybe String
  , _homepageUrl :: Maybe String
  , _notes       :: Maybe Text
  , _textUrls    :: [String]
  , _osiUrl      :: Maybe String
  , _otherUrls   :: [String]
  , _text        :: Maybe Text
  } deriving (Eq, Ord, Show, Generic)
instance FromJSON ScancodeData where
  parseJSON = withObject "ScancodeData" $ \v -> ScancodeData
    <$> v .: "key"
    <*> v .: "short_name"
    <*> v .: "name"
    <*> v .:? "category"
    <*> v .:? "spdx_license_key"
    <*> v .:? "owner"
    <*> v .:? "homepage_url"
    <*> v .:? "notes"
    <*> v .:? "text_urls" .!= []
    <*> v .:? "osi_url"
    <*> v .:? "other_urls" .!= []
    <*> v .:? "text"
instance ToJSON ScancodeData

instance LicenseFactC ScancodeData where
    getType _ = "ScancodeData"
    getApplicableLNs scd = (LN . newNLN "scancode" . pack . _key) scd `AlternativeLNs`
                                [ (LN . newLN . pack . _shortName) scd
                                , (LN . newLN . pack . _name) scd
                                ]
    getImpliedStmts scd = case _category scd of
                            Just category -> [typestmt category]
                            _             -> []
                          ++ map mstmt [ _homepageUrl scd
                                       , _osiUrl scd
                                       ]
                          ++ maybeToList (fmap LicenseComment (_notes scd))
                          ++ maybeToList (fmap LicenseUrl (_osiUrl scd))
                          ++ map LicenseUrl (_textUrls scd)
                          ++ map LicenseUrl (_otherUrls scd)
                          ++ maybeToList (fmap LicenseText (_text scd))

newtype ScancodeLicenseDB = ScancodeLicenseDB FilePath

instance HasOriginalData ScancodeLicenseDB where
    getOriginalData (ScancodeLicenseDB dir) = 
        FromUrl "https://scancode-licensedb.aboutcode.org/" $
        FromUrl "https://github.com/nexB/scancode-licensedb" $
        FromFile dir NoPreservedOriginalData
instance Source ScancodeLicenseDB where
    getSource _  = Source "ScancodeLicenseDB"
    getFacts (ScancodeLicenseDB dir) = let
            parseOrFailJson json = do
                logFileReadIO json
                decoded <- eitherDecodeFileStrict json :: IO (Either String ScancodeData)
                case decoded of
                    Left err           -> fail err
                    Right scancodeData -> return scancodeData
        in do
            scancodeJsons <- (fmap (filter (not . isSuffixOf "index.json")) . glob) (dir </> "*.json")
            scancodeDatas <- mapM parseOrFailJson scancodeJsons
            (return . V.fromList) (wrapFacts scancodeDatas)

