{-# LANGUAGE OverloadedStrings #-}
module Main where

import qualified Data.Vector                        as V
import           Prelude                            hiding (div, head, id)

import qualified Control.Monad.State                as MTL
import           Data.Monoid                        (mconcat)

import           Ldbcollector.Model
import           Ldbcollector.Sink.GraphViz
import           Ldbcollector.Source
import           Ldbcollector.Server

main :: IO ()
main = do
    (_, licenseGraph) <- runLicenseGraphM $ do
        applySources
        -- let lns = map (LicenseName . newLN)
        --         [ "BSD-3-Clause"
        --         ]
        -- let nlns = map (LicenseName . uncurry newNLN)
        --         [ ("SPDX", "Apache-2.0")
        --         , ("scancode", "sleepycat")
        --         ]
        -- focus (V.fromList (lns ++ nlns)) $
        --     writeGraphViz "_out/focused.graph.dot"
        serve
    return ()
