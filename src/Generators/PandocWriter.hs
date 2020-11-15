{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE LambdaCase #-}
module Generators.PandocWriter
  ( writePandoc, writePandocs
  , LicenseDetails (..)
  ) where
{-
   see: https://pandoc.org/using-the-pandoc-api.html#Builder
        http://hackage.haskell.org/package/pandoc
 -}

import qualified Prelude as P
import           MyPrelude

import qualified Data.Map as M
import           Data.List (stripPrefix)
import qualified Data.Text as T
import qualified Data.Text.IO as T
import           Data.Aeson.Encode.Pretty (encodePretty)
import           Data.ByteString.Lazy.Char8 (unpack)
import qualified Data.Aeson.Lens as AL
import           Data.Char (toLower)
import qualified Text.Pandoc as P
import qualified Text.Pandoc.Builder as P
import           Data.Csv as C
import qualified Data.Vector as V
import qualified Data.ByteString.Lazy as BL

import           Model.License
import           Model.Query
import           Processors.Rating
import           Processors.ToPage

renderSource :: LicenseFactClassifier -> Inlines
renderSource lfc = P.space <> P.text "(source: " <> toInline lfc <> P.text ")"

renderDetails :: LicenseDetails -> Blocks
renderDetails details = let
    copyleftRow = case ldCopyleft details of
                    Nothing       -> []
                    Just copyleft -> [["Classification", show copyleft]]
    patentRow = case ldHasPatentHint details of
                  Nothing  -> []
                  Just val -> [["Has Patent Hint",  show val]]
    nonCommercialRow = case ldNonCommercial details of
                         Nothing -> []
                         Just nc -> [["Is Non-Commercial", show nc]]
  in P.simpleTable [P.para (P.text "Key"), P.para (P.text "Value")]
    (map (map (P.para . P.text))
      ([ ["Fullname", ldFullname details]
       , ["Shortname", ldShortname details]
       , ["Rating", show (ldRating details)]
       ] ++ copyleftRow ++ patentRow ++ nonCommercialRow))
    <> if not (null (ldOtherNames details))
       then P.para (P.strong (P.text "Other Names:"))
            <> P.bulletList (map (P.para . P.code) (ldOtherNames details))
       else mempty

renderDescription :: Maybe (WithSource String) -> Blocks
renderDescription Nothing = mempty
renderDescription (Just desc) =
  P.header 2 (P.text "Description")
  <> P.blockQuote (P.para (P.text (unpackWithSource desc)))
  <> case desc of
       WithSource lfc _ -> P.para (renderSource  lfc)
       WithoutSource _  -> mempty

renderJudgements :: [WithSource Judgement] -> Blocks
renderJudgements jdgs = let
    fun' :: Judgement -> Inlines -> Blocks
    fun' j i = P.para (case j of
                          PositiveJudgement d -> P.strong (P.text "↑") <> P.doubleQuoted (P.text d) <> i
                          NeutralJudgement d  -> P.doubleQuoted (P.text d) <> i
                          NegativeJudgement d -> P.strong (P.text "↓") <> P.doubleQuoted (P.text d) <> i )
    fun old (WithoutSource j) = old ++ [fun' j mempty]
    fun old (WithSource k j)  = old ++ [fun' j (renderSource k)]
  in P.header 2 (P.text "Comments on (easy) usability")
    <> (P.bulletList . foldl fun []) jdgs

renderComments :: [WithSource Text] -> Blocks
renderComments cs = let
    fun' :: Text -> Inlines -> Blocks
    fun' c i = P.para (P.doubleQuoted (P.text (T.unpack c)) <> i)
    fun old (WithoutSource c) = old ++ [fun' c mempty]
    fun old (WithSource k c)  = old ++ [fun' c (renderSource k)]
  in P.header 2 (P.text "General Comments")
    <> (P.bulletList . foldl fun []) cs

renderObligations :: Maybe (WithSource LicenseObligations) -> Blocks
renderObligations Nothing = mempty
renderObligations (Just obs) =
  P.header 2 (P.text "Obligations")
  <> toBlock (unpackWithSource obs)
  <> case obs of
       WithSource lfc _ -> P.para (renderSource  lfc)
       WithoutSource _  -> mempty

renderURLs :: [(Maybe String, URL)] -> Blocks
renderURLs [] = mempty
renderURLs urls = let
  in P.header 2 (P.text "URLs")
    <> P.bulletList (map (\case
                             (Just desc, url) -> P.para (P.strong (P.text (desc ++ ":")) <> P.space <> P.text url)
                             (Nothing, url)   -> P.para (P.text url)) urls)

renderOSADLRule :: Maybe (WithSource Text) -> Blocks
renderOSADLRule Nothing          = mempty
renderOSADLRule (Just osadlRule) =
  P.header 2 (P.text "OSADL Rule")
  <> P.codeBlock (T.unpack (unpackWithSource osadlRule))
  <> case osadlRule of
       WithSource lfc _ -> P.para (renderSource lfc)
       WithoutSource _  -> mempty

renderText :: Maybe (WithSource Text) -> Blocks
renderText Nothing = mempty
renderText (Just text) =
  P.header 2 (P.text "Text")
  <> P.codeBlock (T.unpack (unpackWithSource text))


renderRawData :: LicenseName -> License -> Blocks
renderRawData shortname lic@(License facts) = let
    lfcs = P.bulletList . V.toList $ V.map (P.para . toInline . getLicenseFactClassifier) facts
  in P.horizontalRule
     <> P.header 2 (P.text "Raw Data")
     <> P.header 3 (P.text "Facts")
     <> lfcs
     <> P.header 3 (P.text "Raw JSON")
     <> P.codeBlock (unpack (encodePretty lic))
     <> P.header 3 (P.text "Dot Cluster Graph")
     <> P.para (let
                   dotPath = "../dot" </> shortname ++ ".svg"
                 in P.link dotPath dotPath (P.text dotPath))

licenseToPandoc :: LicenseName -> Page -> Pandoc
licenseToPandoc shortname page = let
    fullname = (ldFullname . pLicenseDetails) page
    headerLine = fullname ++ " (" ++ shortname ++ ")"
  in P.doc $ P.header 1 (P.text headerLine)
          <> renderDetails (pLicenseDetails page)
          <> renderDescription (pDescription page)
          <> renderJudgements (pJudgements page)
          <> renderComments (pComments page)
          <> renderObligations (pObligations page)
          <> renderURLs (pURLs page)
          <> renderOSADLRule (pOSADLRule page)
          <> renderText (pText page)
          <> renderRawData shortname (pLicense page)

writePandoc :: FilePath -> Page -> IO ()
writePandoc outDirectory page = let
    shortname = (ldShortname . pLicenseDetails) page
    pandoc = licenseToPandoc shortname page
  in do

    createDirectoryIfNotExists outDirectory
    createDirectoryIfNotExists (outDirectory </> "org")
    case P.runPure (P.writeOrg P.def pandoc) of
      Left err -> print err
      Right org -> T.writeFile (outDirectory </> "org" </> shortname ++ ".org") org

    createDirectoryIfNotExists (outDirectory </> "md")
    case P.runPure (P.writeMarkdown P.def pandoc) of
      Left err -> print err
      Right md -> T.writeFile (outDirectory </> "md" </> shortname ++ ".md") md

    createDirectoryIfNotExists (outDirectory </> "html")
    case P.runPure (P.writeHtml5String P.def pandoc) of
      Left err -> print err
      Right html -> T.writeFile (outDirectory </> "html" </> shortname ++ ".html") html

    createDirectoryIfNotExists (outDirectory </> "adoc")
    case P.runPure (P.writeAsciiDoc P.def pandoc) of
      Left err -> print err
      Right adoc -> T.writeFile (outDirectory </> "adoc" </> shortname ++ ".adoc") adoc

writeHtmlIndex :: FilePath -> [Page] -> IO ()
writeHtmlIndex index pages = let
    renderFun :: Page -> Blocks
    renderFun page = let
        shortname = (ldShortname . pLicenseDetails) page
        link = P.link (shortname ++ ".html") shortname (P.text shortname)
      in P.para link
    list :: Blocks
    list = (P.bulletList . map renderFun) pages
    pandoc = P.doc $ list
  in case P.runPure (P.writeHtml5String P.def pandoc) of
      Left err -> print err
      Right html -> T.writeFile index html

writePandocs :: FilePath -> [Page] -> IO ()
writePandocs outDirectory pages = do
  mapM_ (writePandoc outDirectory) pages
  writeHtmlIndex (outDirectory </> "html" </> "index.html") pages
