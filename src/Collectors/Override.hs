{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE OverloadedStrings #-}
module Collectors.Override
    ( Override (..)
    , loadOverrideFacts
    ) where

import qualified Prelude as P
import           MyPrelude hiding (id)

import qualified Data.Vector as V

import           Model.License
import           Collectors.Common

data Override
  = Override
  { oName :: LicenseName
  , oDescription :: Maybe String
  , oRatingState :: Maybe RatingState
  , oJudgement :: Maybe Judgement
  , oNonCommecrial :: Maybe Bool
  } deriving (Eq, Show, Generic)
emptyOverride :: LicenseName -> Override
emptyOverride ln = Override ln Nothing Nothing Nothing Nothing
instance ToJSON Override
instance LFRaw Override where
  getLicenseFactClassifier _                                 = LFC ["Override"]
  getImpliedId o@Override{oName=n}                           = mkRLSR o 101 n
  getImpliedNames                                            = CLSR . (:[]) . oName
  getImpliedDescription o@Override{oDescription=Just d}      = mkRLSR o 101 d
  getImpliedDescription _                                    = NoRLSR
  getImpliedJudgement o@Override{oJudgement=Just j}          = mkSLSR o j
  getImpliedJudgement _                                      = NoSLSR
  getImpliedRatingState o@Override{oRatingState=Just rs}     = mkSLSR o rs
  getImpliedRatingState _                                    = NoSLSR
  getImpliedNonCommercial o@Override{oNonCommecrial=Just nc} = mkRLSR o 101 nc
  getImpliedNonCommercial _                                  = NoRLSR

overrides :: [Override]
overrides =
  [ (emptyOverride "BSD-4-Clause") { oRatingState = Just (RatingState False True True True)
                                   , oJudgement = Just (NegativeJudgement "Advertisement clause (3.) is complicated and prone to conflicts") }
  , (emptyOverride "BSD-4-Clause-UC") { oRatingState = Just (RatingState False True True True)
                                      , oJudgement = Just (NegativeJudgement "Advertisement clause (3.) is complicated and prone to conflicts") }
  ] ++ map (\ sn -> (emptyOverride sn) { oRatingState = Just (FinalRating RNoGo)
                                       , oNonCommecrial = Just True }) [ "CC-BY-NC-1.0"
                                                                       , "CC-BY-NC-2.0"
                                                                       , "CC-BY-NC-2.5"
                                                                       , "CC-BY-NC-3.0"
                                                                       , "CC-BY-NC-4.0"
                                                                       , "CC-BY-NC-ND-1.0"
                                                                       , "CC-BY-NC-ND-2.0"
                                                                       , "CC-BY-NC-ND-2.5"
                                                                       , "CC-BY-NC-ND-3.0"
                                                                       , "CC-BY-NC-ND-4.0"
                                                                       , "CC-BY-NC-SA-1.0"
                                                                       , "CC-BY-NC-SA-2.0"
                                                                       , "CC-BY-NC-SA-2.5"
                                                                       , "CC-BY-NC-SA-3.0"
                                                                       , "CC-BY-NC-SA-4.0" ]


loadOverrideFacts :: IO Facts
loadOverrideFacts = do
  logThatFactsAreLoadedFrom "Override definitions"
  mapM_ (\Override{oName=n} -> hPutStrLn stderr ("Overide license with name: " ++ n)) overrides
  return . V.map (LicenseFact Nothing) $ V.fromList overrides
