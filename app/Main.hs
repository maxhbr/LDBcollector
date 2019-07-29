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

cleanupAndMakeOutputFolder :: FilePath -> IO FilePath
cleanupAndMakeOutputFolder outputFolder = do
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

  -- make folders
  outputFolder <- cleanupAndMakeOutputFolder "_generated/"

  -- calculate licenses
  licenses <- case args of
    [] -> calculateSPDXLicenses facts
    _  -> calculateLicenses (V.fromList args) facts

  let pages = toPages (cRatingRules configuration) licenses

  -- generate output
  writeLicenseJSONs outputFolder licenses
  writeDetails outputFolder pages
  writePandocs outputFolder pages

  -- echo some stats
  writeStats outputFolder facts licenses
