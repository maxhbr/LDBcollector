module Ldbcollector.Model
    ( module X
    , Source (..)
    ) where

import           MyPrelude                           as X

import           Ldbcollector.Model.LicenseFact      as X
import           Ldbcollector.Model.LicenseGraph     as X
import           Ldbcollector.Model.LicenseGraphAlgo as X
import           Ldbcollector.Model.LicenseName      as X
import           Ldbcollector.Model.LicenseStatement as X

import qualified Control.Monad.State                 as MTL
import qualified Data.Vector                         as V

class Source a where
    getSource :: a -> SourceRef
    getFacts :: a -> IO (Vector LicenseFact)
    applySource :: a -> LicenseGraphM ()
    applySource a = let
            source = getSource a
        in do
            lift $ infoM rootLoggerName ("# get " ++ show source)
            facts <- force <$> MTL.lift (getFacts a)
            lift $ infoM rootLoggerName (show (V.length facts) ++ " entries")
            V.mapM_ (\fact -> withFact (source, fact) applyFact) facts
            debugOrderAndSize

