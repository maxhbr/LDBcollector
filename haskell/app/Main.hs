{-# LANGUAGE OverloadedStrings #-}
module Main where

import qualified Data.Vector as V

import Ldbcollector.Model
import Ldbcollector.Source
import Ldbcollector.Sink.GraphViz

main :: IO ()
main = do
    _ <- runLicenseGraphM $ do
        applySources
        let lns = map (LicenseName . newLN)
                [ "BSD-3-Clause"
                ]
        let nlns = map (LicenseName . uncurry newNLN)
                [ ("SPDX", "MIT")
                , ("scancode", "sleepycat")
                ]
        focus (V.fromList (lns ++ nlns)) $
            writeGraphViz "_out/focused.graph.dot"
        -- writeGraphViz "_out/graph.dot"
    return ()
