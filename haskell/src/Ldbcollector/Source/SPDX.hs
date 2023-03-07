{-# LANGUAGE OverloadedStrings #-}
module Ldbcollector.Source.SPDX
  ( SPDXLicenseIds(SPDXLicenseIds)
  ) where

import qualified Data.Graph.Inductive.Graph as G
import           Ldbcollector.Model

import qualified Data.Vector as V
import           Distribution.SPDX.Extra    (LicenseId)

data SPDXLicenseIds = SPDXLicenseIds

instance Source SPDXLicenseIds where
    getTask _ = return $ let
            spdxLicenseIds :: [LicenseId]
            spdxLicenseIds = enumFrom (toEnum 0)
            getTaskForId licenseId =
                Edge ((Add . LicenseName . newLN . pack . show) licenseId) Better $
                    Add ((LicenseName . newNLN "spdx" . pack . show) licenseId)
        in AddTs . V.fromList $ map getTaskForId spdxLicenseIds
