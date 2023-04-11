{-# LANGUAGE OverloadedStrings #-}
module Main where

import qualified Data.Vector                as V
import           Prelude                    hiding (div, head, id)

import qualified Control.Monad.State        as MTL
import           Data.Monoid                (mconcat)

import           Ldbcollector.Model
import           Ldbcollector.Server
import           Ldbcollector.Sink.GraphViz
import           Ldbcollector.Sink.Metrics
import           Ldbcollector.Source

main :: IO ()
main = do
    setupLogger
    (_, licenseGraph) <- runLicenseGraphM $ do
        applySources
        writeMetrics
        serve
    return ()
