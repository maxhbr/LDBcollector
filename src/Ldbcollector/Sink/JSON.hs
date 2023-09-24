{-# LANGUAGE CPP #-}
{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE OverloadedStrings #-}

module Ldbcollector.Sink.JSON
  ( writeJSON,
  )
where

import Control.Monad.State qualified as MTL
import Data.Aeson (ToJSON)
import Data.Aeson.Text (encodeToLazyText)
import Data.Graph.Inductive.Graph qualified as G
import Data.Graph.Inductive.Monad qualified as G
import Data.Graph.Inductive.PatriciaTree qualified as G
import Data.Graph.Inductive.Query.DFS qualified as G
import Data.Text.Lazy (Text)
import Data.Text.Lazy.IO as I
import Ldbcollector.Model

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
