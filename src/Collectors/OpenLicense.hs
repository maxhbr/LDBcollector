{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE QuasiQuotes #-}
{-# LANGUAGE TemplateHaskell #-}
module Collectors.OpenLicense
  ( olLFC
  , loadOpenLicenseFacts
  , loadOpenLicenseTranslateables, TranslationRow (..)
  )
  where

import qualified Prelude as P
import           MyPrelude hiding (id)

import           Data.Aeson
import           Data.Aeson.Encode.Pretty (encodePretty)
import           Data.Aeson.Types (Parser)
import qualified Data.ByteString
import qualified Data.ByteString.Lazy as B
import qualified Data.ByteString.Lazy.Char8 as Char8
import qualified Data.Char as Char
import qualified Data.Csv as C
import           Data.FileEmbed (embedFile)
import           Data.Map (Map)
import           Data.Set (Set)
import qualified Data.Set as S
import qualified Data.Map as M
import qualified Data.Text as T
import           Data.Maybe (catMaybes, maybeToList)
import qualified Data.Vector as V
import           Network.URI (parseURI)

import           Model.License
import           Collectors.Common

olLFC :: LicenseFactClassifier
olLFC = LFCWithURLAndLicense "https://github.com/Hitachi/open-license" (LFL "CDLA-Permissive-1.0") "Hitachi open-license"

objectWithoutEmpty :: [(Text, Value)] -> Value
objectWithoutEmpty = object . filter (\(_,v) -> v /= "")

{- #############################################################################
   #### Translatable ###########################################################
   ########################################################################## -}

data TranslationRow
  = TranslationRow String String
  deriving (Generic, Eq, Show)
instance C.FromNamedRecord TranslationRow where
  parseNamedRecord r = TranslationRow
    <$> r C..: "ja"
    <*> r C..: "en"
instance C.ToNamedRecord TranslationRow where
  toNamedRecord (TranslationRow ja en) = C.namedRecord  [ "ja" C..= ja, "en" C..= en ]
instance C.DefaultOrdered TranslationRow where
  headerOrder _ = V.fromList ["ja", "en"]

normalizeKey :: String -> String
normalizeKey = filter (not . Char.isSpace)

translations :: Map String (Maybe String)
translations = M.fromList . map (\(TranslationRow ja en) -> (normalizeKey ja
                                                            , case en of
                                                                ""  -> Nothing
                                                                en' -> Just en')) . V.toList $
  case (C.decodeByName (B.fromStrict translationsCSV) :: Either String (C.Header, V.Vector TranslationRow)) of
        Right (_, rows) -> rows
        Left err -> V.empty

class Translateable a where
  getTranslateables :: a -> Set String
  translate :: a -> a
translateString :: String -> Maybe String
translateString "" = Just ""
translateString ja = case (normalizeKey ja) `M.lookup` translations of
  Just v -> v
  _      -> Nothing

instance (Translateable a) => Translateable [a] where
  getTranslateables = S.unions . map getTranslateables
  translate = map translate
instance (Translateable a) => Translateable (Maybe a) where
  getTranslateables (Just a) = getTranslateables a
  getTranslateables Nothing  = S.empty
  translate (Just a) = Just (translate a)
  translate Nothing  = Nothing

{- #############################################################################
   #### Text ###################################################################
   ########################################################################## -}

data OlTextEntry
  = OlTextEntry String String
  deriving (Generic, Eq, Show)
instance FromJSON OlTextEntry where
  parseJSON = withObject "OlTextEntry" $ \v -> OlTextEntry
    <$> v .: "language"
    <*> v .: "text"
newtype OlText
  = OlText (Map String String)
  deriving (Generic, Eq)
instance Show OlText where
  show (OlText m) = let
    english = "en"
    in case M.toList m of
      (_, v):_ -> M.findWithDefault v english m
      _        -> ""
instance Translateable OlText where
  getTranslateables (OlText m) = case "ja" `M.lookup` m of
    Just v -> S.singleton v
    _      -> S.empty
  translate t@(OlText m) = let
      ja = M.findWithDefault "" "ja" m
      en = case "en" `M.lookup` m of
        Just "" -> Nothing
        en'     -> en'
    in case en of
      Just _ -> t
      _      -> case translateString ja of
        Just en' -> OlText $ M.insert "en" en' m
        Nothing  -> t
instance ToJSON OlText where
  toJSON olt = toJSON (show olt)
instance FromJSON OlText where
  parseJSON = let
    mkOlText :: [OlTextEntry] -> OlText
    mkOlText = OlText . M.fromList . filter (\(_,value) -> value /= "") . map (\(OlTextEntry key value) -> (key, value))
    in \v -> fmap mkOlText (parseJSON v :: Parser [OlTextEntry])
emptyOlText :: OlText
emptyOlText = OlText M.empty
cleanOlText :: OlText -> OlText
cleanOlText (OlText m) = OlText (M.filter (/= "") m)
isEmptyOlText :: OlText -> Bool
isEmptyOlText = (== emptyOlText) . cleanOlText
olTextToList :: OlText -> [String]
olTextToList t = case show t of
  "" -> []
  t' -> [t']

olTextToRLSR :: LFRaw a => a -> OlText -> RankedLicenseStatementResult String
olTextToRLSR ole t =
  case cleanOlText t of
    (OlText m) -> case "en" `M.lookup` m of
                    Just en -> mkRLSR ole 50 en
                    _       -> case "ja" `M.lookup` m of
                                 Just ja -> mkRLSR ole 10 ja
                                 _       -> NoRLSR

{- #############################################################################
   #### Wrapped ################################################################
   ########################################################################## -}

data DataWrapped a
  = DataWrapped { unwrap :: a }
  deriving (Generic)
unwrapList :: [DataWrapped a] -> [a]
unwrapList = map unwrap
instance (Translateable a) => Translateable (DataWrapped a) where
  getTranslateables (DataWrapped a) = getTranslateables a
  translate (DataWrapped a) = DataWrapped (translate a)
instance (ToJSON a) => ToJSON (DataWrapped a) where
  toJSON (DataWrapped a) = toJSON a
instance (FromJSON a) => FromJSON (DataWrapped a) where
  parseJSON = withObject "DataWrapped" $ \v -> DataWrapped
    <$> v .: "data"

{- #############################################################################
   #### Ref ####################################################################
   ########################################################################## -}

data OlRef
  = OlRef String
  deriving (Generic, Eq)
instance FromJSON OlRef where
  parseJSON = withObject "OlRef" $ \v -> OlRef
    <$> v .: "ref"

class OlRefable a where
  getRef :: a -> OlRef
  matchesRef :: a -> OlRef -> Bool
  matchesRef a ref = (getRef a) == ref
  getForOlRef :: [a] -> OlRef -> Maybe a
  getForOlRef list ref = case filter (`matchesRef` ref) list of
    a:_ -> Just a
    _   -> Nothing
  getForOlRefs :: [a] -> [OlRef] -> [a]
  getForOlRefs list = catMaybes . map (getForOlRef list)

{- #############################################################################
   #### Action #################################################################
   ########################################################################## -}

data OlAction
  = OlAction
  { _action_schemaVersion :: String
  , _action_uri :: URL
  , _action_baseUri :: URL
  , _action_id :: String
  , _action_name :: OlText
  , _action_description :: OlText
  } deriving (Generic, Eq)
instance Show OlAction where
  show a = unwords (show (_action_name a) : (map (\d -> "(" ++ d ++ ")") (olTextToList (_action_description a))))
instance Translateable OlAction where
  getTranslateables a = getTranslateables (_action_name a) `S.union` getTranslateables (_action_description a)
  translate a = a { _action_name = translate (_action_name a)
                  , _action_description = translate (_action_description a)}
instance ToJSON OlAction where
  toJSON a = objectWithoutEmpty [ "name" .= toJSON (_action_name a)
                                , "description" .= toJSON (_action_description a)
                                -- , "_id" .= _action_id a
                                ]
instance FromJSON OlAction where
  parseJSON = withObject "OlAction" $ \v -> OlAction
    <$> (fmap show (v .: "schemaVersion" :: Parser Double) :: Parser String)
    <*> v .: "uri"
    <*> v .: "baseUri"
    <*> v .: "id"
    <*> v .: "name"
    <*> v .: "description"
instance OlRefable OlAction where
  getRef = OlRef . _action_id

actions :: [OlAction]
actions = case eitherDecode (B.fromStrict actionsFile) of
            Right actions -> unwrapList actions
            Left err      -> trace ("ERR: Failed to parse actions JSON: " ++ err) []

{- #############################################################################
   #### Condition ##############################################################
   ########################################################################## -}

data OlConditionType
  = OBLIGATION -- must be fulfilled when actions are taken
  | RESTRICTION -- must be fulfilled after actions are taken
  | REQUISITE -- must be fulfilled before actions are taken
  deriving (Generic, Eq, Show)
instance ToJSON OlConditionType
instance FromJSON OlConditionType

data OlCondition
  = OlCondition
  { _condition_schemaVersion :: String
  , _condition_uri :: URL
  , _condition_baseUri :: URL
  , _condition_id :: String
  , _condition_conditionType :: OlConditionType
  , _condition_name :: OlText
  , _condition_description :: OlText
  } deriving (Generic, Eq)
instance Show OlCondition where
  show c = unwords ([ show (_condition_conditionType c) ++ ":"
                    , show (_condition_name c)
                    ] ++ map (\d -> "(" ++ d ++ ")") (olTextToList (_condition_description c)))
instance Translateable OlCondition where
  getTranslateables c = getTranslateables (_condition_name c) `S.union` getTranslateables (_condition_description c)
  translate c = c { _condition_name = translate (_condition_name c)
                  , _condition_description = translate (_condition_description c)}
instance ToJSON OlCondition where
  toJSON c = objectWithoutEmpty [ "name" .= toJSON (_condition_name c)
                                , "description" .= toJSON (_condition_description c)
                                , "type" .= toJSON (_condition_conditionType c)
                                -- , "_id" .= _condition_id c
                                ]
instance FromJSON OlCondition where
  parseJSON = withObject "OlCondition" $ \v -> OlCondition
    <$> (fmap show (v .: "schemaVersion" :: Parser Double) :: Parser String)
    <*> v .: "uri"
    <*> v .: "baseUri"
    <*> v .: "id"
    <*> v .: "conditionType"
    <*> v .: "name"
    <*> v .: "description"
instance OlRefable OlCondition where
  getRef = OlRef . _condition_id

conditions :: [OlCondition]
conditions = case eitherDecode (B.fromStrict conditionsFile) of
               Right conditions -> unwrapList conditions
               Left err      -> trace ("ERR: Failed to parse conditions JSON: " ++ err) []

{- #############################################################################
   #### ConditionTree ##########################################################
   ########################################################################## -}

data OlConditionTree
  = OlConditionTreeAnd [OlConditionTree]
  | OlConditionTreeOr [OlConditionTree]
  | OlConditionTreeLeaf OlCondition
  deriving (Generic, Eq)
addIndentation :: [String] -> [String]
addIndentation = map (unlines . (map ("  " ++)) . lines)
instance Show  OlConditionTree where
  show (OlConditionTreeAnd as) = concat ("AND\n": (addIndentation (map show as)))
  show (OlConditionTreeOr as)  = concat ("OR\n": (addIndentation (map show as)))
  show (OlConditionTreeLeaf a) = show a
instance Translateable OlConditionTree where
  getTranslateables (OlConditionTreeAnd as) = getTranslateables as
  getTranslateables (OlConditionTreeOr as)  = getTranslateables as
  getTranslateables (OlConditionTreeLeaf a) = getTranslateables a
  translate (OlConditionTreeAnd as) = OlConditionTreeAnd (translate as)
  translate (OlConditionTreeOr as)  = OlConditionTreeOr (translate as)
  translate (OlConditionTreeLeaf a) = OlConditionTreeLeaf (translate a)
instance ToJSON OlConditionTree where
  toJSON (OlConditionTreeAnd as) = object [ "AND" .=  toJSON as ]
  toJSON (OlConditionTreeOr as)  = object [ "OR" .= toJSON as ]
  toJSON (OlConditionTreeLeaf a) = toJSON a
instance FromJSON OlConditionTree where
  -- "conditionHead": {
  --   "type": "AND",
  --   "children": [
  --     {
  --       "type": "LEAF",
  --       "ref": "conditions/1"
  --     },
  --     {
  --       "type": "LEAF",
  --       "ref": "conditions/8"
  --     },
  --     {
  --       "type": "LEAF",
  --       "ref": "conditions/78"
  --     },
  --     {
  --       "type": "OR",
  --       "children": [
  --         {
  --           "type": "LEAF",
  --           "ref": "conditions/50"
  --         },
  --         {
  --           "type": "LEAF",
  --           "ref": "conditions/41"
  --         }
  --       ]
  --     }
  --   ]
  -- }
  parseJSON = let
      andParser, orParser, leafParser :: Object -> Parser OlConditionTree
      andParser v  = OlConditionTreeAnd
        <$> v .: "children"
      orParser v   = OlConditionTreeOr
        <$> v .: "children"
      emptyConditionTree :: OlConditionTree
      emptyConditionTree = OlConditionTreeAnd []
      leafParser v = fmap ((\case
                               Just con -> OlConditionTreeLeaf con
                               Nothing  -> emptyConditionTree)
                            . getForOlRef conditions)
                     (parseJSON (Object v) :: Parser OlRef)
    in withObject "OlConditionTree" $ \v -> do
      treeType <- v .: "type" :: Parser String
      case treeType of
         "AND"  -> andParser v
         "OR"   -> orParser v
         "LEAF" -> leafParser v
         _      -> undefined

{- #############################################################################
   #### Notice #################################################################
   ########################################################################## -}

data OlNotice
  = OlNotice
  { _notice_schemaVersion :: String
  , _notice_uri :: URL
  , _notice_baseUri :: URL
  , _notice_id :: String
  , _notice_content :: OlText
  , _notice_description :: OlText
  } deriving (Generic, Eq, Show)
instance Translateable OlNotice where
  getTranslateables n = getTranslateables (_notice_content n) `S.union` getTranslateables (_notice_description n)
  translate n = n { _notice_content = translate (_notice_content n)
                  , _notice_description = translate (_notice_description n)}
instance ToJSON OlNotice where
  toJSON n = objectWithoutEmpty [ "content" .= toJSON (_notice_content n)
                                , "description" .= toJSON (_notice_description n)
                                -- , "_id"         .= _notice_id n
                                ]
instance FromJSON OlNotice where
  parseJSON = withObject "OlNotice" $ \v -> OlNotice
    <$> (fmap show (v .: "schemaVersion" :: Parser Double) :: Parser String)
    <*> v .: "uri"
    <*> v .: "baseUri"
    <*> v .: "id"
    <*> v .: "content"
    <*> v .: "description"
instance OlRefable OlNotice where
  getRef = OlRef . _notice_id

notices :: [OlNotice]
notices = case eitherDecode (B.fromStrict noticesFile) of
               Right notices -> unwrapList notices
               Left err      -> trace ("ERR: Failed to parse notices JSON: " ++ err) []

{- #############################################################################
   #### License ################################################################
   ########################################################################## -}

data OlPermission
  = OlPermission
  { _permission_summary :: OlText
  , _permission_description :: OlText
  , _permission_actions :: [OlAction]
  , _permission_conditionHead :: Maybe OlConditionTree
  } deriving (Generic, Eq)
instance Show OlPermission where
  show p = let
      summary = map ("Summary: " ++) (olTextToList (_permission_summary p))
      description = map ("Description: " ++) (olTextToList (_permission_description p))
      actions = unlines ("Actions:" : (map (("- " ++) . show) (_permission_actions p)))
      conditions = case _permission_conditionHead p of
        Just cs -> ["Conditions:", show cs]
        Nothing -> ["Conditions: None"]
    in unlines (summary ++ description ++ [actions] ++ conditions)
instance Translateable OlPermission where
  getTranslateables p =
    getTranslateables (_permission_summary p)
    `S.union` getTranslateables (_permission_description p)
    `S.union` getTranslateables (_permission_actions p)
    `S.union` getTranslateables (_permission_conditionHead p)
  translate p = p { _permission_summary = translate (_permission_summary p)
                  , _permission_description = translate (_permission_description p)
                  , _permission_actions = translate (_permission_actions p)
                  , _permission_conditionHead = translate (_permission_conditionHead p)}
instance ToJSON OlPermission where
  toJSON p = objectWithoutEmpty [ "summary" .= toJSON (_permission_summary p)
                                , "description" .= toJSON (_permission_description p)
                                , "actions" .= toJSON (_permission_actions p)
                                , "conditions" .= _permission_conditionHead p
                                , "_str" .= show p
                                ]
instance FromJSON OlPermission where
  parseJSON = withObject "OlPermission" $ \v -> OlPermission
    <$> v .: "summary"
    <*> v .: "description"
    <*> (fmap (getForOlRefs actions) (v .: "actions" :: Parser [OlRef]) :: Parser [OlAction])
    <*> v .:? "conditionHead"
prettyPrintPermissions :: [OlPermission] -> String
prettyPrintPermissions = Char8.unpack . encodePretty

data OlLicense
 = OlLicense
 { _license_schemaVersion :: String
 , _license_uri :: URL
 , _license_baseUri :: URL
 , _license_id :: String
 , _license_name :: LicenseName
 , _license_summary :: OlText
 , _license_description :: OlText
 , _license_permissions :: [OlPermission]
 , _license_notices :: [OlNotice]
 , _license_content :: Text
 } deriving (Generic, Eq, Show)
instance Translateable OlLicense where
  getTranslateables l =
    getTranslateables (_license_summary l)
    `S.union` getTranslateables (_license_description l)
    `S.union` getTranslateables (_license_permissions l)
    `S.union` getTranslateables (_license_notices l)
  translate l = l
    { _license_summary = translate (_license_summary l)
    , _license_description = translate (_license_description l)
    , _license_permissions = translate (_license_permissions l)
    , _license_notices = translate (_license_notices l) }
instance ToJSON OlLicense where
  toJSON l = objectWithoutEmpty [ "name"           .= toJSON (_license_name l)
                                , "summary"        .= toJSON (_license_summary l)
                                , "description"    .= toJSON (_license_description l)
                                , "permissions"    .= toJSON (_license_permissions l)
                                , "notices"        .= toJSON (_license_notices l)
                                , "content"        .= toJSON (_license_content l)
                                -- , "_id"         .= _license_id l
                                ]
instance FromJSON OlLicense where
  parseJSON = withObject "OlLicense" $ \v -> OlLicense
    <$> (fmap show (v .: "schemaVersion" :: Parser Double) :: Parser String)
    <*> v .: "uri"
    <*> v .: "baseUri"
    <*> v .: "id"
    <*> v .: "name"
    <*> v .: "summary"
    <*> v .: "description"
    <*> v .: "permissions"
    <*> (fmap (getForOlRefs notices) (v .: "notices" :: Parser [OlRef]) :: Parser [OlNotice])
    <*> fmap (T.filter (/= '\r')) (v .: "content" :: Parser Text)

instance LicenseFactClassifiable OlLicense where
  getLicenseFactClassifier _ = olLFC
instance LFRaw OlLicense where
  getLicenseFactVersion ole = LFVersion "429ef37c6f3f057e724b04db0a6cd94fa1aa2db9"
  getImpliedNames ole       = CLSR (_license_name ole : (fixName (_license_name ole)))
  getImpliedFullName ole    = mkRLSR ole 40 (_license_name ole)
  getImpliedURLs ole        = CLSR [(Just "open-license", _license_uri ole)]
  getImpliedText ole        = mkRLSR ole 30 (_license_content ole)
  getImpliedComments ole    = let
      permsL = case _license_permissions ole of
        [] -> []
        ps -> [prettyPrintPermissions ps]
    in case (concat [ olTextToList (_license_summary ole)
                          , olTextToList (_license_description ole)
                          ]) of
         [] -> NoSLSR
         cs -> mkSLSR ole cs
  -- getImpliedDescription ole = case olTextToRLSR ole (_license_description ole) of
  --   NoRLSR -> olTextToRLSR ole (_license_summary ole)
  --   rlsr   -> rlsr

licenses :: [OlLicense]
licenses = case eitherDecode (B.fromStrict licensesFile) of
             Right lics -> unwrapList lics
             Left err   -> trace ("ERR: Failed to parse licenses JSON: " ++ err) []

{- #############################################################################
   #### general ################################################################
   ########################################################################## -}

loadOpenLicenseFacts :: IO Facts
loadOpenLicenseFacts = let
    toFact lic = LicenseFact (Just (_license_uri lic)) lic
  in logThatFactsWithNumberAreLoadedFrom "Hitachi open-license" $ do
  (return . V.map toFact . V.map translate . V.fromList) licenses

loadOpenLicenseTranslateables :: [TranslationRow]
loadOpenLicenseTranslateables = (map (\t -> TranslationRow t (case translateString t of
                                                                Nothing -> ""
                                                                Just en -> en))
                                  . filter (\s -> not ((length s < 100) && (isJust $ parseURI s)))
                                  . S.toList
                                  . getTranslateables) licenses

{- #############################################################################
   #### fixes ##################################################################
   ########################################################################## -}

nameFixesRaw :: [(LicenseName, [LicenseName])]
nameFixesRaw =
  [ ("Ruby", ["Ruby License (1.9.2 and earlier)", "Ruby License (1.9.3 and later)"])
  , ("EPL-1.0", ["Eclipse Public License 1.0"])
  , ("MPL-1.0", ["Mozilla Public License Version 1.0"])
  , ("MPL-1.1", ["Mozilla Public License Version 1.1"])
  , ("MPL-2.0", ["Mozilla Public License Version 2.0"])
  , ("CDDL-1.0", ["COMMON DEVELOPMENT AND DISTRIBUTION LICENSE Version 1.0 governed by the laws of the State of California"])
  , ("CDDL-1.1", ["COMMON DEVELOPMENT AND DISTRIBUTION LICENSE Version 1.1"])
  , ("CPL-1.0", ["Common Public License Version 1.0"])
  , ("ANTLR-PD", ["ANTLR 2 License"])
  , ("APSL-1.1", ["APPLE PUBLIC SOURCE LICENSE, Version 1.1"])
  , ("AFL-2.1", ["Academic Free License Version 2.1"])
  , ("Artistic-1.0", ["Artistic License (Perl) 1.0"])
  -- , ("", ["Artistic License"])
  , ("BSD-2-Clause", ["BSD 2-Clause \"Simplified\" or \"FreeBSD\" License"])
  , ("BSL-1.0", ["Boost Software License - Version 1.0"])
  , ("CNRI-Python", ["CNRI LICENSE AGREEMENT FOR PYTHON 1.6.1"]) -- ??
  , ("CPAL-1.0", ["Common Public Attribution License Version 1.0"])
  , ("CC-BY-NC-ND-4.0", ["Creative Commons Attribution-NoDerivatives 4.0 International"])
  , ("CC-BY-NC-ND-2.5", ["Creative Commons Attribution-NoDerivs 2.5 Generic"])
  , ("CC-BY-NC-ND-3.0", ["Creative Commons Attribution-NoDerivs 3.0 Unported"])
  , ("CC-BY-NC-SA-3.0", ["Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported"])
  , ("CC-BY-NC-SA-4.0", ["Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International"])
  , ("CC-BY-SA-1.0", ["Creative Commons Attribution-ShareAlike 1.0 Generic"])
  , ("CC-BY-SA-2.0", ["Creative Commons Attribution-ShareAlike 2.0 Generic"])
  , ("CC-BY-SA-2.5", ["Creative Commons Attribution-ShareAlike 2.5"])
  , ("CC-BY-SA-3.0", ["Creative Commons Attribution-ShareAlike 3.0 Unported"])
  , ("CC-BY-SA-4.0", ["Creative Commons Attribution-ShareAlike 4.0 International"])
  , ("CC0-1.0", ["Creative Commons CC0 1.0 Universal"])
  , ("CC-PDDC", ["Creative Commons Copyright-Only Dedication (based on United States law) or Public Domain Certification"])
  , ("CC-BY-SA-1.0", ["Creative Commons ShareAlike 1.0 Generic"]) -- ??
  , ("CC-BY-NC-1.0", ["Creative Comnons Attribution-NonCommercial 1.0 Generic"]) -- TYPO!
  , ("CC-BY-NC-ND-3.0", ["Creative Comnons Attribution-NonCommercial-NoDerivs 3.0 Unported"]) -- TYPO!
  , ("ErlPL-1.1", ["ERLANG PUBLIC LICENSE Version 1.1"])
  , ("EPL-2.0", ["Eclipse Public License - v 2.0"])
  , ("EUPL-1.1", ["European Union Public Licence, v.1.1"])
  , ("GL2PS", ["GL2PS LICENSE, Version 2"])
  , ("GFDL-1.1", ["GNU Free Documentation License Version 1.1"])
  , ("GFDL-1.2", ["GNU Free Documentation License Version 1.2"])
  , ("GFDL-1.3", ["GNU Free Documentation License Version 1.3"])
  , ("ICU", ["ICU License (ICU 1.8.1 and later)"])
  , ("IJG", ["IJG License"])
  , ("Interbase-1.0", ["INTERBASE PUBLIC LICENSE, Version 1.0 by \"Borland Software Corporation\""])
  , ("IPA", ["IPA Font License Agreement v1.0"])
  , ("Info-ZIP", ["Info-ZIP copyright and license (version 2005-Feb-10)"])
  , ("Info-ZIP", ["Info-ZIP license (Version 2007-Mar-04)"])
  , ("Info-ZIP", ["Info-ZIP license (version 2009-Jan-02)"])
  -- , ("", ["Initial Developer's Public License Version 1.0"]) -- ??
  , ("Intel", ["Intel License Agreement"]) -- ??
  , ("Interbase-1.0", ["InterBase Public License, Version 1.0"])
  , ("JasPer-2.0", ["JasPer License Version 2.0"])
  -- , ("", ["Microsoft Limited Public License"]) -- ??
  -- , ("", ["Microsoft Permissive License"]) -- ??
  -- , ("", ["Microsoft Platform and Application License"])
  , ("NetCDF", ["NetCDF Copyright"])
  , ("NetCDF", ["NetCDF Copyright(version 2009)"])
  , ("NPL-1.1", ["Netscape Public License Version 1.1"])
  , ("BSD-3-Clause-Open-MPI", ["Open MPI License"])
  , ("PHP-3.0", ["PHP License, version 3.0"])
  , ("PHP-3.01", ["PHP License, version 3.01"])
  , ("Python-2.0", ["PYTHON SOFTWARE FOUNDATION LICENSE VERSION 2"])
  , ("QPL-1.0", ["Q PUBLIC LICENSE version 1.0"])
  , ("Sendmail", ["SENDMAIL LICENSE (version 1998)"])
  , ("Sendmail", ["SENDMAIL LICENSE (version 2004)"])
  , ("Sendmail", ["SENDMAIL LICENSE (version 2012)"])
  , ("SGI-B-1.1", ["SGI FREE SOFTWARE LICENSE B (Version 1.1 [02/22/2000])"])
  , ("SGI-B-2.0", ["SGI FREE SOFTWARE LICENSE B (Version 2.0, Sept. 18, 2008)"])
  , ("OFL-1.0", ["SIL OPEN FONT LICENSE Version 1.0 - 22 November 2005"])
  , ("OFL-1.1", ["SIL OPEN FONT LICENSE Version 1.1 - 26 February 2007"])
  , ("SISSL-1.2", ["Sun Industry Standards Source License - Version 1.2"])
  , ("SISSL", ["Sun Industry Standards Source License Version 1.1"])
  , ("TMate", ["TMate Open Source License for \"TMate JavaSVN library\""])
  , ("Artistic-2.0", ["The Artistic License 2.0"])
  , ("OLDAP-2.7", ["The OpenLDAP Public License"]) -- ??
  , ("bzip2-1.0.6", ["The bzip2 license"]) -- ??
  , ("Unicode-DFS-2015", ["UNICODE, INC. LICENSE AGREEMENT - DATA FILES AND SOFTWARE (since 2016)"])
  , ("Unicode-DFS-2016", ["UNICODE, INC. LICENSE AGREEMENT - DATA FILES AND SOFTWARE"])
  , ("VSL-1.0", ["Vovida Software License, Version 1.0"])
  , ("W3C-20150513", ["W3C SOFTWARE AND DOCUMENT NOTICE AND LICENSE (become active on May 13, 2015)"])
  , ("W3C-19980720", ["W3C SOFTWARE NOTICE AND LICENSE (became active on August 14 1998)"])
  , ("W3C", ["W3C Software Notice and License (became active on December 31 2002)"])
  , ("XFree86-1.0", ["XFree86 1.0 License"])
  , (" Zend-2.0", ["Zend Engine License, Version 2.00"])
  , ("ZPL-1.0", ["Zope Public License (ZPL) Version 1.0"])
  , ("ZPL-2.0", ["Zope Public License (ZPL) Version 2.0"])
  , ("ZPL-2.1", ["Zope Public License (ZPL) Version 2.1"])
  , ("gSOAP-1.3b", ["gSOAP Public License Version 1.3b"])
  , ("Libpng", ["libpng license (libpng-1.2.6 and later)"]) -- ??  libpng-2.0
  , ("wxWindows", ["wxWindows Library Licence, Version 3.1"])
  ]
nameFixes :: Map LicenseName LicenseName
nameFixes = M.fromList (concatMap (\(s, ns) -> map (\n -> (n, s)) ns) nameFixesRaw)
fixName :: LicenseName -> [LicenseName]
fixName = maybeToList . (`M.lookup` nameFixes)

{- #############################################################################
   #### files ##################################################################
   ########################################################################## -}

actionsFile :: Data.ByteString.ByteString
actionsFile = $(embedFile "data/hitachi-open-license/actions.json")
conditionsFile :: Data.ByteString.ByteString
conditionsFile = $(embedFile "data/hitachi-open-license/conditions.json")
noticesFile :: Data.ByteString.ByteString
noticesFile = $(embedFile "data/hitachi-open-license/notices.json")
licensesFile :: Data.ByteString.ByteString
licensesFile = $(embedFile "data/hitachi-open-license/licenses.json")
translationsCSV :: Data.ByteString.ByteString
translationsCSV = $(embedFile "data/hitachi-open-license/translations.csv")
