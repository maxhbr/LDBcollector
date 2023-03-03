{-# LANGUAGE ScopedTypeVariables #-}
module Ldbcollector.Source.Cavil
    ( CavilLicenseChanges (..)
    ) where

import Prelude hiding (unwords, lines)
import Ldbcollector.Model hiding (decode, unwords, lines)

import qualified Data.ByteString as B
import Data.Csv
import qualified Data.Vector as V
import           Data.Char (ord)
import           Data.ByteString.Char8 (lines, split, unwords)
import           Data.Text.Encoding as T


-- data/openSUSE-cavil/lib/Cavil/resources/license_changes.txt

newtype CavilLicenseChanges = CavilLicenseChanges FilePath

instance Source CavilLicenseChanges where
    applySource (CavilLicenseChanges txt) = do
        stderrLog ("read " ++ txt)
        csvData <- lift $ B.readFile txt
        let csvLines = tail $ lines csvData
        mapM_ (\bs -> case split '\t' bs of
            []         -> return ()
            [one]      -> stderrLog ("Just found " ++ show one)
            name:alias -> let
                    onerror err input = Just '_'
                    nameNode = LicenseName (newLN (T.decodeUtf8With onerror name))
                    aliasNode = LicenseName (newLN (T.decodeUtf8With onerror (unwords alias)))
                in do
                    _ <- addEdge (aliasNode, nameNode, Better)
                    return ()
            ) csvLines