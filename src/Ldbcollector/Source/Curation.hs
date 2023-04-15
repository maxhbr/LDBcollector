module Ldbcollector.Source.Curation
  ( Curation (..)
  , CurationItem (..)
  ) where

import           Ldbcollector.Model    hiding (ByteString)

import           Data.ByteString       (ByteString)
import qualified Data.ByteString       as B
import qualified Data.ByteString.Char8 as Char8
import qualified Data.Text             as T
import qualified Data.Vector           as V
import           Data.Yaml

data CurationItem
    = CurationItem ApplicableLNs [LicenseStatement]
    deriving (Show, Eq, Generic)
instance ToJSON CurationItem

instance LicenseFactC CurationItem where
    getType _ = "Curation"
    getApplicableLNs (CurationItem applicableLNs _) = applicableLNs
    getImpliedStmts (CurationItem _ stmts) = stmts

newtype Curation = Curation (V.Vector CurationItem)

instance Source Curation where
    getSource _  = Source "Curation"
    getFacts (Curation items) = return (V.map wrapFact items)

