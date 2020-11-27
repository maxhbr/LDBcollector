{-# LANGUAGE QuasiQuotes #-}
{-# LANGUAGE TemplateHaskell #-}
module Collectors.CavilData
  ( cavilFolder
  ) where

import           Data.ByteString (ByteString)
import           Data.FileEmbed (embedDir)

cavilFolder :: [(FilePath, ByteString)]
cavilFolder = [] {- $ -} {- (embedDir "data/openSUSE-cavil/") -}
