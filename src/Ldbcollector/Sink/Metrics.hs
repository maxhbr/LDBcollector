{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE OverloadedStrings #-}

module Ldbcollector.Sink.Metrics
  ( writeMetrics,
  )
where

import Control.Monad.State qualified as MTL
import Data.Graph.Inductive.Basic qualified as G
import Data.Graph.Inductive.Graph qualified as G
import Data.Map qualified as Map
import Ldbcollector.Model

writeMetrics :: LicenseGraphM ()
writeMetrics = do
  lift $ updateGlobalLogger "Metrics" (setLevel DEBUG)
  debugOrderAndSize
  lift $ infoM "Metrics" "metrics: "
  licenseGraph <- MTL.get
  let names = getLicenseGraphLicenseNames licenseGraph
  clusters <- getClusters
  licenseNameGraph <- getLicenseNameGraph
  let facts = _facts licenseGraph

  let sources = (map fst . Map.keys) facts
  lift $ infoM "Metrics" $ "number of sources: " ++ show (length (nub sources))
  lift $ infoM "Metrics" $ "number of facts: " ++ show (length facts)
  lift $ infoM "Metrics" $ "number of license clusters: " ++ show (length clusters)
  lift $ infoM "Metrics" $ "number of license names: " ++ show (length names)
