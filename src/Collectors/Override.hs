{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE OverloadedStrings #-}
module Collectors.Override
    ( Override (..), emptyOverride
    , loadOverrideFacts
    , overrideLFC
    ) where

import qualified Prelude as P
import           MyPrelude hiding (id)

import qualified Data.Vector as V

import           Model.License
import           Collectors.Common

data Override
  = Override
  { oName :: LicenseName
  , oOtherLicenseIds :: [LicenseName]
  , oDescription :: Maybe String
  , oRatingState :: Maybe RatingState
  , oJudgement :: Maybe Judgement
  , oNonCommecrial :: Maybe Bool
  } deriving (Eq, Show, Generic)
type Overrides
  = [Override]
emptyOverride :: LicenseName -> Override
emptyOverride ln = Override ln [] Nothing Nothing Nothing Nothing
instance ToJSON Override
overrideLFC :: LicenseFactClassifier
overrideLFC = LFC "Override"
instance LFRaw Override where
  getLicenseFactClassifier _                                 = overrideLFC
  getImpliedId o@Override{oName=n}                           = mkRLSR o 101 n
  getImpliedNames o                                          = CLSR (oName o : oOtherLicenseIds o)
  getImpliedDescription o@Override{oDescription=Just d}      = mkRLSR o 101 d
  getImpliedDescription _                                    = NoRLSR
  getImpliedJudgement o@Override{oJudgement=Just j}          = mkSLSR o j
  getImpliedJudgement _                                      = NoSLSR
  getImpliedRatingState o@Override{oRatingState=Just rs}     = mkSLSR o rs
  getImpliedRatingState _                                    = NoSLSR
  getImpliedNonCommercial o@Override{oNonCommecrial=Just nc} = mkRLSR o 101 nc
  getImpliedNonCommercial _                                  = NoRLSR

loadOverrideFacts :: Overrides -> IO Facts
loadOverrideFacts overrides = do
  logThatFactsAreLoadedFrom "Override definitions"
  mapM_ (\Override{oName=n} -> hPutStrLn stderr ("Overide license with name: " ++ n)) overrides
  return . V.map (LicenseFact Nothing) $ V.fromList overrides
