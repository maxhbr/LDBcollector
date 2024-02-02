{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE TemplateHaskell #-}

module Ldbcollector.Source.FossLicense
  ( FossLicenseVar (..),
  )
where

import Data.Aeson
import Data.Aeson.Encode.Pretty (encodePretty)
import Data.Aeson.Types (Parser)
import Data.ByteString qualified
import Data.ByteString.Lazy qualified as B
import Data.ByteString.Lazy.Char8 qualified as Char8
import Data.Char qualified as Char
import Data.Map (Map)
import Data.Map qualified as Map
import Data.Maybe (catMaybes, maybeToList)
import Data.Set (Set)
import Data.Set qualified as S
import Data.Text qualified as T
import Data.Text.IO qualified as T
import Data.Vector qualified as V
import Ldbcollector.Model

data FossLicenseMeta = FossLicenseMeta
  { _disclaimer :: Text,
    _comment :: Text
  }
  deriving (Show, Eq, Ord, Generic)

$(deriveJSON defaultOptions {fieldLabelModifier = drop 1, constructorTagModifier = map toLower} ''FossLicenseMeta)

data FossLicense = FossLicense
  { _meta :: FossLicenseMeta,
    _name :: Text,
    _scancode_key :: Text,
    _spdxid :: Text,
    _aliases :: [Text],
    _text :: Maybe Text
  } deriving (Show, Eq, Ord, Generic)

$(deriveJSON defaultOptions {fieldLabelModifier = drop 1, constructorTagModifier = map toLower} ''FossLicense)

-- data FossLicense = FossLicense
--   { _fljson :: FossLicenseJson
--   , _fltext :: Text
--   }
-- instance ToJSON FossLicense

-- toFacts :: GoogleLicensePolicyJson -> [GoogleLicense]
-- toFacts (GoogleLicensePolicyJson canonical_names types) =
--   let canonicalize :: String -> Maybe LicenseName
--       canonicalize = fmap (setNS "spdx" . fromString) . (`Map.lookup` canonical_names)
--    in concatMap
--         ( \(ty, GoogleLicenseType desc lics) ->
--             map
--               ( \lic ->
--                   GoogleLicense ((setNS "google" . fromString) lic) (canonicalize lic) ty desc
--               )
--               lics
--         )
--         (Map.assocs types)

instance LicenseFactC FossLicense where
  getType _ = "FossLicense"
  getApplicableLNs fl = let
          flln = LN $ newNLN "foss-license" (_name fl)
          scln = LN $ newNLN "scancode" (_scancode_key fl)
          aliaslns = map (LN . newLN) (_aliases fl)
      in flln `AlternativeLNs` (scln : aliaslns)
  getImpliedLicenseTexts (FossLicense _ _ _ _ _ (Just text)) = [text]
  getImpliedLicenseTexts _ = []

newtype FossLicenseVar = FossLicenseVar FilePath

instance HasOriginalData FossLicenseVar where
  getOriginalData (FossLicenseVar _) =
    FromUrl "https://github.com/hesa/foss-licenses/" $
      FromUrl "https://github.com/hesa/foss-licenses/tree/main/var/licenses" $
        NoPreservedOriginalData

instance Source FossLicenseVar where
    getSource _ = Source "FOSS License"
    getFacts (FossLicenseVar var) =
        let parseOrFailJson json = do
              logFileReadIO json
              decoded <- eitherDecodeFileStrict json :: IO (Either String FossLicense)
              case decoded of
                Left err -> fail err
                Right fossLicense -> do
                    text <- T.readFile (json -<.> "LICENSE")
                    return (fossLicense {_text = Just text})
         in do
              let varLicenses = var </> "licenses"
              jsonFiles <- glob (varLicenses </> "*.json")
              jsons <- mapM parseOrFailJson jsonFiles
              return ((V.fromList . map wrapFact) jsons)
              

              -- -- for each .json file in var/licenses, parse it and return a FossLicense
              -- mapM (getFacts . FossLicense) =<< do
              --   files <- listDirectory varLicenses
              --   forM files $ \file -> do
              --     let json = varLicenses </> file


              -- logFileReadIO json
              -- decoded <- eitherDecodeFileStrict json :: IO (Either String FossLicenseJson)
              -- case decoded of
              --   Left err -> fail err
              --   Right m -> (return . V.fromList . map wrapFact . toFacts) m


-- instance Source GoogleLicensePolicy where
--   getSource _ = Source "GoogleLicensePolicy"
--   getFacts (GoogleLicensePolicy json) = do
--     logFileReadIO json
--     decoded <- eitherDecodeFileStrict json :: IO (Either String GoogleLicensePolicyJson)
--     case decoded of
--       Left err -> fail err
--       Right m -> (return . V.fromList . map wrapFact . toFacts) m
