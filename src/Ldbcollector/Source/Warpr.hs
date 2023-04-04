{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE OverloadedStrings #-}
module Ldbcollector.Source.Warpr
    ( Warpr (..)
    ) where

import           Ldbcollector.Model
import qualified Data.Vector           as V
import qualified Data.Map              as Map
-- import qualified Data.Text.Lazy as T
-- import qualified Data.Text.Lazy.IO as T
import qualified Swish.RDF               as TTL
import qualified Swish.RDF.Parser.Turtle as TTL
import qualified Data.Text.IO as T
import qualified Data.Text as T (Text, pack, unlines)

import qualified Data.RDF.Query  as RDF
import qualified Data.RDF.Graph.TList as RDF (TList)
import qualified Data.RDF.Types as RDF
import qualified Text.RDF.RDF4H.TurtleParser as RDF

data WarprLicense
    = WarprLicense LicenseName (RDF.RDF RDF.TList)
    deriving (Show, Generic)
instance Eq WarprLicense where 
instance ToJSON WarprLicense where
    toJSON (WarprLicense id graph) = object ["_id" .= id, "_graph" .= show graph]

instance LicenseFactC WarprLicense where
    getType _ = "WarprLicense"
    getApplicableLNs (WarprLicense l g) = NLN l
    getImpliedStmts (WarprLicense l g) = []

getWarprLicense :: FilePath -> IO WarprLicense
getWarprLicense ttl = do
    putStrLn ("read " ++ ttl)
    let fromFilename = takeBaseName (takeBaseName ttl)
    ttlText <- T.readFile ttl
    case RDF.parseString (RDF.TurtleParser Nothing Nothing) ttlText of
        Left err -> fail (show err)
        Right rdf -> return $ WarprLicense (newNLN "warpr" (pack fromFilename)) rdf
    -- case TTL.parseTurtlefromText ttlText of
    --     Left err -> fail err
    --     Right rdf -> return $ WarprLicense (newNLN "warpr" (pack fromFilename)) rdf

newtype Warpr = Warpr FilePath

instance Source Warpr where
    getOrigin _ = Origin "Warpr"
    getFacts (Warpr dir) = do
        ttls <- glob (dir </> "*.ttl")
        V.fromList . map wrapFact <$> mapM getWarprLicense ttls
