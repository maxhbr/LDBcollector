{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE DeriveGeneric #-}
module Generators.AliasesWriter
    ( writeAliasesCSV
    ) where


import qualified Prelude as P
import           MyPrelude

import qualified Data.ByteString.Lazy as BL
import           Data.Aeson.Encode.Pretty (encodePretty)
import qualified Data.Vector as V
import           Data.Csv hiding ((.=))
import qualified Data.Csv as C
import           Data.Char (toLower)
import           Data.List (nub)

import           Model.License
import           Processors.ToPage (Page (..), LicenseDetails (..), unpackWithSource)

data Alias
  = Alias 
  { _target :: LicenseName
  , _alias :: LicenseName
  , _is_nonambiguos :: Bool
  } deriving (Eq,Show)
instance ToRecord Alias where
   toRecord (Alias ln a b) = record [ toField ln, toField a, (if b
                                                              then "True"
                                                              else "False")]

writeAliasesCSV :: FilePath -> [(LicenseName, License)] -> IO ()
writeAliasesCSV  outputFolder licenses = let
    fun :: (LicenseName, License) -> [Alias]
    fun (ln, l) = [Alias ln alias True | alias <- getImpliedNonambiguousNames l
                                       , map toLower ln /= map toLower alias ] ++
                  [Alias ln alias False | alias <- unpackCLSR (getImpliedAmbiguousNames l)
                                        , not (alias `elem ` getImpliedNonambiguousNames l)
                                        , map toLower ln /= map toLower alias ]

    duplicates :: [LicenseName] -> [LicenseName]
    duplicates [] = []
    duplicates (a:as) | a `elem` as = a : duplicates as
                      | otherwise   = duplicates as
    flagDuplicates mapping' = let
        ds = (duplicates . map _alias . nub) mapping'
      in map (\m@(Alias ln a _) -> if a `elem` ds
                             then Alias ln a False
                             else m) mapping'
    mapping = nub. flagDuplicates $ concatMap fun licenses
  in do
    createDirectoryIfNotExists (outputFolder </> "aliases")
    BL.writeFile (outputFolder </> "aliases" </> "aliases.csv") (C.encode  mapping)
