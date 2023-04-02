{-# LANGUAGE ScopedTypeVariables #-}
module Ldbcollector.Source.Cavil
    ( CavilLicenseChanges (..)
    ) where

import           Ldbcollector.Model    hiding (decode, lines, unwords)
import           Prelude               hiding (lines, unwords)

import qualified Data.ByteString       as B
import           Data.ByteString.Char8 (lines, split, unwords)
import           Data.Text.Encoding    as T
import qualified Data.Map as M
import qualified Data.Vector as V


-- data/openSUSE-cavil/lib/Cavil/resources/license_changes.txt

newtype CavilLicenseChanges = CavilLicenseChanges FilePath

data CavilLicenseChange
    = CavilLicenseChange
    { _clcName :: LicenseName
    , _clcAlias :: [LicenseName]
    } deriving (Eq, Ord, Show, Generic)
instance ToJSON CavilLicenseChange
instance LicenseFactC CavilLicenseChange where
    getType _ = "CavilLicenseChange"
    getApplicableLNs (CavilLicenseChange name aliases) = LN name `ImpreciseLNs` map LN aliases

lineToMap :: B.ByteString -> Map LicenseName [LicenseName]
lineToMap bs = let
        onerror err input = Just '_'
    in case split '\t' bs of
            []         -> mempty
            [one]      -> M.singleton (newLN (T.decodeUtf8With onerror one)) []
            name:alias -> let
                    nameNode = newLN (T.decodeUtf8With onerror name)
                    aliasNode = newLN (T.decodeUtf8With onerror (unwords alias))
                in M.singleton nameNode [aliasNode]
linesToMap :: [B.ByteString] -> Map LicenseName [LicenseName]
linesToMap bss = M.unionsWith (<>) $ map lineToMap bss

instance Source CavilLicenseChanges where
    getOrigin _  = Origin "CavilLicenseChanges"
    getFacts (CavilLicenseChanges txt) = do
        putStrLn ("read " ++ txt)
        csvData <- B.readFile txt
        let csvLines = tail $ lines csvData
        let changesMap = linesToMap csvLines
        let facts = map (uncurry CavilLicenseChange) (M.assocs changesMap)
        (return . V.fromList . map wrapFact) facts
