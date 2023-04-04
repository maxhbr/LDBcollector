module Main (main) where

import           Test.Hspec
import           Test.QuickCheck

import           ModelSpec
import           SourceSpec

main :: IO ()
main = do
  hspec $ do
    modelSpec
    sourceSpec
