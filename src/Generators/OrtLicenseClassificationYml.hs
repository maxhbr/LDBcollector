{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE LambdaCase #-}
module Generators.OrtLicenseClassificationYml
    ( writeOrtLicenseClassificationYml
    ) where


import qualified Prelude as P
import           MyPrelude

import qualified Data.ByteString.Lazy as BL
import           Data.Aeson.Encode.Pretty (encodePretty)
import qualified Data.Yaml as Y

import           Model.License
import           Processors.ToPage (Page (..), LicenseDetails (..), unpackWithSource)

-- categories:
-- - name: "copyleft"
-- - name: "strong-copyleft"
-- - name: "copyleft-limited"
-- - name: "permissive"
--   description: "Licenses with permissive obligations."
-- - name: "public-domain"
-- - name: "include-in-notice-file"
--   description: >-
--     This category is checked by templates used by the ORT report generator. The licenses associated with this
--     category are included into NOTICE files.
-- - name: "include-source-code-offer-in-notice-file"
--   description: >-
--     A marker category that indicates that the licenses assigned to it require that the source code of the packages
--     needs to be provided.
--
-- categorizations:
-- - id: "AGPL-1.0"
--   categories:
--   - "copyleft"
--   - "include-in-notice-file"
--   - "include-source-code-offer-in-notice-file"
-- - id: "AGPL-1.0-only"
--   categories:
--   - "copyleft"
--   - "include-in-notice-file"
--   - "include-source-code-offer-in-notice-file"
-- - id: "AGPL-1.0-or-later"
--   categories:
--   - "copyleft"
--   - "include-in-notice-file"
--   - "include-source-code-offer-in-notice-file"
-- [..]

type OLCY_Category_Name = String
data OLCY_Category
  = OLCY_Category
  { _OLCY_Category_name :: OLCY_Category_Name
  , _OLCY_Category_description :: Maybe String
  } deriving (Eq, Show)
instance ToJSON OLCY_Category where
  toJSON a = Y.object ( [ "name" Y..= Y.toJSON (_OLCY_Category_name a)
                        ] ++ (case _OLCY_Category_description a of
                                Just d -> [  "categories" Y..= Y.toJSON d ]
                                Nothing -> []
                                ))
data OLCY_Categorization
  = OLCY_Categorization
  { _OLCY_Category_id :: LicenseName
  , _OLCY_Category_categories :: [OLCY_Category]
  } deriving (Eq, Show)
instance ToJSON OLCY_Categorization where
  toJSON a = Y.object [ "id" Y..= Y.toJSON (_OLCY_Category_id a)
                      , "categories" Y..= Y.toJSON (map _OLCY_Category_name (_OLCY_Category_categories a))
                      ]
data OrtLicenseClassificationYml
  = OrtLicenseClassificationYml
  { _OLCY_categories      :: [OLCY_Category]
  , _OLCY_categorizations :: [OLCY_Categorization]
  } deriving (Eq, Show)
instance ToJSON OrtLicenseClassificationYml where
  toJSON a = Y.object [ "categories" Y..= Y.toJSON (_OLCY_categories a)
                      , "categorizations" Y..= Y.toJSON (_OLCY_categorizations a)
                      ]

copyleftKindToCategoryName :: CopyleftKind -> OLCY_Category_Name
copyleftKindToCategoryName StrongCopyleft  = "strong-copyleft"
copyleftKindToCategoryName WeakCopyleft    = "weak-copyleft"
copyleftKindToCategoryName SaaSCopyleft    = "saas-copyleft"
copyleftKindToCategoryName MaximalCopyleft = "maximal-copyleft"
copyleftKindToCategoryName Copyleft        = "copyleft"
copyleftKindToCategoryName MaybeCopyleft   = "maybe-copyleft"
copyleftKindToCategoryName NoCopyleft      = "permissive"
copyleftKindToCategory :: CopyleftKind -> [OLCY_Category]
copyleftKindToCategory ck@StrongCopyleft  =
  [ OLCY_Category (copyleftKindToCategoryName ck) Nothing
  ] ++ copyleftKindToCategory Copyleft
copyleftKindToCategory ck@WeakCopyleft    =
  [ OLCY_Category (copyleftKindToCategoryName ck) Nothing
  ] ++ copyleftKindToCategory Copyleft
copyleftKindToCategory ck@SaaSCopyleft    =
  [ OLCY_Category (copyleftKindToCategoryName ck) Nothing
  ] ++ copyleftKindToCategory Copyleft
copyleftKindToCategory ck@MaximalCopyleft =
  [ OLCY_Category (copyleftKindToCategoryName ck) Nothing
  ] ++ copyleftKindToCategory Copyleft
copyleftKindToCategory ck@Copyleft        =
  [ OLCY_Category (copyleftKindToCategoryName ck) Nothing
  ]
copyleftKindToCategory ck@MaybeCopyleft   =
  [ OLCY_Category (copyleftKindToCategoryName ck) Nothing
  ]
copyleftKindToCategory ck@NoCopyleft      =
  [ OLCY_Category (copyleftKindToCategoryName ck) Nothing
  ]

hasPatentHintCategory = OLCY_Category "has-patent-hint" Nothing
hasNoPatentHintCategory = OLCY_Category "has-no-patent-hint" Nothing

nonCommercialCategory = OLCY_Category "non-commercial" Nothing
nonNonCommercialCategory = OLCY_Category "allows-commercial" Nothing

ratingToCategoryName :: Rating -> [OLCY_Category_Name]
ratingToCategoryName (RUnknown rs) = map (\r -> "maybe-rating:" ++ (show r)) rs
ratingToCategoryName r             = ["rating:" ++ (show r)]
ratingToCategory :: Rating -> [OLCY_Category]
ratingToCategory r = map (`OLCY_Category` Nothing) (ratingToCategoryName r)

  -- = ImpliedRight String
  -- | ImpliedRightWithDesc String String
  -- = ImpliedCondition String
  -- | ImpliedConditionWithDesc String String
  -- = ImpliedLimitation String
  -- | ImpliedLimitationWithDesc String String
licenseObligationsToCategory :: LicenseObligations -> [OLCY_Category]
licenseObligationsToCategory (LicenseObligations irs ics ils) =
  (map (\case
           ImpliedRight r -> OLCY_Category ("right:" ++ r) Nothing
           ImpliedRightWithDesc r d -> OLCY_Category ("right:" ++ r) (Just d)
           ) irs)
  ++ (map (\case
           ImpliedCondition r -> OLCY_Category ("condition:" ++ r) Nothing
           ImpliedConditionWithDesc r d -> OLCY_Category ("condition:" ++ r) (Just d)
           ) ics)
  ++ (map (\case
           ImpliedLimitation r -> OLCY_Category ("limitation:" ++ r) Nothing
           ImpliedLimitationWithDesc r d -> OLCY_Category ("limitation:" ++ r) (Just d)
           ) ils)

categories :: [OLCY_Category]
categories = nub $ concat
  -- Copyleft Kind
  [ copyleftKindToCategory StrongCopyleft
  , copyleftKindToCategory WeakCopyleft
  , copyleftKindToCategory SaaSCopyleft
  , copyleftKindToCategory MaximalCopyleft
  , copyleftKindToCategory Copyleft
  , copyleftKindToCategory MaybeCopyleft
  , copyleftKindToCategory NoCopyleft
  -- Patent Hint
  , [ hasPatentHintCategory , hasNoPatentHintCategory ]
  -- Non Commercial
  , [ nonCommercialCategory , nonNonCommercialCategory ]
  ]

pageToCategorization :: Page -> OLCY_Categorization
pageToCategorization page = let
  licenseDetails = pLicenseDetails page
  categorizationsFromCopyleft = case ldCopyleft licenseDetails of
    Just ck -> copyleftKindToCategory ck
    Nothing -> []
  categorizationsFromHasPatentHint = case ldHasPatentHint licenseDetails of
    Just True  -> [hasPatentHintCategory]
    Just False -> [hasNoPatentHintCategory]
    Nothing    -> []
  categorizationsFromNonCommercial = case ldNonCommercial licenseDetails of
    Just True  -> [nonCommercialCategory]
    Just False -> [nonNonCommercialCategory]
    Nothing -> []
  categorizationsFromRating = ratingToCategory (ldRating licenseDetails)
  categorizationsFromObligations = case pObligations page of
    Just ows -> licenseObligationsToCategory (unpackWithSource ows)
    Nothing -> []
  in OLCY_Categorization (ldShortname licenseDetails)
  ( categorizationsFromCopyleft
  ++ categorizationsFromNonCommercial
  ++ categorizationsFromHasPatentHint
  ++ categorizationsFromRating
  ++ categorizationsFromObligations
  )

writeOrtLicenseClassificationYml :: FilePath -> [Page] -> IO ()
writeOrtLicenseClassificationYml  outputFolder pages = let
  categorizations = map pageToCategorization pages
  allCategories = nub (categories ++ concatMap _OLCY_Category_categories categorizations)
  ortLicenseClassificationYml = OrtLicenseClassificationYml allCategories categorizations
  in do
    createDirectoryIfNotExists (outputFolder </> "ort")
    Y.encodeFile (outputFolder </> "ort" </> "license-classifications.yml") ortLicenseClassificationYml
