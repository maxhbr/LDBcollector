{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE OverloadedStrings #-}
module Collectors.ChooseALicense
  ( loadChooseALicenseFacts
  , extractValueFromText
  , extractListFromText
  ) where

import qualified Prelude as P
import           MyPrelude hiding (ByteString)
import           Collectors.Common

import           Data.List as L
import qualified Data.Vector as V
import qualified Data.ByteString as B
import           Data.ByteString (ByteString)
import qualified Data.ByteString.Char8 as Char8

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
instance LFRaw CALFactRaw where
  getLicenseFactClassifier _                                  = LFC ["choosealicense.com", "CALFact"]
  getImpliedNames CALFactRaw{name = sn
                            , spdxId = sid
                            , nickname = nid}                 = CLSR $ sn : (case sid of
                                                                               Just v  -> [v]
                                                                               Nothing -> []) ++ (case nid of
                                                                                                    Just v  -> [v]
                                                                                                    Nothing -> [])
  getImpliedDescription cfr                                   = case description cfr of
        Just cmt -> mkRLSR cfr 70 cmt
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

loadCalFactFromFile :: FilePath -> FilePath -> IO LicenseFact
loadCalFactFromFile calFolder calFile = let
    fileWithPath = calFolder </> calFile
    n = dropExtension calFile
  in do
    cnt <- B.readFile fileWithPath
    let ls = lines (Char8.unpack cnt)
    return (LicenseFact (Just $ "https://github.com/github/choosealicense.com/blob/gh-pages/_licenses/" ++ calFile)
                        (CALFactRaw n
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

loadChooseALicenseFacts :: FilePath -> IO Facts
loadChooseALicenseFacts calFolder = do
  logThatFactsAreLoadedFrom "choosealicense.com"
  files <- getDirectoryContents calFolder
  let cals = filter ("txt" `isSuffixOf`) files
  facts <- mapM (loadCalFactFromFile calFolder) cals
  return (V.fromList facts)
