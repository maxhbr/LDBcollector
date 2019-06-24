{-# LANGUAGE OverloadedStrings #-}
module Generators.MarkdownWriter
  ( writeMarkdown
  ) where

import qualified Prelude as P
import           MyPrelude

import qualified Data.Map as M
import qualified Data.Text as T
import           Data.Aeson.Encode.Pretty (encodePretty)
import           Data.ByteString.Lazy.Char8 (unpack)
import qualified Data.Aeson.Lens as AL

import           Model.License
import           Model.Query
import           Processors.Rating

mkCodeBlock :: String -> String
mkCodeBlock code = "\n```\n" ++ code ++ "\n```\n"

renderNames :: CollectedLicenseStatementResult String -> String
renderNames names = let
    list = unpackCLSR names
    fun :: String -> String -> String
    fun old n = old ++ "\n   - " ++ n
  in foldl fun "- other names:" list

renderClassification :: License -> String
renderClassification lic = case getCalculatedCopyleft lic of
  Nothing       -> ""
  Just copyleft -> "## Classification: " ++ show copyleft

renderJudgements :: ScopedLicenseStatementResult Judgement -> String
renderJudgements jdgs = let
    jdgsMap = unpackSLSR jdgs
    fun :: String -> LicenseFactClassifier -> Judgement -> String
    fun old k j = old ++ "\n - " ++
      (case j of
        PositiveJudgement d -> "**[possitive]** " ++ d
        NeutralJudgement d -> "**[neutral]** " ++ d
        NegativeJudgement d -> "**[negative]** " ++ d ) ++
      " (by " ++ show k ++ ")"
  in M.foldlWithKey fun "## Comments:" jdgsMap

renderURLs :: CollectedLicenseStatementResult (Maybe String, String) -> String
renderURLs urls = let
    list = unpackCLSR urls
    fun :: String -> (Maybe String, String) -> String
    fun old (Just desc, url) = old ++ "\n - **" ++ desc ++ ":** " ++ url
    fun old (Nothing, url) = old ++ "\n - " ++ url
  in foldl fun "## URLs:" list

renderOSADLRule :: License -> String
renderOSADLRule lic = case queryLicense (LFC ["OSADL", "OSADLFact"]) (AL.key "osadlRule" . AL._String) lic of
  Just osadlRule -> "## OSADL Rule:\n" ++ mkCodeBlock (T.unpack osadlRule)
  Nothing        -> ""

renderText :: RankedLicenseStatementResult Text -> String
renderText text = case unpackRLSR text of
  Just value -> "## Text:" ++ mkCodeBlock (T.unpack value)
  Nothing    -> ""

renderRawData :: License -> String
renderRawData lic = "## Raw Data:" ++ (mkCodeBlock . unpack $ encodePretty lic)

licenseToMarkdown :: (LicenseName, License) -> String
licenseToMarkdown (licName, lic) = let
    id = fromMaybe "" . unpackRLSR $ getImpliedId lic
    fullname = fromMaybe licName . unpackRLSR $ getImpliedFullName lic
    names = getImpliedNames lic
    urls = getImpliedURLs lic
    text = getImpliedText lic
    judgements = getImpliedJudgement lic

    rating = applyDefaultRatingRules lic

  in concat
     [ "# ", fullname, "\n\n"
     , "- id: ", id, "\n\n"
     , renderNames names , "\n"
     , renderClassification lic, "\n"
     , "## Rating: ", show rating, "\n"
     , renderJudgements judgements, "\n"
     , renderURLs urls, "\n"
     , renderOSADLRule lic, "\n"
     , renderText text
     , renderRawData lic ]

writeMarkdown :: FilePath -> (LicenseName, License) -> IO FilePath
writeMarkdown markdownsDirectory (licName, lic) = let
    out = markdownsDirectory </> (licName ++ ".md")
  in do
    writeFile out (licenseToMarkdown (licName, lic))
    return out
