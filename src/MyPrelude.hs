{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE LambdaCase #-}
module MyPrelude
    ( module X
    , tShow
    , mergeAeson, mergeAesonL
    ) where

import Prelude as X
import GHC.Generics as X
import Data.Maybe as X
import Data.Text as T hiding (map)
import Data.Text as X (Text)
import qualified Data.Vector as V
import Data.Vector as X (Vector)
import Data.Map as X (Map)
import Data.Aeson as X
import Data.List as X
import qualified Data.HashMap.Lazy as HML
-- import Data.ByteString.Lazy as B
import Data.ByteString.Lazy as X (ByteString)
import Debug.Trace as X (trace)
import System.FilePath as X
import System.Directory as X
import System.IO as X (hPutStrLn, stderr)
import Control.Applicative as X ((<|>))

tShow :: (Show a) => a -> Text
tShow = T.pack . show

-- copied from: https://stackoverflow.com/a/44409320
-- answered by: Willem Van Onsem
-- cc-by-sa 3.0
mergeAeson :: ToJSON a => Vector a -> Value
mergeAeson = Object . HML.unions . map (\case
                                           (Object x) -> x
                                           v          -> "value" .= v
                                       ) . V.toList . V.map toJSON

mergeAesonL :: ToJSON a => [a] -> Value
mergeAesonL = Object . HML.unions . map (\case
                                            (Object x) -> x
                                            v          -> "value" .= v
                                        ) . map toJSON
