{-# LANGUAGE LambdaCase        #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE CPP               #-}
module Ldbcollector.Sink.JSON
    ( writeJSON
    ) where

import qualified Control.Monad.State           as MTL
import qualified Data.Graph.Inductive.Graph        as G
import qualified Data.Graph.Inductive.Monad        as G
import qualified Data.Graph.Inductive.PatriciaTree as G
import qualified Data.Graph.Inductive.Query.DFS    as G
import Data.Text.Lazy (Text)
import Data.Text.Lazy.IO as I
import Data.Aeson.Text (encodeToLazyText)
import Data.Aeson (ToJSON)
import           Ldbcollector.Model

writeJSON :: FilePath -> LicenseGraphM ()
writeJSON json = do
    debugLog $ "generate " ++ json
    facts <- MTL.gets (mapMaybe (\case
                               LGFact f -> Just f
                               _        -> Nothing
                           . snd) . G.labNodes . _gr)
    lift $ I.writeFile json (encodeToLazyText facts)