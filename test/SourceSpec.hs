{-# LANGUAGE OverloadedStrings #-}

module SourceSpec where

import Control.Monad.State qualified as MTL
import Data.Graph.Inductive.Graph qualified as G
import Data.Map qualified as Map
import Data.Vector qualified as V
import Ldbcollector.Model
import Ldbcollector.Source
import Test.Hspec hiding (focus)
import Test.QuickCheck

testGraph lg = do
  let gr_size = (length . G.nodes . _gr) lg
  let node_map_size = (Map.size . _node_map) lg
  let node_map_rev_size = (Map.size . _node_map_rev) lg
  it "license graph should not be empty" $ do
    gr_size > 0 `shouldBe` True
  it "license graph sizes should be consistent" $ do
    gr_size `shouldBe` node_map_size
    gr_size `shouldBe` node_map_rev_size

sourceSpec = do
  describe "Sources" $ do
    (_, lg) <- runIO . runLicenseGraphM $ do
      applySources mempty
      MTL.get
    testGraph lg

    describe "focused" $ do
      (_, focusedLg) <-
        runIO $
          runLicenseGraphM
            ( do
                applySources mempty
                getFocused
                  []
                  ( (V.fromList . map (LGName . newLN))
                      [ "BSD-3-Clause",
                        "MIT",
                        "GPL-3.0-only",
                        "GPL-3.0-or-later"
                      ]
                  )
            )
      testGraph focusedLg
