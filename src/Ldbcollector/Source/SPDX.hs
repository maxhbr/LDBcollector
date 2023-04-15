{-# LANGUAGE TemplateHaskell #-}
{-# LANGUAGE OverloadedStrings #-}
module Ldbcollector.Source.SPDX
  ( SPDXData (..)
  ) where

import           Ldbcollector.Model

import qualified Data.Vector             as V

data SPDXCrossRef
    = SPDXCrossRef
    { _match :: String
    , _url :: String
    , _isValid :: Bool
    , _isLive :: Bool
    , _timestamp :: String
    , _isWayBackLink :: Bool
    , _order :: Int
    }
    deriving (Eq, Ord)
$(deriveJSON defaultOptions{fieldLabelModifier = drop 1, constructorTagModifier = map toLower} ''SPDXCrossRef)

data SPDXLicense
    = SPDXLicense
    { _licenseId :: LicenseName
    , _name :: LicenseName
    , _isDeprecatedLicenseId :: Bool
    , _licenseComments :: Maybe Text
    , _crossRef :: [SPDXCrossRef]
    , _seeAlso :: [String]
    , _isFsfLibre :: Maybe Bool
    , _isOsiApproved :: Bool
    , _standardLicenseTemplate :: Text
    , _licenseText :: Text
    , _licenseTextHtml :: Text
    }
    deriving (Eq, Ord)
$(deriveJSON defaultOptions{fieldLabelModifier = drop 1, constructorTagModifier = map toLower} ''SPDXLicense)

getUrls :: SPDXLicense -> [String]
getUrls lic = map _url (_crossRef lic) ++ _seeAlso lic


instance LicenseFactC SPDXLicense where
    getType _            = "SPDXLicense"
    getApplicableLNs lic = LN (_licenseId lic) `AlternativeLNs` [LN (_name lic)]
    getImpliedStmts lic  =
        [ ifToStmt (show (_licenseId lic) ++ " is a deprecated LicenseId") (_isDeprecatedLicenseId lic)
        , case _isFsfLibre lic of
            Just True -> LicenseRating "FSF" (PositiveLicenseRating "Libre" Nothing) 
            Just False -> LicenseRating "FSF" (NegativeLicenseRating "Not-Libre" Nothing) 
            _ -> noStmt
        , LicenseRating "OSI" $ if _isOsiApproved lic
                                then PositiveLicenseRating "Approved" Nothing
                                else NeutralLicenseRating "not-Approved" Nothing
        , maybe noStmt LicenseComment (_licenseComments lic)
        , LicenseText (_licenseText lic) `SubStatements` [LicenseText (_licenseTextHtml lic)]
        ] ++ map LicenseUrl (getUrls lic)

newtype SPDXData = SPDXData FilePath

instance Source SPDXData where
    getSource _  = Source "SPDX"
    getFacts (SPDXData jsonDetailsDir) = let
            parseOrFailJson json = do
                logFileReadIO json
                decoded <- eitherDecodeFileStrict json :: IO (Either String SPDXLicense)
                case decoded of
                    Left err  -> fail err
                    Right lic -> return lic 
            setLicenseIdNS lic@(SPDXLicense{_licenseId = lid}) = lic{_licenseId = setNS "spdx" lid}
        in do
            licenseJsons <- glob (jsonDetailsDir </> "*.json")
            licenses <- mapM (fmap setLicenseIdNS . parseOrFailJson) licenseJsons
            (return . V.fromList) (wrapFacts licenses)
