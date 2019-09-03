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

main :: IO ()
main = do
  outputFolder <- cleanupAndMakeOutputFolder "_generated/"
  runLDBCore configuration
    (\_ input ->
        do
          let licenses = map (\(ln, l, _) -> (ln, l)) input
          let pages = map (\(_,_,p) -> p) input

          writeLicenseJSONs outputFolder licenses
          writeDetails outputFolder pages
          writePandocs outputFolder pages

          return outputFolder)
