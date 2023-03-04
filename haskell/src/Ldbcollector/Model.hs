module Ldbcollector.Model
    ( module X
    , Source (..)
    ) where

import           MyPrelude                           as X

import           Ldbcollector.Model.LicenseGraph     as X
import           Ldbcollector.Model.LicenseGraphTask as X
import           Ldbcollector.Model.LicenseName      as X

class Source a where
    applySource :: a -> LicenseGraphM ()
    applySource a = lift (getTask a) >>= applyTask
    getTask :: a -> IO LicenseGraphTask
    getTask = return . Pure . applySource

