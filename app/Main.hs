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

handler outputFolder = (\facts input -> do
                           let licenses = map (\(ln, l, _, _) -> (ln, l)) input
                           let pages = map (\(_,_,p, _) -> p) input
                           let trees = map (\(ln, _, _, t) -> (ln, t)) input

                           writeLicenseJSONs outputFolder licenses
                           writeFlictLicenseTranslationJSON outputFolder licenses
                           writeDetails outputFolder pages
                           writePandocs outputFolder pages
                           writeGraphizs outputFolder trees
                           writeOrtLicenseClassificationYml outputFolder pages

                           writeCopyleftTable outputFolder licenses
                           -- writeFactJSONs outputFolder facts


                           return outputFolder)

run :: IO()
run = do
  outputFolder <- cleanupAndMakeOutputFolder "_generated/"
  runLDBCore configuration (handler outputFolder)

runPriv :: IO ()
runPriv = do
  outputFolderPriv <- cleanupAndMakeOutputFolder "_generated.priv/"
  runLDBCore configurationPriv (handler outputFolderPriv)

main :: IO ()
main = do
  args <- getArgs
  case args of
    ["translate", apiKey] -> writeTranslate apiKey
    "priv":args'          -> withArgs args' runPriv
    _                     -> run
