{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE LambdaCase #-}
module Processors.ToPage
  ( toPages
  , WithSource (..), unpackWithSource
  , LicenseDetails (..)
  , Page (..)
  ) where


import qualified Prelude as P
import           MyPrelude

import qualified Data.Map as M
import           Data.List (stripPrefix)
import qualified Data.Text as T
import qualified Data.Text.IO as T
import           Data.Aeson.Encode.Pretty (encodePretty)
import           Data.ByteString.Lazy.Char8 (unpack)
import qualified Data.Aeson.Lens as AL
import           Data.Char (toLower)
import qualified Text.Pandoc as P
import qualified Text.Pandoc.Builder as P
import           Control.Monad
import           Data.Csv as C
import qualified Data.Vector as V
import qualified Data.ByteString.Lazy as BL

import           Model.License
import           Model.LicenseClusterer
import           Model.Query
import           Processors.Rating

data WithSource a
  = WithSource LicenseFactClassifier a
  | WithoutSource a
  deriving (Show, Generic)
unpackWithSource :: WithSource a -> a
unpackWithSource (WithSource _ a)  = a
unpackWithSource (WithoutSource a) = a

data LicenseDetails
  = LicenseDetails
  { ldFullname :: LicenseName
  , ldShortname :: LicenseName
  , ldRating :: Rating
  , ldCopyleft :: Maybe CopyleftKind
  , ldHasPatentHint :: Maybe Bool
  , ldNonCommercial :: Maybe Bool
  , ldOtherNames :: [LicenseName]
  } deriving (Show, Generic)
instance ToNamedRecord LicenseDetails where
  toNamedRecord details = namedRecord [ "Fullname"      C..= ldFullname details
                                      , "Shortname"     C..= ldShortname details
                                      , "Rating"        C..= show (ldRating details)
                                      , "Copyleft"      C..= case ldCopyleft details of
                                          Just copyleft -> show copyleft
                                          Nothing       -> "UNDEFINED"
                                      , "HasPatentHint" C..= case ldHasPatentHint details of
                                          Just patentHint -> show patentHint
                                          Nothing       -> "UNDEFINED"
                                      , "IsNonCommercial" C..= case ldNonCommercial details of
                                          Just nc -> show nc
                                          Nothing -> "UNDEFINED"
                                      ]

calculateDetails :: RatingRules -> (LicenseName, License) -> LicenseDetails
calculateDetails ratingRules (licName, lic) = let
    shortname = fromMaybe "" . unpackRLSR $ getImpliedId lic
    fullname = fromMaybe licName . unpackRLSR $ getImpliedFullName lic
    rating = applyRatingRules ratingRules lic
    copyleft = getCalculatedCopyleft lic
    patent = unpackRLSR (getHasPatentnHint lic)
    nonCommercial = unpackRLSR (getImpliedNonCommercial lic)
    otherNames = let
        isNotElemUpToCase :: String -> [String] -> Bool
        isNotElemUpToCase needle hay = let
          hAY = map (map toLower) hay
          in map toLower needle `notElem` hAY
      in filter (`isNotElemUpToCase` [shortname, fullname]) (unpackCLSR (getImpliedNames lic))
  in LicenseDetails fullname
                    shortname
                    rating
                    copyleft
                    patent
                    nonCommercial
                    otherNames

data Page
  = Page
  { pLicenseDetails :: LicenseDetails
  , pDescription    :: Maybe (WithSource String)
  , pJudgements     :: [WithSource Judgement]
  , pObligations    :: Maybe (WithSource LicenseObligations)
  , pURLs           :: [(Maybe String, URL)]
  , pOSADLRule      :: Maybe (WithSource Text)
  , pText           :: Maybe (WithSource Text)
  -- raw data
  , pLicense        :: License
  } deriving (Show, Generic)

toPage :: RatingRules -> (LicenseName, (License, LicenseClusterTree)) -> (LicenseName, License, Page)
toPage ratingRules (licName, (lic, lct)) = let

    details = calculateDetails ratingRules (licName, lic)

    description = let
        impliedDesc = getImpliedDescription lic
        sourcifyer :: String -> WithSource String
        sourcifyer = case unpackSourceFromRLSR impliedDesc of
          Just lfc -> WithSource lfc
          Nothing  -> WithoutSource
      in case unpackRLSR impliedDesc of
        Just description' -> Just (sourcifyer description')
        Nothing -> Nothing

    judgements = let
        jdgsMap :: Map LicenseFactClassifier Judgement
        jdgsMap = unpackSLSR (getImpliedJudgement lic)
      in (map (uncurry WithSource) . sortOn snd . M.assocs) jdgsMap

    obligations = let
        impliedObligations = getImpliedObligations lic
      in case unpackRLSR impliedObligations of
           Just licOs -> Just (case unpackSourceFromRLSR impliedObligations of
                                 Just lfc -> WithSource lfc licOs
                                 Nothing  -> WithoutSource licOs)
           Nothing    -> Nothing

    urls = let
        sortFun _ (Nothing,_)            = LT
        sortFun (Nothing,_) _            = GT
        sortFun (Just d1,_) (Just d2,_) = d1 `compare` d2
        nubFun (_,u1) (_,u2) = let
            stripPref :: Eq a => [a] -> [a] -> [a]
            stripPref pref act = fromMaybe act (stripPrefix pref act)
            cleanupForNub = stripPref "www" . stripPref "http://" . stripPref "https://" . map toLower
          in cleanupForNub u1 == cleanupForNub u2
      in nubBy nubFun . sortBy sortFun $ unpackCLSR (getImpliedURLs lic)

    osadlRule = let
        lfc = LFC "OSADL License Checklist"
      in case queryLicense lfc (AL.key "osadlRule" . AL._String) lic of
        Just osadlRule' -> Just (WithSource lfc osadlRule')
        Nothing         -> Nothing

    text = let
        impliedText = getImpliedText lic
        sourcifyer :: Text -> WithSource Text
        sourcifyer = case unpackSourceFromRLSR impliedText of
          Just lfc -> WithSource lfc
          Nothing  -> WithoutSource
      in case unpackRLSR impliedText of
        Just text' -> Just (sourcifyer text')
        Nothing    -> Nothing

    page = Page details
                description
                judgements
                obligations
                urls
                osadlRule
                text
                lic

  in (licName, lic, page)


toPages :: RatingRules -> [(LicenseName, (License, LicenseClusterTree))] -> [(LicenseName, License, Page)]
toPages ratingRules = map (toPage ratingRules)
