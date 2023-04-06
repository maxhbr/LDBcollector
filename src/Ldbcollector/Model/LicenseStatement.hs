{-# LANGUAGE OverloadedStrings #-}
module Ldbcollector.Model.LicenseStatement
  where

import           MyPrelude

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

data LicenseStatement where
    LicenseStatement :: String -> LicenseStatement
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
ifToStmt :: String -> Bool -> LicenseStatement
ifToStmt stmt True = LicenseStatement stmt
ifToStmt _    False = noStmt