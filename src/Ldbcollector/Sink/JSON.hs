{-# LANGUAGE CPP #-}
{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE OverloadedStrings #-}

module Ldbcollector.Sink.JSON
  ( writeJSON,
    writeJSONAndGzip,
    writeOutputLicensesJSON,
    writeOutputLicensesToFile,
  )
where

import Codec.Compression.GZip qualified as GZip
import Control.Monad.State qualified as MTL
import Data.Aeson (ToJSON)
import Data.Aeson.Text (encodeToLazyText)
import Data.ByteString.Lazy qualified as BL
import Data.Graph.Inductive.Graph qualified as G
import Data.Text qualified as T
import Data.Text.Lazy.Encoding qualified as TLE
import Data.Text.Lazy.IO qualified as I
import Data.Vector qualified as V
import Ldbcollector.Model
import MyPrelude (createDirectoryIfMissing, dropFileName, (</>))

writeJSON :: FilePath -> LicenseGraphM ()
writeJSON json = do
  writeJSONInternal False json

writeJSONAndGzip :: FilePath -> LicenseGraphM ()
writeJSONAndGzip json = do
  writeJSONInternal True json

writeJSONInternal :: Bool -> FilePath -> LicenseGraphM ()
writeJSONInternal writeGzip json = do
  infoLog $ "generate " ++ json
  facts <-
    MTL.gets
      ( mapMaybe
          ( \case
              LGFact f -> Just f
              _ -> Nothing
              . snd
          )
          . G.labNodes
          . _gr
      )
  let encoded = encodeToLazyText facts
  lift $ I.writeFile json encoded
  when writeGzip $ do
    let gz = json ++ ".gz"
    infoLog $ "generate " ++ gz
    lift $ BL.writeFile gz (GZip.compress (TLE.encodeUtf8 encoded))

writeOutputLicensesJSON :: FilePath -> Text -> LicenseGraphM ()
writeOutputLicensesJSON outdir ns = do
  let json = outdir </> (T.unpack ns) <.> "json"
  infoLog $ "generate concise " ++ json
  outputLicenses <- getOutputLicensesByNamespace ns
  writeOutputLicensesToFile json outputLicenses

writeOutputLicensesToFile :: (ToJSON a) => FilePath -> [a] -> LicenseGraphM ()
writeOutputLicensesToFile json outputLicenses = do
  lift $ createDirectoryIfMissing True (dropFileName json)
  lift $ I.writeFile json (encodeToLazyText outputLicenses)
