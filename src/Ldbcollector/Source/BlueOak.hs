{-# LANGUAGE DeriveGeneric     #-}
{-# LANGUAGE LambdaCase        #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE TemplateHaskell   #-}
module Ldbcollector.Source.BlueOak
  ( BlueOakCouncil (..)
  ) where

import           Ldbcollector.Model
import           MyPrelude

import qualified Data.ByteString
import           Data.ByteString.Lazy (ByteString)
import qualified Data.ByteString.Lazy as B
import qualified Data.Map             as M
import qualified Data.Vector          as V


data BlueOakLicense
 = BlueOakLicense
 { _name :: String
 , _id   :: String
 , _url  :: String
 } deriving (Eq,Show,Ord,Generic)
instance FromJSON BlueOakLicense where
  parseJSON = withObject "BlueOakLicense" $ \v -> BlueOakLicense
    <$> v .: "name"
    <*> v .: "id"
    <*> v .: "url"
instance ToJSON BlueOakLicense

-- #############################################################################
-- #  permissive  ##############################################################
-- #############################################################################

data BlueOakRating
 = BlueOakRating
 { _rating   :: String
 , _licenses :: [BlueOakLicense]
 } deriving (Show,Generic)
instance FromJSON BlueOakRating where
  parseJSON = withObject "BlueOakRating" $ \v -> BlueOakRating
    <$> v .: "name"
    <*> v .: "licenses"

data BlueOakData
  = BlueOakData
  { _version :: String
  , _ratings :: [BlueOakRating]
  } deriving (Show,Generic)
instance FromJSON BlueOakData where
  parseJSON = withObject "BlueOakData" $ \v -> BlueOakData
    <$> v .: "version"
    <*> v .: "ratings"

-- #############################################################################
-- #  copyleft  ################################################################
-- #############################################################################

data BlueOakCopyleftGroup
  = BlueOakCopyleftGroup
  { _bocgName :: String
  , _versions :: [BlueOakLicense]
  } deriving (Show,Generic)
instance FromJSON BlueOakCopyleftGroup where
  parseJSON = withObject "BlueOakCopyleftGroup" $ \v -> BlueOakCopyleftGroup
    <$> v .: "name"
    <*> v .: "versions"
data BlueOakCopyleftData
  = BlueOakCopyleftData
  { _bocgVersion :: String
  , _families    :: Map String [BlueOakCopyleftGroup]
  } deriving (Show,Generic)
instance FromJSON BlueOakCopyleftData where
  parseJSON = withObject "BlueOakCopyleftData" $ \v -> BlueOakCopyleftData
    <$> v .: "version"
    <*> v .: "families"

-- #############################################################################
-- #  facts  ###################################################################
-- #############################################################################

data BlueOakCouncilFact
    = BOCPermissive String BlueOakLicense
    | BOCCopyleft String String BlueOakLicense
    deriving (Eq, Show, Ord, Generic)
instance ToJSON BlueOakCouncilFact
permissiveToFacts :: BlueOakData -> [BlueOakCouncilFact]
permissiveToFacts (BlueOakData _ ratings) =
    concatMap (\(BlueOakRating rating licenses) -> map (BOCPermissive rating) licenses) ratings
copyleftToFacts :: BlueOakCopyleftData -> [BlueOakCouncilFact]
copyleftToFacts (BlueOakCopyleftData _ families) =
    concatMap (\(kind, groups) -> concatMap (\(BlueOakCopyleftGroup name versions) -> map (BOCCopyleft kind name) versions) groups) $ M.assocs families

alnFromBol :: BlueOakLicense -> ApplicableLNs
alnFromBol (BlueOakLicense name id _) = (NLN . newNLN "BlueOak" . pack) id `AlternativeLNs`
                                                [ (LN . newLN . pack) name
                                                ]

instance LicenseFactC BlueOakCouncilFact where
    getType _ = "BlueOakCouncil"
    getApplicableLNs (BOCPermissive _ bol) = alnFromBol bol
    getApplicableLNs (BOCCopyleft _ kind bol) = alnFromBol bol `ImpreciseLNs` [(LN . newLN . pack) kind]
    getImpliedStmts (BOCPermissive rating bol) = [stmt "Permissive", stmt rating]
    getImpliedStmts (BOCCopyleft kind _ bol) = [stmt kind `SubStatements` [stmt "Copyleft"]]


-- #############################################################################
-- #  general  #################################################################
-- #############################################################################

data BlueOakCouncil
     = BlueOakCouncilLicenseList FilePath
     | BlueOakCouncilCopyleftList FilePath

instance Source BlueOakCouncil where
    getOrigin _  = Origin "BlueOakCouncil"
    getFacts (BlueOakCouncilLicenseList file) = do
        logFileReadIO file
        decoded <- eitherDecodeFileStrict file :: IO (Either String BlueOakData)
        case decoded of
            Left err  -> fail err
            Right bod -> return . V.fromList . map wrapFact $ permissiveToFacts bod
    getFacts (BlueOakCouncilCopyleftList file) = do
        logFileReadIO file
        decoded <- eitherDecodeFileStrict file :: IO (Either String BlueOakCopyleftData)
        case decoded of
            Left err   -> fail err
            Right bocd -> return . V.fromList . map wrapFact $ copyleftToFacts bocd
