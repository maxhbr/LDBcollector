module Ldbcollector.Model 
    ( module X
    , Source (..)
    ) where

import MyPrelude as X

import Ldbcollector.Model.LicenseName as X
import Ldbcollector.Model.LicenseGraph as X

class Source a where
    applySource :: a -> LicenseGraphM ()

