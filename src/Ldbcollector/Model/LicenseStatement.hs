{-# LANGUAGE OverloadedStrings #-}
module Ldbcollector.Model.LicenseStatement
  where

import           MyPrelude

import           Ldbcollector.Model.LicenseName

import qualified Data.GraphViz                     as GV
import qualified Data.GraphViz.Attributes.Complete as GV
import qualified Data.GraphViz.Attributes.HTML     as GVH
import qualified Data.Text.Lazy                    as LT

data PCL
    = PCL 
    { _permissions :: [Text]
    , _conditions :: [Text]
    , _limitations :: [Text]
    } deriving (Eq, Show, Ord, Generic)
instance ToJSON PCL

data LicenseCompatibility
    = LicenseCompatibility 
    { _other :: LicenseName 
    , _compatibility :: String 
    , _explanation :: Text
    } deriving (Eq, Show, Ord, Generic)
instance ToJSON LicenseCompatibility

data LicenseStatement where
    LicenseStatement :: String -> LicenseStatement
    LicenseComment :: Text -> LicenseStatement
    LicenseUrl :: String -> LicenseStatement
    LicenseText :: Text -> LicenseStatement
    LicenseRule :: Text -> LicenseStatement
    LicensePCL :: PCL -> LicenseStatement
    LicenseCompatibilities :: [LicenseCompatibility] -> LicenseStatement
    SubStatements :: LicenseStatement -> [LicenseStatement] -> LicenseStatement
    MaybeStatement :: Maybe LicenseStatement -> LicenseStatement
    deriving (Eq, Show, Ord, Generic)
instance ToJSON LicenseStatement

instance IsString LicenseStatement where
    fromString = LicenseStatement
noStmt :: LicenseStatement
noStmt = MaybeStatement Nothing
stmt :: String -> LicenseStatement
stmt = fromString
mstmt :: Maybe String -> LicenseStatement
mstmt = MaybeStatement . fmap fromString
ifToStmt :: String -> Bool -> LicenseStatement
ifToStmt stmt True = LicenseStatement stmt
ifToStmt _    False = noStmt

toMultilineHTML :: Text -> GV.Label
toMultilineHTML txt = let
        dropLeadingWhitespace :: Char -> LT.Text -> LT.Text
        dropLeadingWhitespace c = LT.dropWhile (== c)
        replaceWhitespacePrefix' :: Char -> Int -> LT.Text -> LT.Text
        replaceWhitespacePrefix' c factor line = let
               shortenedLine = dropLeadingWhitespace c line
               lengthDiff = LT.length line - LT.length shortenedLine
            in LT.replicate lengthDiff (LT.replicate (fromIntegral factor) "&nbsp;") <> shortenedLine
        replaceWhitespacePrefix :: LT.Text -> LT.Text
        replaceWhitespacePrefix = replaceWhitespacePrefix' ' ' 1 . replaceWhitespacePrefix' '\t' 4
        newline = GVH.Newline [GVH.Align GVH.HLeft]
    in (GV.HtmlLabel . GVH.Text) $ intersperse newline ((map (GVH.Str . replaceWhitespacePrefix) . LT.lines . LT.fromStrict) txt) ++ [newline]

toMultilineStr :: Text -> GV.Label
toMultilineStr = GV.StrLabel . LT.replace "\n" "\\l" . LT.fromStrict . (<> "\\l")

instance GV.Labellable LicenseStatement where
    toLabelValue (LicenseText txt) = toMultilineStr txt
    toLabelValue (LicenseRule txt) =  toMultilineStr txt
    toLabelValue (LicenseComment txt) = toMultilineStr txt
    toLabelValue (LicensePCL pcl) = let
            header = GVH.Cells [ GVH.LabelCell [] (GVH.Text [GVH.Str "Permissions"])
                               , GVH.LabelCell [] (GVH.Text [GVH.Str "Conditions"])
                               , GVH.LabelCell [] (GVH.Text [GVH.Str "Limitations"])
                               ]
            linesToContent :: [Text] -> GVH.Cell
            linesToContent = GVH.LabelCell [] . GVH.Text . intersperse newline . map (GVH.Str . LT.fromStrict)
            newline = GVH.Newline []
            content = GVH.Cells (map linesToContent [ _permissions pcl, _conditions pcl, _limitations pcl])
        in GV.HtmlLabel . GVH.Table $ GVH.HTable Nothing [] [ header, content ]
    toLabelValue (LicenseCompatibilities compatibilities) = let
            mkLine (LicenseCompatibility other compatibility explanation) = 
                GVH.Cells [ GVH.LabelCell [] (GVH.Text [GVH.Str . LT.pack $ show other])
                          , GVH.LabelCell [] (GVH.Text [GVH.Str $ LT.pack compatibility])
                        --   , GVH.LabelCell [] (GVH.Text [GVH.Str $ LT.fromStrict explanation])
                          ]
        in GV.HtmlLabel . GVH.Table $ GVH.HTable Nothing [] (map mkLine compatibilities)
    toLabelValue statement = (GV.StrLabel . LT.pack . show) statement