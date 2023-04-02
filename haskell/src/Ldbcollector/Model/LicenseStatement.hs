module Ldbcollector.Model.LicenseStatement
  where

import           MyPrelude

type LicenseStatement = String

data PCL
    = PCL 
    { _permissions :: [Text]
    , _conditions :: [Text]
    , _limitations :: [Text]
    } deriving (Eq, Show, Ord, Generic)
instance ToJSON PCL