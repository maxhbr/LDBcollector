{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE TemplateHaskell #-}

module Ldbcollector.Source.BlueOak
  ( BlueOakCouncil (..),
  )
where

import Data.ByteString qualified
import Data.ByteString.Lazy (ByteString)
import Data.ByteString.Lazy qualified as B
import Data.Map qualified as M
import Data.Vector qualified as V
import Ldbcollector.Model
import MyPrelude

data BlueOakLicense = BlueOakLicense
  { _name :: String,
    _id :: String,
    _url :: Maybe String
  }
  deriving (Eq, Show, Ord, Generic)

instance FromJSON BlueOakLicense where
  parseJSON = withObject "BlueOakLicense" $ \v ->
    BlueOakLicense
      <$> v .: "name"
      <*> v .: "id"
      <*> v .:? "url"

instance ToJSON BlueOakLicense

-- #############################################################################
-- #  permissive  ##############################################################
-- #############################################################################

data BlueOakRating = BlueOakRating
  { _rating :: String,
    _notes :: Text,
    _licenses :: [BlueOakLicense]
  }
  deriving (Show, Generic)

instance FromJSON BlueOakRating where
  parseJSON = withObject "BlueOakRating" $ \v ->
    BlueOakRating
      <$> v .: "name"
      <*> v .: "notes"
      <*> v .: "licenses"

data BlueOakData = BlueOakData
  { _version :: String,
    _ratings :: [BlueOakRating]
  }
  deriving (Show, Generic)

instance FromJSON BlueOakData where
  parseJSON = withObject "BlueOakData" $ \v ->
    BlueOakData
      <$> v .: "version"
      <*> v .: "ratings"

-- #############################################################################
-- #  copyleft  ################################################################
-- #############################################################################

data BlueOakCopyleftGroup = BlueOakCopyleftGroup
  { _bocgName :: String,
    _versions :: [BlueOakLicense]
  }
  deriving (Show, Generic)

instance FromJSON BlueOakCopyleftGroup where
  parseJSON = withObject "BlueOakCopyleftGroup" $ \v ->
    BlueOakCopyleftGroup
      <$> v .: "name"
      <*> v .: "versions"

data BlueOakCopyleftData = BlueOakCopyleftData
  { _bocgVersion :: String,
    _families :: Map String [BlueOakCopyleftGroup]
  }
  deriving (Show, Generic)

instance FromJSON BlueOakCopyleftData where
  parseJSON = withObject "BlueOakCopyleftData" $ \v ->
    BlueOakCopyleftData
      <$> v .: "version"
      <*> v .: "families"

-- #############################################################################
-- #  facts  ###################################################################
-- #############################################################################

data BlueOakCouncilFact
  = BOCPermissive String Text BlueOakLicense
  | BOCCopyleft String String BlueOakLicense
  deriving (Eq, Show, Ord, Generic)

instance ToJSON BlueOakCouncilFact

permissiveToFacts :: BlueOakData -> [BlueOakCouncilFact]
permissiveToFacts (BlueOakData _ ratings) =
  concatMap (\(BlueOakRating rating notes licenses) -> map (BOCPermissive rating notes) licenses) ratings

copyleftToFacts :: BlueOakCopyleftData -> [BlueOakCouncilFact]
copyleftToFacts (BlueOakCopyleftData _ families) =
  concatMap (\(kind, groups) -> concatMap (\(BlueOakCopyleftGroup name versions) -> map (BOCCopyleft kind name) versions) groups) $ M.assocs families

alnFromBol :: BlueOakLicense -> ApplicableLNs
alnFromBol (BlueOakLicense name id _) =
  (LN . newNLN "BlueOak" . pack) id
    `AlternativeLNs` [ (LN . newLN . pack) name
                     ]

getImpliedStmtsOfBOL :: BlueOakLicense -> [LicenseStatement]
getImpliedStmtsOfBOL (BlueOakLicense {_url = Just url}) = [LicenseUrl Nothing url]
getImpliedStmtsOfBOL _ = []

instance LicenseFactC BlueOakCouncilFact where
  getType _ = "BlueOakCouncil"
  getApplicableLNs (BOCPermissive _ _ bol) = alnFromBol bol
  getApplicableLNs (BOCCopyleft _ kind bol) = alnFromBol bol `ImpreciseLNs` [(LN . newLN . pack) kind]
  getImpliedStmts a@(BOCPermissive rating notes bol) =
    let boRatingToStatement = case strToLower rating of
          "gold" -> LicenseRating $ PositiveLicenseRating (ScopedLicenseTag (getType a) "Gold" $ LicenseTagDescription notes)
          "silver" -> LicenseRating $ PositiveLicenseRating (ScopedLicenseTag (getType a) "Silver" $ LicenseTagDescription notes)
          "bronze" -> LicenseRating $ NeutralLicenseRating (ScopedLicenseTag (getType a) "Bronze" $ LicenseTagDescription notes)
          "lead" -> LicenseRating $ NegativeLicenseRating (ScopedLicenseTag (getType a) "Lead" $ LicenseTagDescription notes)
          _ -> LicenseTag $ (ScopedLicenseTag (getType a) (fromString rating) NoLicenseTagText)
     in [typeStmt "Permissive", boRatingToStatement] ++ getImpliedStmtsOfBOL bol
  getImpliedStmts (BOCCopyleft kind _ bol) = (typeStmt kind `SubStatements` [typeStmt "Copyleft"]) : getImpliedStmtsOfBOL bol

-- #############################################################################
-- #  general  #################################################################
-- #############################################################################

data BlueOakCouncil
  = BlueOakCouncilLicenseList FilePath
  | BlueOakCouncilCopyleftList FilePath

instance HasOriginalData BlueOakCouncil where
  getOriginalData (boc) =
    FromUrl "https://blueoakcouncil.org/" $
      case boc of
        (BlueOakCouncilLicenseList file) ->
          FromUrl "https://blueoakcouncil.org/list.json" $
            FromFile file NoPreservedOriginalData
        (BlueOakCouncilCopyleftList file) ->
          FromUrl "https://blueoakcouncil.org/copyleft.json" $
            FromFile file NoPreservedOriginalData

instance Source BlueOakCouncil where
  getSource _ = Source "BlueOakCouncil"
  getFacts (BlueOakCouncilLicenseList file) = do
    logFileReadIO file
    decoded <- eitherDecodeFileStrict file :: IO (Either String BlueOakData)
    case decoded of
      Left err -> fail err
      Right bod -> return . V.fromList . map wrapFact $ permissiveToFacts bod
  getFacts (BlueOakCouncilCopyleftList file) = do
    logFileReadIO file
    decoded <- eitherDecodeFileStrict file :: IO (Either String BlueOakCopyleftData)
    case decoded of
      Left err -> fail err
      Right bocd -> return . V.fromList . map wrapFact $ copyleftToFacts bocd
