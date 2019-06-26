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
  , oRatingState :: Maybe RatingState
  , oJudgement :: Maybe Judgement
  } deriving (Eq, Show, Generic)
emptyOverride :: LicenseName -> Override
emptyOverride ln = Override ln Nothing Nothing
instance ToJSON Override
instance LFRaw Override where
  getLicenseFactClassifier _                             = LFC ["Override"]
  getImpliedNames                                        = CLSR . (:[]) . oName
  getImpliedJudgement o@Override{oJudgement=Just j}      = mkSLSR o j
  getImpliedJudgement _                                  = NoSLSR
  getImpliedRatingState o@Override{oRatingState=Just rs} = mkSLSR o rs
  getImpliedRatingState _                                = NoSLSR

loadOverrideFacts :: IO Facts
loadOverrideFacts = pure . V.map (LicenseFact Nothing) $ V.fromList
  [ (emptyOverride "BSD-4-Clause") { oRatingState = Just (RatingState False True True True)
                                   , oJudgement = Just (NegativeJudgement "Advertisement clause (3.) is complicated and prone to conflicts") }
  ]
