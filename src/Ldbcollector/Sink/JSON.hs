{-# LANGUAGE CPP #-}
{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE OverloadedStrings #-}

module Ldbcollector.Sink.JSON
  ( writeJSON,
    writeOutputLicensesJSON,
  )
where

import Control.Monad.State qualified as MTL
import Data.Aeson (ToJSON)
import Data.Aeson.Text (encodeToLazyText)
import Data.Graph.Inductive.Graph qualified as G
import Data.Text qualified as T
import Data.Text.Lazy.IO qualified as I
import Data.Vector qualified as V
import Ldbcollector.Model
import MyPrelude ((</>))

writeJSON :: FilePath -> LicenseGraphM ()
writeJSON json = do
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
  lift $ I.writeFile json (encodeToLazyText facts)

writeOutputLicensesJSON :: FilePath -> Text -> LicenseGraphM ()
writeOutputLicensesJSON outdir ns = do
  let json= outdir </> (T.unpack ns) <.> "json"
  infoLog $ "generate concise " ++ json
  outputLicenses <- getOutputLicensesByNamespace ns
  lift $ I.writeFile json (encodeToLazyText outputLicenses)
