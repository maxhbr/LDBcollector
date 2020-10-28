{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE TemplateHaskell #-}
module Collectors.ChooseALicense
  ( loadChooseALicenseFacts
  , extractValueFromText
  , extractListFromText
  , calLFC
  ) where

import qualified Prelude as P
import           MyPrelude hiding (ByteString)
import           Collectors.Common

import           Data.List as L
import qualified Data.Vector as V
import qualified Data.ByteString as B
import           Data.ByteString (ByteString)
import qualified Data.ByteString.Char8 as Char8
import           Data.FileEmbed (embedDir)

import           Model.License

data CALFactRaw
  = CALFactRaw
  { name :: LicenseName
  , title :: Maybe String
  , spdxId :: Maybe LicenseName
  , nickname :: Maybe LicenseName
  , featured :: Maybe String
  , hidden :: Maybe String
  , description :: Maybe String
  , how :: Maybe String
  , permissions :: [String]
  , conditions :: [String]
  , limitations :: [String]
  , content :: ByteString
  } deriving (Show, Generic)
instance ToJSON ByteString where
  toJSON = toJSON . Char8.unpack
instance ToJSON CALFactRaw
calLFC :: LicenseFactClassifier
calLFC = LFCWithLicense (LFLWithURL "https://github.com/github/choosealicense.com/blob/gh-pages/LICENSE.md" "MIT") "choosealicense.com"
instance LicenseFactClassifiable CALFactRaw where
  getLicenseFactClassifier _ = calLFC
instance LFRaw CALFactRaw where
  getImpliedNames CALFactRaw{name = sn
                            , spdxId = sid
                            , nickname = nid}                 = CLSR $ sn : (case sid of
                                                                               Just v  -> [v]
                                                                               Nothing -> []) ++ (case nid of
                                                                                                    Just v  -> [v]
                                                                                                    Nothing -> [])
  getImpliedDescription cal                                   = case description cal of
        Just cmt -> mkRLSR cal 70 cmt
        Nothing  -> NoRLSR
  getImpliedJudgement cfr                                     = case featured cfr of
                                                                  Just "true" -> mkSLSR cfr $ PositiveJudgement " This License is featured by choosealicense.com"
                                                                  _           -> NoSLSR
  getImpliedObligations cal@CALFactRaw{ permissions = perms
                                      , conditions = conds
                                      , limitations = limits} = mkRLSR cal 70 (LicenseObligations (map ImpliedRight perms) (map ImpliedCondition conds) (map ImpliedLimitation limits))

extractValueFromText :: [String] -> String -> Maybe String
extractValueFromText ls key = let
    prefix = key ++ ": "
  in case filter (prefix `isPrefixOf`) ls of
       [l] -> stripPrefix prefix l
       _   -> Nothing

extractListFromText :: [String] -> String -> [String]
extractListFromText ls key = let
    prefix = key ++ ":"
    tailIfPresent []     = []
    tailIfPresent (_:as) = as
    lns = map (drop 4) . L.takeWhile (/= "") . tailIfPresent $ L.dropWhile (/= prefix) ls
  in lns

loadCalFactFromFile :: (FilePath, ByteString) -> LicenseFact
loadCalFactFromFile (calFile, cnt) = let
    ls = lines (Char8.unpack cnt)
  in (LicenseFact (Just $ "https://github.com/github/choosealicense.com/blob/gh-pages/_licenses/" ++ calFile)
       (CALFactRaw (dropExtension calFile)
                   (extractValueFromText ls "title")
                   (extractValueFromText ls "spdx-id")
                   (extractValueFromText ls "nickname")
                   (extractValueFromText ls "featured")
                   (extractValueFromText ls "hidden")
                   (extractValueFromText ls "description")
                   (extractValueFromText ls "how")
                   (extractListFromText ls "permissions")
                   (extractListFromText ls "conditions")
                   (extractListFromText ls "limitations")
                   cnt))

calFolder :: [(FilePath, ByteString)]
calFolder = $(embedDir "data/choosealicense.com/")

loadChooseALicenseFacts :: IO Facts
loadChooseALicenseFacts = let
    facts = map loadCalFactFromFile (filter (\(fp,_) -> "txt" `isSuffixOf` fp) calFolder)
  in do
    logThatFactsAreLoadedFrom "choosealicense.com"
    return (V.fromList facts)
