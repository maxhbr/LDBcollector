module Main (main) where

import ModelSpec
import SourceSpec
import Test.Hspec
import Test.QuickCheck

main :: IO ()
main = do
  hspec $ do
    modelSpec
    sourceSpec
