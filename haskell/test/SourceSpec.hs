{-# LANGUAGE OverloadedStrings #-}
module SourceSpec where

import           Test.Hspec hiding (focus)
import           Test.QuickCheck

import qualified Data.Graph.Inductive.Graph as G
import qualified Data.Map as Map
import qualified Data.Vector as V

import Ldbcollector.Model 
import Ldbcollector.Source

testGraph lg = do
    let gr_size = (length . G.nodes . _gr) lg
    let node_map_size = (Map.size . _node_map) lg
    let node_map_rev_size =  (Map.size . _node_map_rev) lg
    it "license graph should not be empty" $ do
        gr_size > 0 `shouldBe` True
    it "license graph sizes should be consistent" $ do
        gr_size `shouldBe` node_map_size
        gr_size `shouldBe` node_map_rev_size

sourceSpec = do
    describe "Sources" $ do
        (_, lg) <- runIO $ runLicenseGraphM applySources
        testGraph lg

        describe "focused" $ do
            (_, focusedLg) <- runIO $ runLicenseGraphM (do
                applySources
                getFocused ((V.fromList . map (LicenseName . newLN)) 
                        [ "BSD-3-Clause"
                        , "MIT"
                        , "GPL-3.0-only"
                        , "GPL-3.0-or-later"
                        ]))
            testGraph focusedLg