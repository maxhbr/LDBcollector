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
  } deriving (Eq, Show, Generic)
emptyOverride :: LicenseName -> Override
emptyOverride ln = Override ln Nothing Nothing Nothing
instance ToJSON Override
instance LFRaw Override where
  getLicenseFactClassifier _                             = LFC ["Override"]
  getImpliedId o@Override{oName=n}                       = mkRLSR o 101 n
  getImpliedNames                                        = CLSR . (:[]) . oName
  getImpliedDescription o@Override{oDescription=Just d}  = mkRLSR o 101 d
  getImpliedDescription _                                = NoRLSR
  getImpliedJudgement o@Override{oJudgement=Just j}      = mkSLSR o j
  getImpliedJudgement _                                  = NoSLSR
  getImpliedRatingState o@Override{oRatingState=Just rs} = mkSLSR o rs
  getImpliedRatingState _                                = NoSLSR

overrides :: [Override]
overrides =
  [ (emptyOverride "BSD-4-Clause") { oRatingState = Just (RatingState False True True True)
                                   , oJudgement = Just (NegativeJudgement "Advertisement clause (3.) is complicated and prone to conflicts") }
  , (emptyOverride "BSD-4-Clause-UC") { oRatingState = Just (RatingState False True True True)
                                      , oJudgement = Just (NegativeJudgement "Advertisement clause (3.) is complicated and prone to conflicts") }
  ]
loadOverrideFacts :: IO Facts
loadOverrideFacts = do
  logThatFactsAreLoadedFrom "Override definitions"
  mapM_ (\Override{oName=n} -> hPutStrLn stderr ("Overide license with name: " ++ n)) overrides
  return . V.map (LicenseFact Nothing) $ V.fromList overrides
