{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE LambdaCase #-}
module Generators.MarkdownWriter
  ( writeMarkdown, writeMarkdowns
  ) where
{-
   see: https://pandoc.org/using-the-pandoc-api.html#Builder
        http://hackage.haskell.org/package/pandoc
 -}

import qualified Prelude as P
import           MyPrelude

import qualified Data.Map as M
import qualified Data.Text as T
import qualified Data.Text.IO as T
import           Data.Aeson.Encode.Pretty (encodePretty)
import           Data.ByteString.Lazy.Char8 (unpack)
import qualified Data.Aeson.Lens as AL
import           Data.Char (toUpper)
import qualified Text.Pandoc as P
import qualified Text.Pandoc.Builder as P
import           Text.Pandoc.Builder (Pandoc, Blocks, Inlines)
import qualified Data.ByteString.Lazy as BL

import           Model.License
import           Model.Query
import           Processors.Rating

-- renderNames :: CollectedLicenseStatementResult String -> [LicenseName] -> String
-- renderNames names otherNames = let
--     list = unpackCLSR names
--     fun :: String -> String -> String
--     fun old n = old ++ "\n   - " ++ n
--   in foldl fun "- other names:" (filter (`isNotElemUpToCase` otherNames) list)

renderDetails :: License -> LicenseName -> LicenseName -> Blocks
renderDetails lic shortname fullname = let
    rating = applyDefaultRatingRules lic
    copyleftRow =case getCalculatedCopyleft lic of
                Nothing       -> []
                Just copyleft -> [["Classification", show copyleft]]
    otherNames = let
        isNotElemUpToCase :: String -> [String] -> Bool
        isNotElemUpToCase needle hay = let
          hAY = map (map toUpper) hay
          in not (map toUpper needle `elem` hAY)
      in case unpackCLSR (getImpliedNames lic) of
        names -> (filter (`isNotElemUpToCase` [shortname, fullname]) names)
  in P.simpleTable [P.para (P.text "Key"), P.para (P.text "Value")]
    (map (map (P.para . P.text))
      ([ ["Fullname", fullname]
       , ["Shortname", shortname]
       , ["Rating", show rating]
       ] ++ copyleftRow))
    <> P.para (P.strong (P.text "Other Names:"))
    <> P.bulletList (map (P.para . P.code) otherNames)
  
renderDescription :: License -> Blocks
renderDescription lic = case unpackRLSR (getImpliedDescription lic) of
  Just desc -> P.header 2 (P.text "Description")
    <> P.para (P.text desc)
  Nothing -> mempty

renderJudgements :: License -> Blocks
renderJudgements lic = let
    jdgsMap = unpackSLSR (getImpliedJudgement lic)
    fun :: [Blocks] -> LicenseFactClassifier -> Judgement -> [Blocks]
    fun old k j = let
        fun' d = P.space <> P.text d <> P.text (" (by " ++ show k ++ ")")
      in old ++ [P.para (case j of
                           PositiveJudgement d -> P.strong (P.text "[possitive]") <> fun' d
                           NeutralJudgement d  -> P.strong (P.text "[neutral]") <> fun' d
                           NegativeJudgement d -> P.strong (P.text "[negative]") <> fun' d )]
  in P.header 2 (P.text "Comments")
    <> P.bulletList (M.foldlWithKey fun [] jdgsMap)

renderObligations :: License -> Blocks
renderObligations lic = case unpackRLSR (getImpliedObligations lic) of
  Just (LicenseObligations rights conditions limitations) ->
    P.header 2 (P.text "Obligations")
    <> P.simpleTable (map (P.para . P.text)
                      ["Rights:", "Conditions:", "Limitations:"])
                     [[ P.bulletList (map (P.para . P.text . show) rights)
                      ,  P.bulletList (map (P.para . P.text . show) conditions)
                      , P.bulletList (map (P.para . P.text . show) limitations) ]]
  Nothing -> mempty

renderURLs :: License -> Blocks
renderURLs lic = let
    urls :: [(Maybe String, String)]
    urls = unpackCLSR (getImpliedURLs lic)
  in P.header 2 (P.text "URLs")
    <> P.bulletList (map (\case
                             (Just desc, url) -> P.para (P.strong (P.text (desc ++ ":")) <> P.space <> P.text url)
                             (Nothing, url)   -> P.para (P.text url)) urls)

renderOSADLRule :: License -> Blocks
renderOSADLRule lic = case queryLicense (LFC ["OSADL", "OSADLFact"]) (AL.key "osadlRule" . AL._String) lic of
  Just osadlRule ->  P.header 2 (P.text "OSADL Rule")
    <> P.codeBlock (T.unpack osadlRule)
  Nothing        -> mempty

renderText :: License -> Blocks
renderText lic = case unpackRLSR (getImpliedText lic) of
  Just text -> P.header 2 (P.text "Text")
    <> P.codeBlock (T.unpack text)
  Nothing    -> mempty

renderRawData :: License -> Blocks
renderRawData lic = P.header 2 (P.text "Raw Data")
  <> P.codeBlock (unpack (encodePretty lic))

licenseToPandoc :: (LicenseName, License) -> Pandoc
licenseToPandoc (licName, lic) = let
    shortname = fromMaybe "" . unpackRLSR $ getImpliedId lic
    fullname = fromMaybe licName . unpackRLSR $ getImpliedFullName lic
    headerLine = fullname ++ " (" ++ shortname ++ ")"
  in P.doc $ P.header 1 (P.text headerLine)
          <> renderDetails lic shortname fullname
          <> renderDescription lic
          <> renderJudgements lic
          <> renderObligations lic
          <> renderOSADLRule lic
          <> renderURLs lic
          <> renderText lic
          <> renderRawData lic

writeMarkdown :: FilePath -> (LicenseName, License) -> IO ()
writeMarkdown outDirectory (licName, lic) = let
    outBase = outDirectory </> licName
    -- mdOut = outBase ++ ".md"
    -- htmlOut = outBase ++ ".html"
    -- adocOut = outBase ++ ".adoc"
    orgOut = outBase ++ ".org"
  in do
    let result = licenseToPandoc (licName, lic)
    -- case P.runPure (P.writeMarkdown P.def result) of
    --   Left err -> print err
    --   Right md -> T.writeFile mdOut md
    -- case P.runPure (P.writeHtml5String P.def result) of
    --   Left err -> print err
    --   Right html -> T.writeFile htmlOut html
    -- case P.runPure (P.writeAsciiDoc P.def result) of
    --   Left err -> print err
    --   Right adoc -> T.writeFile adocOut adoc
    case P.runPure (P.writeOrg P.def result) of
      Left err -> print err
      Right org -> T.writeFile orgOut org

writeMarkdowns :: FilePath -> [(LicenseName, License)] -> IO ()
writeMarkdowns outDirectory  = mapM_ (writeMarkdown outDirectory)
