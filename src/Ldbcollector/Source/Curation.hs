module Ldbcollector.Source.Curation
  ( Curation (..),
    CurationItem (..),
  )
where

import Data.ByteString (ByteString)
import Data.ByteString qualified as B
import Data.ByteString.Char8 qualified as Char8
import Data.Text qualified as T
import Data.Vector qualified as V
import Data.Yaml
import Ldbcollector.Model hiding (ByteString)

data CurationItem
  = CurationItem ApplicableLNs [LicenseStatement]
  deriving (Show, Eq, Generic)

instance ToJSON CurationItem

instance LicenseFactC CurationItem where
  getType _ = "Curation"
  getApplicableLNs (CurationItem applicableLNs _) = applicableLNs
  getImpliedStmts (CurationItem _ stmts) = stmts

newtype Curation = Curation (V.Vector CurationItem)

instance HasOriginalData Curation where
  getOriginalData (Curation items) =
    OriginalJsonData (toJSON items)

instance Source Curation where
  getSource _ = Source "Curation"
  getFacts (Curation items) = return (V.map wrapFact items)
