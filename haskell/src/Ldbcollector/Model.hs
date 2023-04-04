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
    getOrigin :: a -> Origin
    getFacts :: a -> IO (Vector LicenseFact)
    applySource :: a -> LicenseGraphM ()
    applySource a = let
            origin = getOrigin a
        in MTL.lift (getFacts a) >>= V.mapM_ (\fact -> withFact (origin, fact) applyFact)

