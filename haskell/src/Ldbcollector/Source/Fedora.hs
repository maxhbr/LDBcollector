module Ldbcollector.Source.Fedora
    ( FedoraData (..)
    ) where

import Ldbcollector.Model hiding (ByteString) 

import qualified Data.ByteString as B
import           Data.ByteString (ByteString)
import qualified Data.Vector as V
import qualified Data.Map as Map
import qualified Data.ByteString.Char8 as Char8
import qualified Control.Monad.State as MTL

data FedoraEntryLicense
    = FedoraEntryLicense
    { _expression :: String
    , _status :: [String]
    , _urls :: [String]
    , _text :: Maybe String
    , _scancode_key :: Maybe String
    }
data FedoraEntryFedora
    = FedoraEntryFedora
    { _legacy_names :: [String]
    , _legacy_abbreviation :: [String]
    , _notes :: Maybe String
    }
data FedoraEntry
    = FedoraEntry
    { _license :: FedoraEntryLicense
    , _fedora :: Maybe FedoraEntryFedora
    }

applyToml :: FilePath -> LicenseGraphM ()
applyToml toml = _

newtype FedoraLicenseData = FedoraLicenseData FilePath
instance Source FedoraLicenseData where
    applySource (FedoraLicenseData dir) = do
        tomls <- MTL.lift . fmap glob (dir </> "*.toml")
        mapM_ applyToml tomls