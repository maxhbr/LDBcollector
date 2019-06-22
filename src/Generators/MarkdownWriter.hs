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

data ToMarkdownData
  = ToMarkdownData
  { _name :: Text
  , _rating :: Rating
  , _comment :: Maybe Text
  , _text :: Text
  }
instance Show ToMarkdownData where
  show ToMarkdownData { _name = name
                      , _rating = rating
                      , _text = text
                      } = T.unpack
                          $ T.concat
                          [ "# ",  name, "\n\n"
                          , "## Classification: ", "\n"
                          , "## Rating: ", tShow rating, "\n"
                          , "## Comments:\n", "\n"
                          , "## URLs:\n", "\n"
                          , "## Text:\n" , text, "\n"
                          , "\n" ]

handleLicese :: (LicenseName, License) -> ToMarkdownData
handleLicese (licName, lic) = let
  in ToMarkdownData (T.pack licName)
                    (applyEmptyRatingConfiguration (licName, lic))
                    (queryLicense (LFC ["ScancodeData"]) (AL.key "text" . AL._String) lic)
                    (tShow $ getTextOfLicense lic)


writeMarkdown :: FilePath -> (LicenseName, License) -> IO ()
writeMarkdown markdownsDirectory (licName, lic) = let
    out = markdownsDirectory </> (licName ++ ".md")
    mdData = handleLicese (licName, lic)
  in writeFile out (show mdData)
