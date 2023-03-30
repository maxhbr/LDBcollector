{-# LANGUAGE OverloadedStrings #-}
module Ldbcollector.Source.SPDX
  ( SPDXLicenseIds(SPDXLicenseIds)
  ) where

import           Ldbcollector.Model

import qualified Data.Vector as V
import           Distribution.SPDX.Extra    (LicenseId)

newtype LicenseIdFact = LicenseIdFact LicenseId
    deriving (Eq, Ord)

instance ToJSON LicenseIdFact where
    toJSON (LicenseIdFact licenseId) = (toJSON . show) licenseId


instance LicenseFactC LicenseIdFact where
    getType _ = "SPDX-LicenseId"
    getTask (LicenseIdFact licenseId) = BetterLNs [(newLN . pack . show) licenseId] $
                                            AddLN ((newNLN "spdx" . pack . show) licenseId)

data SPDXLicenseIds = SPDXLicenseIds

instance Source SPDXLicenseIds where
    getOrigin _  = Origin "SPDX"
    getFacts SPDXLicenseIds = return $ let
            spdxLicenseIds :: [LicenseId]
            spdxLicenseIds = enumFrom (toEnum 0)
        in (wrapFactV . V.fromList . map LicenseIdFact) spdxLicenseIds
