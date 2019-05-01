module Model.Utils
    ( mergeAeson
    , mergeAesonL
    ) where

import qualified Data.Vector as V
import           Data.Vector (Vector)
import           Data.Aeson
import qualified Data.HashMap.Lazy as HML

-- copied from: https://stackoverflow.com/a/44409320
-- answered by: Willem Van Onsem
-- cc-by-sa 3.0
mergeAeson :: ToJSON a => Vector a -> Value
mergeAeson = Object . HML.unions . map (\(Object x) -> x) . V.toList . V.map toJSON

mergeAesonL :: ToJSON a => [a] -> Value
mergeAesonL = Object . HML.unions . map (\(Object x) -> x) . map toJSON
