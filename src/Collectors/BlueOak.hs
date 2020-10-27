{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE TemplateHaskell #-}
module Collectors.BlueOak
  ( loadBlueOakFacts
  , loadBlueOakFactsFromString
  , decodeBlueOakData -- for testing
  , blueOakLFC
  ) where

import qualified Prelude as P
import           MyPrelude hiding (id)

import qualified Data.Text as T
import qualified Data.Vector as V
import qualified Data.Map as M
import qualified Data.ByteString
import qualified Data.ByteString.Lazy as B
import           Data.ByteString.Lazy (ByteString)
import           Data.FileEmbed (embedFile)

import           Model.License
import           Collectors.Common

data BlueOakLicense
 = BlueOakLicense
 { name :: String
 , id :: String
 , url :: String
 } deriving (Show,Generic)
instance FromJSON BlueOakLicense
instance ToJSON BlueOakLicense

blueOakLFC :: LicenseFactClassifier
blueOakLFC = LFC "BlueOak License List"

-- #############################################################################
-- #  permissive  ##############################################################
-- #############################################################################

data BlueOakRating
 = BlueOakRating
 { rating :: String
 , licenses :: [BlueOakLicense]
 } deriving (Show,Generic)
instance FromJSON BlueOakRating where
  parseJSON = withObject "BlueOakRating" $ \v -> BlueOakRating
    <$> v .: "name"
    <*> v .: "licenses"

data BlueOakData
  = BlueOakData
  { version :: String
  , ratings :: [BlueOakRating]
  } deriving (Show,Generic)
instance FromJSON BlueOakData where
  parseJSON = withObject "BlueOakData" $ \v -> BlueOakData
    <$> v .: "version"
    <*> v .: "ratings"

decodeBlueOakData :: ByteString -> BlueOakData
decodeBlueOakData bs = case decode bs of
  Just bod -> bod
  Nothing  -> trace "ERR: Failed to parse Blue Oak JSON" (BlueOakData "-1" [])

data BOEntry
  = BOEntry String -- licenseListVersion
            String -- rating
            BlueOakLicense -- data
  deriving Generic
instance ToJSON BOEntry where
  toJSON (BOEntry _ r l) = object [ "BlueOakRating" .= r
                                  , "name" .= name l
                                  , "id" .= id l
                                  , "url" .= url l
                                  , "isPermissive" .= True ]
instance Show BOEntry where
  show (BOEntry _ _ j) = show j

instance LFRaw BOEntry where
  getLicenseFactClassifier _               = blueOakLFC
  getImpliedFullName boe@(BOEntry _ _ bol) = mkRLSR boe 40 (name bol)
  getImpliedNames (BOEntry _ _ bol)        = CLSR [id bol, name bol]
  getImpliedJudgement boe@(BOEntry _ r _)  = let
      ratingText = "Rating is: " ++ r
    in SLSR (getLicenseFactClassifier boe) $
       case r of
         "Lead" -> NegativeJudgement ratingText
         _      -> PositiveJudgement ratingText
  getImpliedURLs (BOEntry _ _ bol)         = let
      urlbol = url bol
      isSPDX = ("spdx.org" `isInfixOf` urlbol)
      urlClass = if isSPDX
                 then Just "SPDX"
                 else Nothing
    in CLSR [(urlClass, urlbol)]
  getImpliedCopyleft boe                   = mkSLSR boe NoCopyleft

-- #############################################################################
-- #  copyleft  ################################################################
-- #############################################################################

data BlueOakCopyleftGroup
  = BlueOakCopyleftGroup
  { bocgName :: String
  , versions :: [BlueOakLicense]
  } deriving (Show,Generic)
instance FromJSON BlueOakCopyleftGroup where
  parseJSON = withObject "BlueOakCopyleftGroup" $ \v -> BlueOakCopyleftGroup
    <$> v .: "name"
    <*> v .: "versions"
data BlueOakCopyleftData
  = BlueOakCopyleftData
  { bocgVersion :: String
  , families :: Map String [BlueOakCopyleftGroup]
  } deriving (Show,Generic)
instance FromJSON BlueOakCopyleftData where
  parseJSON = withObject "BlueOakCopyleftData" $ \v -> BlueOakCopyleftData
    <$> v .: "version"
    <*> v .: "families"

decodeBlueOakCopyleftData :: ByteString -> BlueOakCopyleftData
decodeBlueOakCopyleftData bs = case decode bs of
  Just bod -> bod
  Nothing  -> trace "ERR: Failed to parse Blue Oak JSON" (BlueOakCopyleftData "-1" M.empty)

data BOCopyleftEntry
  = BOCopyleftEntry String -- copyleftListVersion
                    CopyleftKind -- kind
                    String -- LicenseGroup
                    BlueOakLicense -- data
  deriving Generic
instance ToJSON BOCopyleftEntry where
  toJSON (BOCopyleftEntry _ k lg l) = object [ "CopyleftKind" .= k
                                             , "name" .= name l
                                             , "id" .= id l
                                             , "url" .= url l
                                             , "familyName" .= lg ]

instance Show BOCopyleftEntry where
  show (BOCopyleftEntry _ _ _ j) = show j

instance LFRaw BOCopyleftEntry where
  getLicenseFactClassifier _                          = blueOakLFC
  getImpliedFullName boe@(BOCopyleftEntry _ _ _ bol)  = mkRLSR boe 40 (name bol)
  getImpliedNames (BOCopyleftEntry _ _ _ bol)         = CLSR [id bol, name bol]
  getImpliedAmbiguousNames (BOCopyleftEntry _ _ lg _) = CLSR [lg]
  getImpliedURLs (BOCopyleftEntry _ _ _ bol)          = CLSR [(Nothing, url bol)]
  getImpliedCopyleft boe@(BOCopyleftEntry _ k _ _)    = mkSLSR boe k

getCommentForKind :: CopyleftKind -> [String]
getCommentForKind WeakCopyleft    = ["Weak copyleft licenses require sharing changes and additions to the licensed software when you give copies to others."]
getCommentForKind StrongCopyleft  = ["Strong copyleft licenses require you to share both the licensed software (like the weak copyleft licenses, and larger programs that you build with the licensed software, when you give copies to others."]
getCommentForKind SaaSCopyleft    =  ["In addition to the requirements of strong copyleft licenses, network copyleft licenses require you to share larger programs that you build with the licensed software not just when you give copies to others, but also when you run the software for others to use over the Internet or another network."]
  ++ getCommentForKind StrongCopyleft
getCommentForKind MaximalCopyleft = ["Maximal copyleft licenses answer the question “When does the license require you to share?” differently than other families. Maximal copyleft licenses require you to share software you make with others, and to license that software alike when you do."]
getCommentForKind _               = []


-- #############################################################################
-- #  general  #################################################################
-- #############################################################################

loadBlueOakFactsFromString :: ByteString -> Facts
loadBlueOakFactsFromString bs = let
    bod = decodeBlueOakData bs
    bodVersion = version bod
    ratingConverter (BlueOakRating r ls) = map (LicenseFact (Just "https://blueoakcouncil.org/list") . BOEntry bodVersion r) ls

    bodc = decodeBlueOakCopyleftData bs
    bodcVersion = bocgVersion bodc
    copyleftConverter f gs = let
      stringToKind "weak"    = WeakCopyleft
      stringToKind "strong"  = StrongCopyleft
      stringToKind "network" = SaaSCopyleft
      stringToKind "maximal" = MaximalCopyleft
      stringToKind _         = Copyleft
      kind = stringToKind f
      copyleftConverter' :: BlueOakCopyleftGroup -> [BOCopyleftEntry]
      copyleftConverter' (BlueOakCopyleftGroup n vs) = map (BOCopyleftEntry bodcVersion kind n) vs
      in concatMap (map (LicenseFact (Just "https://blueoakcouncil.org/copyleft")) . copyleftConverter') gs

    facts = concatMap ratingConverter (ratings bod) ++ concat (M.mapWithKey copyleftConverter (families bodc))
  in trace ("INFO: the version of BlueOak is: " ++ bodVersion) $ V.fromList facts

blueOakFile :: Data.ByteString.ByteString
blueOakFile = $(embedFile "data/blue-oak-council-license-list.json")

loadBlueOakFacts :: IO Facts
loadBlueOakFacts = let
    blueOakFile :: Data.ByteString.ByteString
    blueOakFile = $(embedFile "data/blue-oak-council-license-list.json")
  in do
    logThatFactsAreLoadedFrom "Blue Oak Council License List"
    return (loadBlueOakFactsFromString (B.fromStrict blueOakFile))
