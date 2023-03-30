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

class Source a where
    getOrigin :: a -> Origin
    getFacts :: a -> Vector LicenseFact
    applyFacts :: a -> LicenseGraphM ()
    applyFacts a = let
            origin = getOrigin a
            facts = getFacts a
        in V.mapM_ (\fact -> withFact (origin, fact) $ (applyTask . getTask) fact) facts
    -- applySource :: a -> LicenseGraphM ()
    -- applySource a = lift (getTask a) >>= applyTask
    -- getTask :: a -> IO LicenseGraphTask
    -- getTask = return . Pure . applySource

