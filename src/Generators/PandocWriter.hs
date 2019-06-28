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
import           Control.Monad
import           Data.Csv as C
import qualified Data.Vector as V
import qualified Data.ByteString.Lazy as BL

import           Model.License
import           Model.Query
import           Processors.Rating

renderSource :: LicenseFactClassifier -> Inlines
renderSource lfc = P.space <> P.text "(source: " <> toInline lfc <> P.text ")"

data LicenseDetails
  = LicenseDetails
  { ldFullname :: LicenseName
  , ldShortname :: LicenseName
  , ldRating :: Rating
  , ldCopyleft :: Maybe CopyleftKind
  , ldHasPatentHint :: Maybe Bool
  , ldNonCommercial :: Maybe Bool
  , ldOtherNames :: [LicenseName]
  } deriving (Show, Generic)
instance ToNamedRecord LicenseDetails where
  toNamedRecord details = namedRecord [ "Fullname"      C..= ldFullname details
                                      , "Shortname"     C..= ldShortname details
                                      , "Rating"        C..= show (ldRating details)
                                      , "Copyleft"      C..= case ldCopyleft details of
                                          Just copyleft -> show copyleft
                                          Nothing       -> "UNDEFINED"
                                      , "HasPatentHint" C..= case ldHasPatentHint details of
                                          Just patentHint -> show patentHint
                                          Nothing       -> "UNDEFINED"
                                      , "IsNonCommercial" C..= case ldNonCommercial details of
                                          Just nc -> show nc
                                          Nothing -> "UNDEFINED"
                                      ]

writeListOfDetailsToFile :: FilePath -> [LicenseDetails] -> IO ()
writeListOfDetailsToFile csv detailss = let
    bs = C.encodeByName (V.fromList ["Fullname","Shortname","Rating","Copyleft","HasPatentHint", "IsNonCommercial"]) detailss
  in BL.writeFile csv bs

calculateDetails :: License -> LicenseName -> LicenseName -> LicenseDetails
calculateDetails lic shortname fullname = let
    rating = applyDefaultRatingRules lic
    copyleft = getCalculatedCopyleft lic
    patent = unpackRLSR (getHasPatentnHint lic)
    nonCommercial = unpackRLSR (getImpliedNonCommercial lic)
    otherNames = let
        isNotElemUpToCase :: String -> [String] -> Bool
        isNotElemUpToCase needle hay = let
          hAY = map (map toLower) hay
          in map toLower needle `notElem` hAY
      in filter (`isNotElemUpToCase` [shortname, fullname]) (unpackCLSR (getImpliedNames lic))
  in LicenseDetails fullname shortname rating copyleft patent nonCommercial otherNames

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

renderDescription :: License -> Blocks
renderDescription lic = let
    impliedDesc = getImpliedDescription lic
  in case unpackRLSR impliedDesc of
    Just desc -> P.header 2 (P.text "Description")
      <> P.blockQuote (P.para (P.text desc))
      <> P.para (case unpackSourceFromRLSR impliedDesc of
                   Just lfc -> renderSource  lfc
                   Nothing -> mempty)
    Nothing -> mempty

renderJudgements :: License -> Blocks
renderJudgements lic = let
    jdgsMap = unpackSLSR (getImpliedJudgement lic)
    sortFun (_,PositiveJudgement _) (_,PositiveJudgement _) = EQ
    sortFun (_,PositiveJudgement _) _                       = LT
    sortFun (_,NeutralJudgement _) (_,PositiveJudgement _)  = GT
    sortFun (_,NeutralJudgement _) (_,NeutralJudgement _)   = EQ
    sortFun (_,NeutralJudgement _) _                        = LT
    sortFun (_,NegativeJudgement _) (_,NegativeJudgement _) = EQ
    sortFun (_,NegativeJudgement _) _                       = GT
    fun :: [Blocks] -> (LicenseFactClassifier, Judgement) -> [Blocks]
    fun old (k,j) = let
        fun' d = P.space <> P.text d <> renderSource k
      in old ++ [P.para (case j of
                           PositiveJudgement d -> P.strong (P.text "↑") <> fun' d
                           NeutralJudgement d  -> fun' d
                           NegativeJudgement d -> P.strong (P.text "↓") <> fun' d )]
  in P.header 2 (P.text "Comments on (easy) usability")
    <> (P.bulletList . foldl fun [] . sortBy sortFun . M.assocs) jdgsMap

renderObligations :: License -> Blocks
renderObligations lic = let
    impliedObligations = getImpliedObligations lic
  in case unpackRLSR impliedObligations of
  Just licOs -> P.header 2 (P.text "Obligations")
                <> toBlock licOs
                <> P.para (case unpackSourceFromRLSR impliedObligations of
                             Just lfc -> renderSource  lfc
                             Nothing -> mempty)
  Nothing -> mempty

renderURLs :: License -> Blocks
renderURLs lic = let
    urls :: [(Maybe String, String)]
    urls = let
        sortFun _ (Nothing,_)            = LT
        sortFun (Nothing,_) _            = GT
        sortFun (Just d1,_) (Just d2,_) = compare d1 d2
        stripPref :: Eq a => [a] -> [a] -> [a]
        stripPref pref act = fromMaybe act (stripPrefix pref act)
        cleanupForNub = stripPref "www" . stripPref "http://" . stripPref "https://" . map toLower
        nubFun (_,u1) (_,u2) = cleanupForNub u1 == cleanupForNub u2
      in nubBy nubFun . sortBy sortFun $ unpackCLSR (getImpliedURLs lic)
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
  Nothing   -> mempty

renderRawData :: License -> Blocks
renderRawData lic = P.horizontalRule
                    <> P.header 2 (P.text "Raw Data")
                    <> P.codeBlock (unpack (encodePretty lic))

licenseToPandoc :: (LicenseName, License) -> (Pandoc, LicenseDetails)
licenseToPandoc (licName, lic) = let
    shortname = fromMaybe "" . unpackRLSR $ getImpliedId lic
    fullname = fromMaybe licName . unpackRLSR $ getImpliedFullName lic
    headerLine = fullname ++ " (" ++ shortname ++ ")"
    details = calculateDetails lic shortname fullname
  in ( P.doc $ P.header 1 (P.text headerLine)
            <> renderDetails details
            <> renderDescription lic
            <> renderJudgements lic
            <> renderObligations lic
            <> renderURLs lic
            <> renderOSADLRule lic
            <> renderText lic
            <> renderRawData lic
     , details)

writePandoc :: FilePath -> (LicenseName, License) -> IO LicenseDetails
writePandoc outDirectory (licName, lic) = let
    (pandoc, details) = licenseToPandoc (licName, lic)
    createDirectoryIfNotExists folder = do
      dirExists <- doesDirectoryExist folder
      unless dirExists $
        createDirectory folder
  in do

    createDirectoryIfNotExists outDirectory
    case P.runPure (P.writeOrg P.def pandoc) of
      Left err -> print err
      Right org -> T.writeFile (outDirectory </> licName ++ ".org") org

    createDirectoryIfNotExists (outDirectory </> "md")
    case P.runPure (P.writeMarkdown P.def pandoc) of
      Left err -> print err
      Right md -> T.writeFile (outDirectory </> "md" </> licName ++ ".md") md

    createDirectoryIfNotExists (outDirectory </> "html")
    case P.runPure (P.writeHtml5String P.def pandoc) of
      Left err -> print err
      Right html -> T.writeFile (outDirectory </> "html" </> licName ++ ".html") html

    createDirectoryIfNotExists (outDirectory </> "adoc")
    case P.runPure (P.writeAsciiDoc P.def pandoc) of
      Left err -> print err
      Right adoc -> T.writeFile (outDirectory </> "adoc" </> licName ++ ".adoc") adoc

    return details

writePandocs :: FilePath -> [(LicenseName, License)] -> IO ()
writePandocs outDirectory lics = do
  detailss <- mapM (writePandoc outDirectory) lics
  writeListOfDetailsToFile (outDirectory </> "index.csv") detailss
