module MyPrelude
  ( module X,
    strToLower,
    tShow,
    bsToText,
    createDirectoryIfNotExists,
    createParentDirectoryIfNotExists,
    setupLogger,
    debugLogIO,
    logFileReadIO,
    infoLogIO,
    stderrLogIO,
  )
where

import Control.Applicative as X
-- import           Text.Pandoc.Builder as X (Pandoc, Blocks, Inlines)
import Control.DeepSeq as X (NFData (..), force, rwhnf)
import Control.Monad as X
import Control.Monad.State as X (lift)
import Data.Aeson as X
import Data.Aeson.Encode.Pretty as X (encodePretty)
import Data.Aeson.TH as X (Options (..), defaultOptions, deriveJSON)
import Data.ByteString qualified as BS (ByteString)
import Data.ByteString.Lazy as X (ByteString)
import Data.Char as X (toLower)
import Data.Graph.Inductive.Graph as X (LNode, Node)
import Data.List as X
import Data.Map as X (Map)
import Data.Maybe as X
import Data.Monoid as X
import Data.String as X (IsString (fromString))
import Data.Text as X (Text, pack, unpack)
import Data.Text.Encoding qualified as Enc
import Data.Typeable as X
import Data.Vector as X (Vector)
import Debug.Trace as X (trace)
import GHC.Generics as X
import System.Console.Pretty (Color (Yellow), color)
import System.Directory as X
import System.FilePath as X
import System.FilePath.Glob as X (glob)
import System.IO as X (hPutStrLn, stderr)
import System.Log.Formatter
import System.Log.Handler (setFormatter)
import System.Log.Handler.Simple
import System.Log.Handler.Syslog
import System.Log.Logger as X
import Text.Blaze as X (Markup)
import Prelude as X

bsToText :: BS.ByteString -> Text
bsToText =
  let onerror _ _ = Just '_'
   in Enc.decodeUtf8With onerror

strToLower :: [Char] -> [Char]
strToLower = map toLower

tShow :: (Show a) => a -> Text
tShow = pack . show

createDirectoryIfNotExists :: FilePath -> IO ()
createDirectoryIfNotExists = createDirectoryIfMissing True

createParentDirectoryIfNotExists :: FilePath -> IO ()
createParentDirectoryIfNotExists = createDirectoryIfNotExists . dropFileName

debugLogIO :: String -> IO ()
debugLogIO msg = debugM rootLoggerName msg

logFileReadIO :: String -> IO ()
logFileReadIO msg = debugM rootLoggerName ("read: " ++ msg)

infoLogIO :: String -> IO ()
infoLogIO msg = infoM rootLoggerName msg

stderrLogIO :: String -> IO ()
stderrLogIO msg = errorM rootLoggerName (color Yellow msg)

setupLogger :: IO ()
setupLogger = do
  updateGlobalLogger rootLoggerName (setLevel DEBUG)
  hStderr <-
    streamHandler stderr INFO >>= \lh ->
      return $
        setFormatter lh (simpleLogFormatter "[$time : $loggername : $prio] $msg")
  hFile <-
    fileHandler "_debug.log" DEBUG >>= \lh ->
      return $
        setFormatter lh (simpleLogFormatter "[$time : $loggername : $prio] $msg")
  infoLogIO "# start ..."
  updateGlobalLogger rootLoggerName (setHandlers [hStderr, hFile])
