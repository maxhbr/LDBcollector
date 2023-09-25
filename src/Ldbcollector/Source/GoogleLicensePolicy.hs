{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE TemplateHaskell #-}

module Ldbcollector.Source.GoogleLicensePolicy
  ( GoogleLicensePolicy (..),
  )
where

import Data.Aeson
import Data.Aeson.Encode.Pretty (encodePretty)
import Data.Aeson.Types (Parser)
import Data.ByteString qualified
import Data.ByteString.Lazy qualified as B
import Data.ByteString.Lazy.Char8 qualified as Char8
import Data.Char qualified as Char
import Data.Csv qualified as C
import Data.FileEmbed (embedFile)
import Data.Map (Map)
import Data.Map qualified as Map
import Data.Maybe (catMaybes, maybeToList)
import Data.Set (Set)
import Data.Set qualified as S
import Data.Text qualified as T
import Data.Vector qualified as V
import Ldbcollector.Model
import Network.URI (parseURI)
import Text.Blaze.Html5 qualified as H

data GoogleLicenseType = GoogleLicenseType
  { _description :: Text,
    _licenses :: [String]
  }

$(deriveJSON defaultOptions {fieldLabelModifier = drop 1, constructorTagModifier = map toLower} ''GoogleLicenseType)

data GoogleLicensePolicyJson = GoogleLicensePolicyJson
  { _canonical_names :: Map.Map String String,
    _types :: Map.Map Text GoogleLicenseType
  }

$(deriveJSON defaultOptions {fieldLabelModifier = drop 1, constructorTagModifier = map toLower} ''GoogleLicensePolicyJson)

data GoogleLicense = GoogleLicense
  { googleLicenseName :: LicenseName,
    spdxLicenseName :: Maybe LicenseName,
    googleLicenseType :: Text,
    googleLicenseTypeDescription :: Text
  }
  deriving (Show, Eq, Ord, Generic)

instance ToJSON GoogleLicense

toFacts :: GoogleLicensePolicyJson -> [GoogleLicense]
toFacts (GoogleLicensePolicyJson canonical_names types) =
  let canonicalize :: String -> Maybe LicenseName
      canonicalize = fmap (setNS "spdx" . fromString) . (`Map.lookup` canonical_names)
   in concatMap
        ( \(ty, GoogleLicenseType desc lics) ->
            map
              ( \lic ->
                  GoogleLicense ((setNS "google" . fromString) lic) (canonicalize lic) ty desc
              )
              lics
        )
        (Map.assocs types)

instance LicenseFactC GoogleLicense where
  getType _ = "GoogleLicense"
  getApplicableLNs (GoogleLicense gln sln _ _) = LN gln `AlternativeLNs` (map LN . maybeToList) sln
  getImpliedStmts (GoogleLicense _ _ ty desc) = case ty of
    "restricted" -> [LicenseRating (NegativeLicenseRating "Google Policy Classification" ty (LicenseRatingDescription desc))]
    "reciprocal" -> [LicenseRating (NeutralLicenseRating "Google Policy Classification" ty (LicenseRatingDescription desc))]
    "notice" -> [LicenseRating (PositiveLicenseRating "Google Policy Classification" ty (LicenseRatingDescription desc))]
    "permissive" -> [LicenseRating (PositiveLicenseRating "Google Policy Classification" ty (LicenseRatingDescription desc))]
    "unencumbered" -> [LicenseRating (PositiveLicenseRating "Google Policy Classification" ty (LicenseRatingDescription desc))]
    "by_exception_only" -> [LicenseRating (NegativeLicenseRating "Google Policy Classification" ty (LicenseRatingDescription desc))]
    _ -> []

newtype GoogleLicensePolicy = GoogleLicensePolicy FilePath

instance HasOriginalData GoogleLicensePolicy where
  getOriginalData (GoogleLicensePolicy json) =
    FromUrl "https://opensource.google/documentation/reference/thirdparty/licenses" $
      FromUrl "https://github.com/google/licenseclassifier/blob/main/license_type.go" $
        FromFile json NoPreservedOriginalData

instance Source GoogleLicensePolicy where
  getSource _ = Source "GoogleLicensePolicy"
  getFacts (GoogleLicensePolicy json) = do
    logFileReadIO json
    decoded <- eitherDecodeFileStrict json :: IO (Either String GoogleLicensePolicyJson)
    case decoded of
      Left err -> fail err
      Right m -> (return . V.fromList . map wrapFact . toFacts) m
