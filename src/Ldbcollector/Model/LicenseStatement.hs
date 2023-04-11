{-# LANGUAGE OverloadedStrings #-}
module Ldbcollector.Model.LicenseStatement
  where

import           MyPrelude
import           Data.Char (toLower)

import           Ldbcollector.Model.LicenseName

data PCLR
    = PCLR 
    { _permissions :: [Text]
    , _conditions :: [Text]
    , _limitations :: [Text]
    , _restrictions :: [Text]
    } deriving (Eq, Show, Ord, Generic)
instance ToJSON PCLR

data LicenseCompatibility
    = LicenseCompatibility 
    { _other :: LicenseName 
    , _compatibility :: String 
    , _explanation :: Text
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
                      , ("weak", WeaklyProtective)
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
                      , ("Unknown", Unknown Nothing)
                      ]
        in case find (\(n,_) -> map toLower n == lowerStr) mapping of
            Just (_,a) -> a
            Nothing -> Unknown (Just str)
class ToLicenseType a where
    toLicenseType :: a -> LicenseType
instance ToLicenseType String where
    toLicenseType = fromString


data LicenseStatement where
    LicenseStatement :: String -> LicenseStatement
    LicenseType :: LicenseType -> LicenseStatement
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
ifToStmt _    False = noStmt