{-# LANGUAGE OverloadedStrings #-}
module Ldbcollector.Source.SPDX
  ( SPDXLicenseIds(SPDXLicenseIds)
  ) where

import Ldbcollector.Model 
import qualified Data.Graph.Inductive.Graph as G

import Distribution.SPDX.Extra (LicenseId)

data SPDXLicenseIds = SPDXLicenseIds

instance Source SPDXLicenseIds where
    applySource _ = let
            spdxLicenseIds :: [LicenseId]
            spdxLicenseIds = enumFrom (toEnum 0)
            fun :: LicenseId -> LicenseGraphM G.Node
            fun licenseId = let 
                    nameAsText = pack $ show licenseId
                    name = LicenseName $ newLN nameAsText
                    namespacedName = LicenseName $ newNLN "SPDX" nameAsText
                in addEdge (name, namespacedName, Better)
        in mapM_ fun spdxLicenseIds