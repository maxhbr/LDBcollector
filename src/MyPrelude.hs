{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE LambdaCase #-}
module MyPrelude
    ( module X
    , tShow
    , mergeAeson, mergeAesonL
    , Inlineable (..), Blockable (..)
    , createDirectoryIfNotExists
    ) where

import           Prelude as X
import           GHC.Generics as X
-- import Data.ByteString.Lazy as B
import           Control.Applicative as X
import           Control.Monad as X
import           Data.Aeson as X
import           Data.ByteString.Lazy as X (ByteString)
import qualified Data.HashMap.Lazy as HML
import           Data.List as X
import           Data.Map as X (Map)
import           Data.Maybe as X
import           Data.Monoid as X ((<>), mempty, mconcat)
import           Data.Text as T hiding (map)
import           Data.Text as X (Text)
import           Data.Vector as X (Vector)
import qualified Data.Vector as V
import           Debug.Trace as X (trace)
import           Text.Pandoc.Builder as X (Pandoc, Blocks, Inlines)
import           System.Directory as X
import           System.FilePath as X
import           System.IO as X (hPutStrLn, stderr)

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
mergeAesonL = Object . HML.unions . map ((\case
                                            (Object x) -> x
                                            v          -> "value" .= v)
                                         . toJSON)

class Inlineable a where
  toInline :: a -> Inlines

class Blockable a where
  toBlock :: a -> Blocks

createDirectoryIfNotExists :: FilePath -> IO ()
createDirectoryIfNotExists = createDirectoryIfMissing True
