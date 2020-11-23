{-# LANGUAGE OverloadedStrings #-}
module Main where

import qualified Prelude as P
import           MyPrelude

import           Control.Monad
import qualified Data.Vector as V
import           GHC.IO.Encoding
import           System.Environment

import Lib
import Configuration (configuration)
import Comparator

main :: IO ()
main = do
  outputFolder <- cleanupAndMakeOutputFolder "_generated/"
  runLDBCore configuration
    (\facts input ->
        do
          let licenses = map (\(ln, l, _, _) -> (ln, l)) input
          let pages = map (\(_,_,p, _) -> p) input
          let trees = map (\(ln, _, _, t) -> (ln, t)) input

          writeLicenseJSONs outputFolder licenses
          writeFactsLicenses outputFolder facts licenses
          writeDetails outputFolder pages
          writePandocs outputFolder pages
          writeGraphizs outputFolder trees

          writeCopyleftTable outputFolder licenses

          return outputFolder)
