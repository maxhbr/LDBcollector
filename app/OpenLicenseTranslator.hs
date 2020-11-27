{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE QuasiQuotes #-}
{-# LANGUAGE TemplateHaskell #-}
module OpenLicenseTranslator
  ( writeTranslate
  )where

import qualified Prelude as P
import           MyPrelude

import           Control.Monad
import           Data.Aeson
import qualified Data.Vector as V
import           GHC.IO.Encoding
import           System.Environment
import qualified Data.ByteString.Lazy as BL
import qualified Data.Csv as C
import           Network.Curl

import           Debug.Trace (trace)

import Lib
import Configuration (configuration)
import Comparator

-- https://www.deepl.com/docs-api/translating-text/request/

-- Example Request
-- curl https://api.deepl.com/v2/translate \
-- 	-d auth_key=$key \
-- 	-d "text=Hello, world"  \
-- 	-d "target_lang=DE"
-- Example Response
-- {
-- 	"translations": [{
-- 		"detected_source_language":"EN",
-- 		"text":"Hallo, Welt!"
-- 	}]
-- }


-- "{\"translations\":[{\"detected_source_language\":\"JA\",\"text\":\"Documentation accompanying the software should be treated in the same way as the software.\"}]}"
data TranslationsEntry
  = TranslationsEntry (Maybe String) String
  deriving (Show)
instance FromJSON TranslationsEntry where
  parseJSON = withObject "TranslationsEntry" $ \v -> TranslationsEntry
    <$> v .:? "detected_source_language"
    <*> v .: "text"
data Translations
  = Translations [TranslationsEntry]
  deriving (Show)
instance FromJSON Translations where
  parseJSON = withObject "Translations" $ \v -> Translations
    <$> v .: "translations"

parseJsonResponse :: ByteString -> Maybe String
parseJsonResponse json = case (decode json :: Maybe Translations) of
  Just (Translations [])                       -> Nothing
  Just (Translations [TranslationsEntry _ en]) -> Just en
  _                                            -> undefined

getTranslation :: String -> TranslationRow -> IO TranslationRow
getTranslation apiKey tr@(TranslationRow ja "") =
  do
    putStrLn $ "Do Request for: " ++ (take 20 ja)
    resp <- curlGetResponse_ "https://api.deepl.com/v2/translate" [CurlPostFields ["auth_key=" ++ apiKey, "text=" ++ ja, "source_lang=JA", "target_lang=EN"]] :: IO (CurlResponse_  [(String, String)] ByteString)
    case respCurlCode resp of
      CurlOK -> case parseJsonResponse (respBody resp) of
        Just en -> return (TranslationRow ja en)
        _       -> do
          putStrLn ("Request parsing failed")
          return tr
      _      -> do
        putStrLn ("Request failed with " ++ (show $ respCurlCode resp))
        return tr
getTranslation _ tr                          =
  return tr

{-
 - a hack used to write translation tables for open-license
 -}
writeTranslate :: String -> IO ()
writeTranslate apiKey = do
  let translateables = loadOpenLicenseTranslateables
  translateables' <- mapM (getTranslation apiKey) translateables
  BL.writeFile "data/hitachi-open-license/translations.csv" (C.encodeDefaultOrderedByName translateables')
