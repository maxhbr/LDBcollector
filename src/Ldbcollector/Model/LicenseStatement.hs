{-# LANGUAGE OverloadedStrings #-}
module Ldbcollector.Model.LicenseStatement
  where

import           MyPrelude

import           Ldbcollector.Model.LicenseName

data PCLR
    = PCLR
    { _permissions  :: [Text]
    , _conditions   :: [Text]
    , _limitations  :: [Text]
    , _restrictions :: [Text]
    } deriving (Eq, Show, Ord, Generic)
instance ToJSON PCLR

data LicenseCompatibility
    = LicenseCompatibility
    { _other         :: LicenseName
    , _compatibility :: String
    , _explanation   :: Text
    } deriving (Eq, Show, Ord, Generic)
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
    fromString str = let
            lowerStr = map toLower str
            mapping = [ ("PublicDomain", PublicDomain)
                      , ("Public Domain", PublicDomain)
                      , ("Permissive", Permissive)
                      , ("Copyleft", Copyleft)
                      , ("WeaklyProtective", WeaklyProtective)
                      , ("Weakly Protective", WeaklyProtective)
                      , ("weak_copyleft", WeaklyProtective)
                      , ("weak", WeaklyProtective)
                      , ("strong_copyleft", StronglyProtective)
                      , ("StronglyProtective", StronglyProtective)
                      , ("Strongly Protective", StronglyProtective)
                      , ("strong", StronglyProtective)
                      , ("NetworkProtective", NetworkProtective)
                      , ("Network Protective", NetworkProtective)
                      , ("network_copyleft",  NetworkProtective)
                      , ("network", NetworkProtective)
                      , ("Unlicensed", Unlicensed)
                      , ("Proprietary" , Proprietary)
                      , ("ProprietaryFree" , ProprietaryFree)
                      , ("proprietary_free" , ProprietaryFree)
                      , ("Unknown", UnknownLicenseType Nothing)
                      ]
        in case find (\(n,_) -> map toLower n == lowerStr) mapping of
            Just (_,a) -> a
            Nothing    -> UnknownLicenseType (Just str)
class ToLicenseType a where
    toLicenseType :: a -> LicenseType
instance ToLicenseType String where
    toLicenseType = fromString

data LicenseRating
    = PositiveLicenseRating Text (Maybe Text)
    | NeutralLicenseRating Text (Maybe Text)
    | NegativeLicenseRating Text (Maybe Text)
    deriving (Eq, Show, Ord, Generic)
instance ToJSON LicenseRating
unLicenseRating :: LicenseRating -> Text
unLicenseRating (PositiveLicenseRating r _) = r
unLicenseRating (NeutralLicenseRating  r _) = r
unLicenseRating (NegativeLicenseRating r _) = r

data LicenseStatement where
    LicenseStatement :: String -> LicenseStatement
    LicenseType :: LicenseType -> LicenseStatement
    LicenseRating :: String -> LicenseRating -> LicenseStatement
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
ifToStmt stmt True  = LicenseStatement stmt
ifToStmt _    False = noStmt


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
            Nothing    -> Just $ SubStatements stmt filtered -- TODO
filterStatement (MaybeStatement Nothing) = Nothing
filterStatement (MaybeStatement (Just stmt)) = filterStatement stmt
filterStatement stmt = Just stmt

filterStatements :: [LicenseStatement] -> [LicenseStatement]
filterStatements = mapMaybe filterStatement
