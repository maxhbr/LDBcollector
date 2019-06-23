{-# LANGUAGE OverloadedStrings #-}
module Generators.MarkdownWriter
  ( writeMarkdown
  ) where

import qualified Prelude as P
import           MyPrelude

import qualified Data.Text as T
import qualified Data.Aeson.Types as A
import qualified Data.Aeson.Lens as AL

import           Model.License
import           Processors.Rating
import           Processors.GetText
import           Model.Query

licenseToMarkdown :: (LicenseName, License) -> String
licenseToMarkdown (licName, lic) = let
    id = show $ getImpliedId lic
    urls = show $ getImpliedURLs lic
    text = show $ getImpliedText lic
    judgements = show $ getImpliedJudgement lic
  in concat
     [ "# ", licName, "\n\n"
     , "- id: ", id, "\n\n"
     , "## Classification: ", "\n"
     -- , "## Rating: ", tShow rating, "\n"
     , "## Comments:\n", judgements, "\n"
     , "## URLs:\n", urls, "\n"
     , "## Text:\n" , text, "\n"
     , "\n" ]

writeMarkdown :: FilePath -> (LicenseName, License) -> IO ()
writeMarkdown markdownsDirectory (licName, lic) = let
    out = markdownsDirectory </> (licName ++ ".md")
  in writeFile out (licenseToMarkdown (licName, lic))
