module Generators.MarkdownWriter
  where

import qualified Prelude as P
import           MyPrelude

import           Model.License

writeMarkdown :: FilePath -> (LicenseName, License) -> IO ()
writeMarkdown markdownsDirectory (licName, lic) = undefined
