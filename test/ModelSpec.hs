{-# LANGUAGE OverloadedStrings #-}

module ModelSpec where

import Data.Graph.Inductive.Graph qualified as G
import Data.Map qualified as Map
import Ldbcollector.Model
import Test.Hspec
import Test.QuickCheck

modelSpec = do
  describe "LicenseName" $ do
    it "Equals should behave as expected" $ do
      newLN "MIT" `shouldBe` newLN "MIT"
      newLN "MIT" `shouldBe` newLN "mit"
      newLN "MIT" `shouldBe` newLN "Mit"
      newLN "MIT" `shouldNotBe` newNLN "Namespace" "Mit"
      newNLN "Namespace" "MIT" `shouldBe` newNLN "Namespace" "Mit"
  describe "LicenseFact" $ do
    pure ()
  describe "LicenseGraph" $ do
    pure ()
