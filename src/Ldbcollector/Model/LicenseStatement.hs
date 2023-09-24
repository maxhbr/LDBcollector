{-# LANGUAGE OverloadedStrings #-}

module Ldbcollector.Model.LicenseStatement where

import Ldbcollector.Model.LicenseName
import MyPrelude
import Text.Blaze qualified as H
import Text.Blaze.Html5 qualified as H
import Text.Blaze.Html5.Attributes qualified as A

data PCLR = PCLR
  { _permissions :: [Text],
    _conditions :: [Text],
    _limitations :: [Text],
    _restrictions :: [Text]
  }
  deriving (Eq, Show, Ord, Generic)

instance ToJSON PCLR

data LicenseCompatibility = LicenseCompatibility
  { _other :: LicenseName,
    _compatibility :: String,
    _explanation :: Text
  }
  deriving (Eq, Show, Ord, Generic)

instance ToJSON LicenseCompatibility

data LicenseType
  = PublicDomain
  | Permissive
  | Copyleft
  | WeaklyProtective
  | StronglyProtective
  | NetworkProtective
  | UnknownLicenseType (Maybe String)
  | Proprietary
  | ProprietaryFree
  | Unlicensed
  deriving (Eq, Show, Ord, Generic)

instance ToJSON LicenseType

instance IsString LicenseType where
  fromString str =
    let lowerStr = map toLower str
        mapping =
          [ ("PublicDomain", PublicDomain),
            ("Public Domain", PublicDomain),
            ("Permissive", Permissive),
            ("Copyleft", Copyleft),
            ("WeaklyProtective", WeaklyProtective),
            ("Weakly Protective", WeaklyProtective),
            ("weak_copyleft", WeaklyProtective),
            ("weak", WeaklyProtective),
            ("strong_copyleft", StronglyProtective),
            ("StronglyProtective", StronglyProtective),
            ("Strongly Protective", StronglyProtective),
            ("strong", StronglyProtective),
            ("NetworkProtective", NetworkProtective),
            ("Network Protective", NetworkProtective),
            ("network_copyleft", NetworkProtective),
            ("network", NetworkProtective),
            ("Unlicensed", Unlicensed),
            ("Proprietary", Proprietary),
            ("ProprietaryFree", ProprietaryFree),
            ("proprietary_free", ProprietaryFree),
            ("Unknown", UnknownLicenseType Nothing)
          ]
     in case find (\(n, _) -> map toLower n == lowerStr) mapping of
          Just (_, a) -> a
          Nothing -> UnknownLicenseType (Just str)

class ToLicenseType a where
  toLicenseType :: a -> LicenseType

instance ToLicenseType String where
  toLicenseType = fromString

data LicenseRating
  = PositiveLicenseRating String Text (Maybe Text)
  | NeutralLicenseRating String Text (Maybe Text)
  | NegativeLicenseRating String Text (Maybe Text)
  deriving (Eq, Show, Ord, Generic)

instance ToJSON LicenseRating

getRatingNamespace :: LicenseRating -> String
getRatingNamespace (PositiveLicenseRating ns _ _) = ns
getRatingNamespace (NeutralLicenseRating ns _ _) = ns
getRatingNamespace (NegativeLicenseRating ns _ _) = ns

unLicenseRating :: LicenseRating -> Text
unLicenseRating (PositiveLicenseRating _ r _) = r
unLicenseRating (NeutralLicenseRating _ r _) = r
unLicenseRating (NegativeLicenseRating _ r _) = r

getRatingDescription :: LicenseRating -> Maybe Text
getRatingDescription (PositiveLicenseRating _ _ (Just desc)) = Just desc
getRatingDescription (NeutralLicenseRating _ _ (Just desc)) = Just desc
getRatingDescription (NegativeLicenseRating _ _ (Just desc)) = Just desc
getRatingDescription _ = Nothing

instance H.ToMarkup LicenseRating where
  toMarkup r =
    let ns = getRatingNamespace r
        rating = unLicenseRating r
        color = case r of
          PositiveLicenseRating {} -> "color: green;"
          NeutralLicenseRating {} -> ""
          NegativeLicenseRating {} -> "color: red;"
     in do
          H.toMarkup ns
          ": "
          H.b H.! A.style color $ H.toMarkup rating
          case getRatingDescription r of
            (Just description) -> do
              H.br
              H.toMarkup description
            _ -> pure ()

data LicenseStatement where
  LicenseStatement :: String -> LicenseStatement
  LicenseType :: LicenseType -> LicenseStatement
  LicenseRating :: LicenseRating -> LicenseStatement
  LicenseComment :: Text -> LicenseStatement
  LicenseUrl :: String -> LicenseStatement
  LicenseText :: Text -> LicenseStatement
  LicenseRule :: Text -> LicenseStatement
  LicensePCLR :: PCLR -> LicenseStatement
  LicenseCompatibilities :: [LicenseCompatibility] -> LicenseStatement
  SubStatements :: LicenseStatement -> [LicenseStatement] -> LicenseStatement
  MaybeStatement :: Maybe LicenseStatement -> LicenseStatement
  deriving (Eq, Show, Ord, Generic)

instance ToJSON LicenseStatement

instance IsString LicenseStatement where
  fromString = LicenseStatement

noStmt :: LicenseStatement
noStmt = MaybeStatement Nothing

stmt :: String -> LicenseStatement
stmt = fromString

mstmt :: Maybe String -> LicenseStatement
mstmt = MaybeStatement . fmap fromString

typestmt :: String -> LicenseStatement
typestmt = LicenseType . fromString

ifToStmt :: String -> Bool -> LicenseStatement
ifToStmt stmt True = LicenseStatement stmt
ifToStmt _ False = noStmt

filterStatement :: LicenseStatement -> Maybe LicenseStatement
filterStatement (LicenseComment "") = Nothing
filterStatement (LicenseStatement "") = Nothing
filterStatement (LicenseUrl "") = Nothing
filterStatement (LicenseText "") = Nothing
filterStatement (LicenseRule "") = Nothing
filterStatement (LicenseCompatibilities []) = Nothing
filterStatement (SubStatements stmt substmts) =
  case filterStatements substmts of
    [] -> filterStatement stmt
    filtered -> case filterStatement stmt of
      Just fStmt -> Just $ SubStatements fStmt filtered
      Nothing -> Just $ SubStatements stmt filtered -- TODO
filterStatement (MaybeStatement Nothing) = Nothing
filterStatement (MaybeStatement (Just stmt)) = filterStatement stmt
filterStatement stmt = Just stmt

filterStatements :: [LicenseStatement] -> [LicenseStatement]
filterStatements = mapMaybe filterStatement

flattenStatements :: [LicenseStatement] -> [LicenseStatement]
flattenStatements =
  let flattenStatements' (SubStatements stmt substmts) = flattenStatements' stmt ++ concatMap flattenStatements' substmts
      flattenStatements' stmt = [stmt]
   in filterStatements . concatMap flattenStatements'
