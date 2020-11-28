{-# LANGUAGE OverloadedStrings #-}
module Main where

import qualified Prelude as P
import           MyPrelude

import           Control.Monad
import qualified Data.Vector as V
import           GHC.IO.Encoding
import           System.Environment
import qualified Data.ByteString.Lazy as BL
import qualified Data.Csv as C

import Lib
import Configuration (configuration, configurationPriv)
import Comparator
import OpenLicenseTranslator

run :: IO()
run = let
    handler outputFolder = (\facts input -> do
                               let licenses = map (\(ln, l, _, _) -> (ln, l)) input
                               let pages = map (\(_,_,p, _) -> p) input
                               let trees = map (\(ln, _, _, t) -> (ln, t)) input

                               writeLicenseJSONs outputFolder licenses
                               writeDetails outputFolder pages
                               writePandocs outputFolder pages
                               writeGraphizs outputFolder trees

                               writeCopyleftTable outputFolder licenses

                               return outputFolder)
  in do
  outputFolder <- cleanupAndMakeOutputFolder "_generated/"
  runLDBCore configuration (handler outputFolder)
  outputFolderPriv <- cleanupAndMakeOutputFolder "_generated.priv/"
  runLDBCore configurationPriv (handler outputFolderPriv)

main :: IO ()
main = do
  args <- getArgs
  case args of
    ["translate", apiKey] -> writeTranslate apiKey
    _             -> run
