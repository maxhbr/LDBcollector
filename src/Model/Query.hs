{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE Rank2Types #-}
module Model.Query
  ( queryLicense
  , queryByteString
  , module X
  ) where

import           Data.List (intersect)
import qualified Data.Text as T
import           Data.Text (Text)
import           Data.Char (toUpper)
import qualified Data.Vector as V
import           Data.Vector (Vector)
import           Data.Aeson
import           Data.Aeson.Lens as X
import           Control.Lens as X
import           GHC.Generics
import qualified Data.ByteString.Lazy as B
import           Data.ByteString.Lazy (ByteString)
import qualified Data.ByteString.Lazy.Char8 as Char8
import           Debug.Trace (trace)
import qualified Data.HashMap.Lazy as HML

import Model.License

queryLicense :: LicenseFactClassifier -> Traversal' Value o -> License -> Maybe o
queryLicense (lfc@(n,t)) qry l = (getFactJSON l lfc) >>= (queryByteString (key (T.pack (n ++ ":" ++ t)) . qry))

queryByteString :: Traversal' ByteString o -> ByteString -> Maybe o
queryByteString qry jsonString = case decode jsonString :: Maybe Value of
  Just v  -> jsonString ^? qry
  Nothing -> trace ("parsing error: " ++ show jsonString) Nothing
