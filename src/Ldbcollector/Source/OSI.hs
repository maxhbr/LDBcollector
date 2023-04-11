{-# LANGUAGE LambdaCase        #-}
{-# LANGUAGE OverloadedStrings #-}
module Ldbcollector.Source.OSI
    ( OSI (..)
    ) where

import qualified Data.Map                            as Map
import qualified Data.Vector                         as V
import qualified Data.Yaml                           as Y
import qualified Data.Yaml.Internal                  as Y
import           Ldbcollector.Model

import           Control.Monad.Except                (runExceptT)
import qualified Network.Protocol.OpenSource.License as OSI

newtype OSILicense
    = OSILicense OSI.OSILicense
    deriving (Eq, Show, Generic)
instance ToJSON OSILicense

instance LicenseFactC OSILicense where
    getType _ = "OSILicense"
    getApplicableLNs (OSILicense l) =
        (LN . newNLN "osi" .  OSI.olId) l
        `AlternativeLNs`
        ((LN . newLN  .  OSI.olName) l : map (\i -> LN $ newNLN (OSI.oiScheme i) (OSI.oiIdentifier i)) (OSI.olIdentifiers l))
        `ImpreciseLNs`
        map (LN . newLN . OSI.oonName) (OSI.olOther_names l)
    getImpliedStmts (OSILicense l) = let
            urls = (map (\link -> (LicenseUrl . unpack . OSI.olUrl) link `SubStatements` [LicenseComment (OSI.olNote link)]) . OSI.olLinks) l
        in urls

data OSI = OSI
instance Source OSI where
    getSource _ = Source "OSI"
    getFacts OSI = do
        response <- runExceptT OSI.allLicenses
        case response of
            Left err -> do
                stderrLogIO $ "Error: " ++ err
                pure mempty
            Right licenses -> (return . V.fromList . map (wrapFact . OSILicense)) licenses
