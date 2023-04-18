{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE TemplateHaskell #-}
module Ldbcollector.Source.GoogleLicensePolicy
  ( GoogleLicensePolicy(..)
  )
  where

import           Ldbcollector.Model

import           Data.Aeson
import           Data.Aeson.Encode.Pretty   (encodePretty)
import           Data.Aeson.Types           (Parser)
import qualified Data.ByteString
import qualified Data.ByteString.Lazy       as B
import qualified Data.ByteString.Lazy.Char8 as Char8
import qualified Data.Char                  as Char
import qualified Data.Csv                   as C
import           Data.FileEmbed             (embedFile)
import           Data.Map                   (Map)
import qualified Data.Map                   as Map
import           Data.Maybe                 (catMaybes, maybeToList)
import           Data.Set                   (Set)
import qualified Data.Set                   as S
import qualified Data.Text                  as T
import qualified Data.Vector                as V
import           Network.URI                (parseURI)
import qualified Text.Blaze.Html5           as H

data GoogleLicenseType
    = GoogleLicenseType
    { _description :: Text
    , _licenses :: [String]
    }
$(deriveJSON defaultOptions{fieldLabelModifier = drop 1, constructorTagModifier = map toLower} ''GoogleLicenseType)
data GoogleLicensePolicyJson
    = GoogleLicensePolicyJson
    { _canonical_names :: Map.Map String String
    , _types :: Map.Map Text GoogleLicenseType
    }
$(deriveJSON defaultOptions{fieldLabelModifier = drop 1, constructorTagModifier = map toLower} ''GoogleLicensePolicyJson)
data GoogleLicense
    = GoogleLicense
    { googleLicenseName :: LicenseName 
    , spdxLicenseName :: Maybe LicenseName
    , googleLicenseType :: Text
    , googleLicenseTypeDescription :: Text
    } deriving (Show, Eq, Ord, Generic)
instance ToJSON GoogleLicense

toFacts :: GoogleLicensePolicyJson -> [GoogleLicense]
toFacts (GoogleLicensePolicyJson canonical_names types) = let
        canonicalize :: String -> Maybe LicenseName
        canonicalize = fmap (setNS "spdx" . fromString) . (`Map.lookup` canonical_names)
    in concatMap (\(ty,GoogleLicenseType desc lics) -> 
            map (\lic -> 
                    GoogleLicense ((setNS "google" . fromString) lic) (canonicalize lic) ty desc
                ) lics
        ) (Map.assocs types)

instance LicenseFactC GoogleLicense where
    getType _ = "GoogleLicense"
    getApplicableLNs (GoogleLicense gln sln _ _) = LN gln `AlternativeLNs` (map LN . maybeToList) sln
    getImpliedStmts (GoogleLicense _ _ ty desc) = case ty of
        "restricted"        -> [LicenseRating (NegativeLicenseRating "Google Policy Classification" ty (Just desc))]
        "reciprocal"        -> [LicenseRating (NeutralLicenseRating  "Google Policy Classification" ty (Just desc))]
        "notice"            -> [LicenseRating (PositiveLicenseRating "Google Policy Classification" ty (Just desc))]
        "permissive"        -> [LicenseRating (PositiveLicenseRating "Google Policy Classification" ty (Just desc))]
        "unencumbered"      -> [LicenseRating (PositiveLicenseRating "Google Policy Classification" ty (Just desc))]
        "by_exception_only" -> [LicenseRating (NegativeLicenseRating "Google Policy Classification" ty (Just desc))]
        _                   -> []

newtype GoogleLicensePolicy = GoogleLicensePolicy FilePath
instance Source GoogleLicensePolicy where
    getSource _  = Source "GoogleLicensePolicy"
    getFacts (GoogleLicensePolicy json) = do
        logFileReadIO json
        decoded <- eitherDecodeFileStrict json :: IO (Either String GoogleLicensePolicyJson)
        case decoded of
            Left err -> fail err
            Right m  ->  (return . V.fromList . map wrapFact . toFacts) m