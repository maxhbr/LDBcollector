module Ldbcollector.Model
    ( module X
    , Source (..)
    ) where

import           MyPrelude                           as X

import           Ldbcollector.Model.LicenseFact      as X
import           Ldbcollector.Model.LicenseGraph     as X
import           Ldbcollector.Model.LicenseGraphAlgo as X
import           Ldbcollector.Model.LicenseGraphTask as X
import           Ldbcollector.Model.LicenseName      as X

import qualified Data.Vector as V
import qualified Control.Monad.State               as MTL

class Source a where
    getOrigin :: a -> Origin
    getFacts :: a -> IO (Vector LicenseFact)
    applySource :: a -> LicenseGraphM ()
    applySource a = let
            origin = getOrigin a
            facts = getFacts a
        in MTL.lift (getFacts a) >>= V.mapM_ (\fact -> withFact (origin, fact) $ (applyTask . getTask) fact)
    -- applySource :: a -> LicenseGraphM ()
    -- applySource a = lift (getTask a) >>= applyTask
    -- getTask :: a -> IO LicenseGraphTask
    -- getTask = return . Pure . applySource

