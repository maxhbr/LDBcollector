module MyPrelude
    ( module X
    , tShow
    ) where

import Prelude as X
import GHC.Generics as X
import Data.Maybe as X
import Data.Text as T
import Data.Text as X (Text)
-- import Data.Vector as V
import Data.Vector as X (Vector)
import Data.Map as X (Map)
import Data.Aeson as X
import Data.List as X
-- import Data.ByteString.Lazy as B
import Data.ByteString.Lazy as X (ByteString)
import Debug.Trace as X (trace)
import System.FilePath as X
import System.Directory as X
import System.IO as X (hPutStrLn, stderr)

tShow :: (Show a) => a -> Text
tShow = T.pack . show
