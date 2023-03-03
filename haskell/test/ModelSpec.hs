{-# LANGUAGE OverloadedStrings #-}
module ModelSpec where

import           Test.Hspec
import           Test.QuickCheck

import qualified Data.Graph.Inductive.Graph as G
import qualified Data.Map as Map

import Ldbcollector.Model 

modelSpec = 
    describe "LicenseName" $ do
        it "Equals should behave as expected" $ do
            newLN "MIT" `shouldBe` newLN "MIT"
            newLN "MIT" `shouldBe` newLN "mit"
            newLN "MIT" `shouldBe` newLN "Mit"
            newLN "MIT" `shouldNotBe` newNLN "Namespace" "Mit"
            newNLN "Namespace" "MIT" `shouldBe` newNLN "Namespace" "Mit"
