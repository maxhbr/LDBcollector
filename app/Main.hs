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
import Stats (writeStats)

cleanupAndMakeOutputFolder :: IO FilePath
cleanupAndMakeOutputFolder = do
  let outputFolder = "_generated/"
  dirExists <- doesDirectoryExist outputFolder
  when dirExists $
    removeDirectoryRecursive outputFolder
  createDirectory outputFolder

  return outputFolder

main :: IO ()
main = do
  setLocaleEncoding utf8

  args <- getArgs

  -- harvest facts
  facts <- readFacts configuration

  -- write output
  outputFolder <- cleanupAndMakeOutputFolder

  -- calculate licenses
  licenses <- case args of
    [] -> calculateSPDXLicenses facts
    _  -> calculateLicenses (V.fromList args) facts
  writeLicenseJSONs outputFolder licenses
  writePandocs (cRatingRules configuration) outputFolder licenses

  -- echo some stats
  writeStats outputFolder facts licenses
