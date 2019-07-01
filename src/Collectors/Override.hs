{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE OverloadedStrings #-}
module Collectors.Override
    ( Override (..)
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
emptyOverride :: LicenseName -> Override
emptyOverride ln = Override ln [] Nothing Nothing Nothing Nothing
instance ToJSON Override
overrideLFC :: LicenseFactClassifier
overrideLFC = LFC "Override"
instance LFRaw Override where
  getLicenseFactClassifier _                                 = overrideLFC
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
    ++ map (\(sn,oIds) -> (emptyOverride sn) { oOtherLicenseIds = oIds}) [ ("GPL-1.0-only", ["GPL-1.0", "GPL1.0", "GPL1"])
                                                                         , ("GPL-2.0-only", ["GPL-2.0", "GPL2.0", "GPL2", "GPL (v2)"])
                                                                         , ("GPL-3.0-only", ["GPL-3.0", "GPL3.0", "GPL3", "GPL (v3)"])
                                                                         , ("LGPL-2.1-only", ["LGPL-2.1", "LGPL2.1", "LGPL2.1", "LGPL (v2.1)"])
                                                                         , ("LGPL-3.0-only", ["LGPL-3.0", "LGPL-3", "LGPL3.0", "LGPL3", "LGPL (v3.0)", "LGPL (v3)"])
                                                                         , ("AGPL-3.0-only", ["AGPL-3.0", "AGPL3.0", "AGPL3", "AGPL (v3)"])
                                                                         , ("GPL-1.0-or-later", ["GPL-1.0+", "GPL1.0+", "GPL1+"])
                                                                         , ("GPL-2.0-or-later", ["GPL-2.0+", "GPL2.0+", "GPL2+", "GPL (v2 or later)"])
                                                                         , ("GPL-3.0-or-later", ["GPL-3.0+", "GPL3.0+", "GPL3+", "GPL (v3 or later)"])
                                                                         , ("LGPL-2.1-or-later", ["LGPL-2.1+", "LGPL2.1+", "LGPL2.1+", "LGPL (v2.1 or later)"])
                                                                         , ("LGPL-3.0-or-later", ["LGPL-3.0+", "LGPL-3+", "LGPL3.0+", "LGPL3", "LGPL (v3.0)", "LGPL (v3 or later)"])
                                                                         , ("AGPL-3.0-or-later", ["AGPL-3.0+", "AGPL3.0+", "AGPL3+", "AGPL (v3 or later)"])
                                                                         , ("BSL-1.0", ["BSL (v1.0)"])
                                                                         , ("Zlib", ["zlib/libpng"])
                                                                         , ("Apache-1.0", ["Apache (v1.0)", "Apache Software License 1.0", "ASL 1.0"])
                                                                         , ("Apache-1.1", ["Apache (v1.1)", "Apache Software License 1.1", "ASL 1.1"])
                                                                         , ("Apache-2.0", ["Apache (v2.0)", "Apache Software License 2.0", "ASL 2.0"])
                                                                         , ("BSL-1.0", ["BSL (v1)"])
                                                                         , ("BSD-2-Clause", ["BSD (2 clause)"])
                                                                         , ("BSD-3-Clause", ["BSD (3 clause)"])
                                                                         , ("MIT", ["MIT license (also X11)"])
                                                                         , ("Sleepycat", ["Berkeley Database License", "Sleepycat Software Product License"])
                                                                         ]


loadOverrideFacts :: IO Facts
loadOverrideFacts = do
  logThatFactsAreLoadedFrom "Override definitions"
  mapM_ (\Override{oName=n} -> hPutStrLn stderr ("Overide license with name: " ++ n)) overrides
  return . V.map (LicenseFact Nothing) $ V.fromList overrides
