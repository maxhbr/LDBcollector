{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE ScopedTypeVariables #-}

module Ldbcollector.Source.Cavil
  ( CavilLicenseChanges (..),
  )
where

import Data.ByteString qualified as B
import Data.ByteString.Char8 (lines, split, unwords)
import Data.Map qualified as M
import Data.Text.Encoding as T
import Data.Vector qualified as V
import Ldbcollector.Model hiding (decode, lines, unwords)
import Prelude hiding (lines, unwords)

data CavilLicenseChange = CavilLicenseChange
  { _clcName :: LicenseName,
    _clcAlias :: [LicenseName]
  }
  deriving (Eq, Ord, Show, Generic)

instance ToJSON CavilLicenseChange

instance LicenseFactC CavilLicenseChange where
  getType _ = "CavilLicenseChange"
  getApplicableLNs (CavilLicenseChange name aliases) = LN name `ImpreciseLNs` map LN aliases

lineToMap :: B.ByteString -> Map LicenseName [LicenseName]
lineToMap bs =
  let onerror _ _ = Just '_'
   in case split '\t' bs of
        [] -> mempty
        [one] -> M.singleton (newNLN "cavil" (T.decodeUtf8With onerror one)) []
        name : alias ->
          let nameNode = newNLN "cavil" (T.decodeUtf8With onerror name)
              aliasNode = newLN (T.decodeUtf8With onerror (unwords alias))
           in M.singleton nameNode [aliasNode]

linesToMap :: [B.ByteString] -> Map LicenseName [LicenseName]
linesToMap bss = M.unionsWith (<>) $ map lineToMap bss

newtype CavilLicenseChanges = CavilLicenseChanges FilePath

instance HasOriginalData CavilLicenseChanges where
  getOriginalData (CavilLicenseChanges txt) =
    FromUrl "https://github.com/openSUSE/cavil" $
      FromFile txt NoPreservedOriginalData

instance Source CavilLicenseChanges where
  getSource _ = Source "CavilLicenseChanges"
  getSourceDescription _ = Just "Cavil is a legal review system for the Open Build Service. It is used in the development of openSUSE Tumbleweed, openSUSE Leap, as well as SUSE Linux Enterprise."
  getFacts (CavilLicenseChanges txt) = do
    logFileReadIO txt
    csvData <- B.readFile txt
    let csvLines = tail $ lines csvData
    let changesMap = linesToMap csvLines
    let facts = map (uncurry CavilLicenseChange) (M.assocs changesMap)
    (return . V.fromList . map wrapFact) facts
