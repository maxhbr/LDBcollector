module MyPrelude
    ( module X
    , tShow
    , createDirectoryIfNotExists
    , createParentDirectoryIfNotExists
    ) where

import           Control.Applicative        as X
import           Control.Monad              as X
import           Data.Aeson                 as X
import           Data.Aeson.Encode.Pretty   as X (encodePretty)
import           Data.ByteString.Lazy       as X (ByteString)
import           Data.List                  as X
import           Data.Map                   as X (Map)
import           Data.Maybe                 as X
import           Data.Monoid                as X
import           Data.Text                  as X (Text, pack, unpack)
import           Data.Vector                as X (Vector)
import           Debug.Trace                as X (trace)
import           GHC.Generics               as X
import           Prelude                    as X
-- import           Text.Pandoc.Builder as X (Pandoc, Blocks, Inlines)
import           Control.Monad.State        as X (lift)
import           Data.Graph.Inductive.Graph as X (LNode, Node)
import           Data.String                as X (IsString (fromString))
import           Data.Typeable              as X
import           System.Directory           as X
import           System.FilePath            as X
import           System.FilePath.Glob       as X (glob)
import           System.IO                  as X (hPutStrLn, stderr)

tShow :: (Show a) => a -> Text
tShow = pack . show

createDirectoryIfNotExists :: FilePath -> IO ()
createDirectoryIfNotExists = createDirectoryIfMissing True

createParentDirectoryIfNotExists :: FilePath -> IO ()
createParentDirectoryIfNotExists = createDirectoryIfNotExists . dropFileName

