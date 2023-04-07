{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE OverloadedStrings #-}
module Ldbcollector.Sink.Metrics
    ( writeMetrics
    ) where

import           Ldbcollector.Model

import qualified Control.Monad.State               as MTL
import qualified Data.Graph.Inductive.Basic        as G
import qualified Data.Graph.Inductive.Graph        as G
import qualified Data.Map                          as Map

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

    let origins = (map fst . Map.keys ) facts
    lift $ infoM "Metrics" $ "number of origins: " ++ show (length (nub origins))
    lift $ infoM "Metrics" $ "number of facts: " ++ show (length facts)
    lift $ infoM "Metrics" $ "number of license clusters: " ++ show (length clusters)
    lift $ infoM "Metrics" $ "number of license names: " ++ show (length names)
    




