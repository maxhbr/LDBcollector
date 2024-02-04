{-# LANGUAGE OverloadedStrings #-}

module Ldbcollector.Model.LicenseStatement where

import Ldbcollector.Model.LicenseName
import MyPrelude
import Text.Blaze qualified as H
import Text.Blaze.Html5 qualified as H
import Text.Blaze.Html5.Attributes qualified as A
import Data.Text qualified as T

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

instance H.ToMarkup LicenseType where
  toMarkup = H.toMarkup . show

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

data LicenseTagText
  = NoLicenseTagText
  | LicenseTagDescription Text
  | LicenseTagReason Text
  | LicenseTagReasonWithDescription Text Text
  deriving (Eq, Show, Ord, Generic)
instance ToJSON LicenseTagText

data LicenseTag
  = ScopedLicenseTag String Text LicenseTagText
  | UnscopedLicenseTag Text LicenseTagText
  deriving (Eq, Show, Ord, Generic)
instance ToJSON LicenseTag

getTagNamespace :: LicenseTag -> Maybe String
getTagNamespace (ScopedLicenseTag ns _ _) = Just ns
getTagNamespace _ = Nothing

unLicenseTag :: LicenseTag -> Text
unLicenseTag (ScopedLicenseTag _ r _) = r
unLicenseTag (UnscopedLicenseTag r _) = r

getTagDescription :: LicenseTag -> Maybe Text
getTagDescription (ScopedLicenseTag _ _ (LicenseTagDescription desc)) = Just desc
getTagDescription (ScopedLicenseTag _ _ (LicenseTagReasonWithDescription _ desc)) = Just desc
getTagDescription (UnscopedLicenseTag _ (LicenseTagDescription desc)) = Just desc
getTagDescription (UnscopedLicenseTag _ (LicenseTagReasonWithDescription _ desc)) = Just desc
getTagDescription _ = Nothing

getTagReason :: LicenseTag -> Maybe Text
getTagReason (ScopedLicenseTag _ _ (LicenseTagReason reason)) = Just reason
getTagReason (ScopedLicenseTag _ _ (LicenseTagReasonWithDescription reason _)) = Just reason
getTagReason (UnscopedLicenseTag _ (LicenseTagReason reason)) = Just reason
getTagReason (UnscopedLicenseTag _ (LicenseTagReasonWithDescription reason _)) = Just reason
getTagReason _ = Nothing

instance H.ToMarkup LicenseTag where
  toMarkup r =
    let mNs = getTagNamespace r
        rating = unLicenseTag r
        desc = case getTagDescription r of
            Just desc' -> H.toValue desc'
            _ -> ""
     in do
          H.div H.! A.title desc $ do
            case mNs of
                Just ns -> do
                    H.toMarkup ns
                    ": "
                _ -> return ()
            H.b $ H.toMarkup rating
            case getTagReason r of
              (Just reason) -> do
                H.br
                H.toMarkup reason
              _ -> pure ()

data LicenseRating
  = PositiveLicenseRating LicenseTag
  | NeutralLicenseRating LicenseTag
  | NegativeLicenseRating LicenseTag
  deriving (Eq, Show, Ord, Generic)
instance ToJSON LicenseRating

tagFromLicenseRating :: LicenseRating -> LicenseTag
tagFromLicenseRating (PositiveLicenseRating t) = t
tagFromLicenseRating (NeutralLicenseRating t) = t
tagFromLicenseRating (NegativeLicenseRating t) = t

getRatingNamespace :: LicenseRating -> Maybe String
getRatingNamespace = getTagNamespace . tagFromLicenseRating

unLicenseRating :: LicenseRating -> Text
unLicenseRating = unLicenseTag . tagFromLicenseRating

getRatingDescription :: LicenseRating -> Maybe Text
getRatingDescription = getTagDescription . tagFromLicenseRating

getRatingReason :: LicenseRating -> Maybe Text
getRatingReason = getTagReason . tagFromLicenseRating

instance H.ToMarkup LicenseRating where
  toMarkup r =
    let mNs = getRatingNamespace r
        rating = unLicenseRating r
        color = case r of
          PositiveLicenseRating {} -> "color: green;"
          NeutralLicenseRating {} -> ""
          NegativeLicenseRating {} -> "color: red;"
        desc = case getRatingDescription r of
            Just desc' -> H.toValue desc'
            _ -> ""
     in do
          H.span H.! A.title desc $ do
            case mNs of
                Just ns -> do
                    H.toMarkup ns
                    ": "
                _ -> return ()
            H.b H.! A.style color $ H.toMarkup rating
            case getRatingReason r of
              (Just reason) -> do
                H.br
                H.toMarkup reason
              _ -> pure ()

data LicenseComment
  = UnscopedLicenseComment Text
  | ScopedLicenseComment String Text
  deriving (Eq, Ord, Generic)
instance Show LicenseComment where
    show (UnscopedLicenseComment comment) = T.unpack comment
    show (ScopedLicenseComment scope comment) = scope ++ ": " ++ T.unpack comment
instance ToJSON LicenseComment

isEmptyLicenseComment :: LicenseComment -> Bool
isEmptyLicenseComment (UnscopedLicenseComment "") = True
isEmptyLicenseComment (ScopedLicenseComment _ "") = True
isEmptyLicenseComment _ = False

instance H.ToMarkup LicenseComment where
  toMarkup (UnscopedLicenseComment comment) = do
    H.toMarkup comment
  toMarkup (ScopedLicenseComment scope comment) = do
    H.b $ do
      H.toMarkup scope
      ": "
    H.toMarkup comment

data LicenseStatement where
  LicenseStatement :: String -> LicenseStatement
  LicenseType :: LicenseType -> LicenseStatement
  LicenseTag :: LicenseTag -> LicenseStatement
  LicenseRating :: LicenseRating -> LicenseStatement
  LicenseComment :: LicenseComment -> LicenseStatement
  LicenseUrl :: Maybe String -> String -> LicenseStatement
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

tagStmt :: Text -> Text -> LicenseStatement
tagStmt st txt = LicenseTag (UnscopedLicenseTag st (LicenseTagDescription txt))

scopedTagStmt :: String -> Text -> Text -> LicenseStatement
scopedTagStmt scope st txt = LicenseTag (ScopedLicenseTag scope st (LicenseTagDescription txt))

mStmt :: Maybe String -> LicenseStatement
mStmt = MaybeStatement . fmap fromString

typeStmt :: String -> LicenseStatement
typeStmt = LicenseType . fromString

commentStmt :: String -> Text -> LicenseStatement
commentStmt scope = LicenseComment . ScopedLicenseComment scope

ifToStmt :: String -> Bool -> LicenseStatement
ifToStmt stmt True = LicenseStatement stmt
ifToStmt _ False = noStmt

filterStatement :: LicenseStatement -> Maybe LicenseStatement
filterStatement (LicenseComment lc) = if isEmptyLicenseComment lc then Nothing else Just $ LicenseComment lc
filterStatement (LicenseStatement "") = Nothing
filterStatement (LicenseUrl (Just "") url) = filterStatement (LicenseUrl Nothing url)
filterStatement (LicenseUrl _ "") = Nothing
filterStatement (LicenseText "") = Nothing
filterStatement (LicenseRule "") = Nothing
filterStatement (LicenseCompatibilities []) = Nothing
filterStatement (SubStatements stmt substmts) =
  case filterStatements substmts of
    [] -> filterStatement stmt
    filtered -> case filterStatement stmt of
      Just fStmt -> Just $ SubStatements fStmt filtered
      Nothing -> Just $ SubStatements stmt filtered -- TODO (meta TODO: what is that TODO?)
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