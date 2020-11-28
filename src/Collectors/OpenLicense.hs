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

import           Data.Aeson.Types (Parser)
import           Data.Aeson
import qualified Data.ByteString
import qualified Data.ByteString.Lazy as B
import qualified Data.Char as Char
import qualified Data.Csv as C
import           Data.FileEmbed (embedFile)
import           Data.Map (Map)
import           Data.Set (Set)
import qualified Data.Set as S
import qualified Data.Map as M
import           Data.Maybe (catMaybes)
import qualified Data.Vector as V
import           Network.URI (parseURI)

import           Model.License
import           Collectors.Common

olLFC :: LicenseFactClassifier
olLFC = LFCWithURLAndLicense "https://github.com/Hitachi/open-license" (LFL "CDLA-Permissive-1.0") "Hitachi open-license"

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
  } deriving (Generic, Eq, Show)
instance Translateable OlAction where
  getTranslateables a = getTranslateables (_action_name a) `S.union` getTranslateables (_action_description a)
  translate a = a { _action_name = translate (_action_name a)
                  , _action_description = translate (_action_description a)}
instance ToJSON OlAction where
  toJSON a = object [ "name" .= toJSON (_action_name a)
                    , "description" .= toJSON (_action_description a)
                    , "_id" .= _action_id a
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
  } deriving (Generic, Eq, Show)
instance Translateable OlCondition where
  getTranslateables c = getTranslateables (_condition_name c) `S.union` getTranslateables (_condition_description c)
  translate c = c { _condition_name = translate (_condition_name c)
                  , _condition_description = translate (_condition_description c)}
instance ToJSON OlCondition where
  toJSON c = object [ "name" .= toJSON (_condition_name c)
                    , "description" .= toJSON (_condition_description c)
                    , "type" .= toJSON (_condition_conditionType c)
                    , "_id" .= _condition_id c
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
  deriving (Generic, Eq, Show)
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
instance ToJSON OlNotice
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
  } deriving (Generic, Eq, Show)
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
  toJSON p = object [ "summary" .= toJSON (_permission_summary c)
                    , "description" .= toJSON (_permission_description c)
                    , "actions" .= toJSON (_permission_actions c)
                    , "conditions" .= _permission_conditionHead c
                    ]
instance FromJSON OlPermission where
  parseJSON = withObject "OlPermission" $ \v -> OlPermission
    <$> v .: "summary"
    <*> v .: "description"
    <*> (fmap (getForOlRefs actions) (v .: "actions" :: Parser [OlRef]) :: Parser [OlAction])
    <*> v .:? "conditionHead"

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
  toJSON l = object [ "name"        .= toJSON (_license_name l)
                    , "summary"     .= toJSON (_license_summary l)
                    , "description" .= toJSON (_license_description l)
                    , "permissions" .= toJSON (_license_permissions l)
                    , "notices"     .= toJSON (_license_notices l)
                    , "content"     .= toJSON (_license_content l)
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
    <*> v .: "content"

instance LicenseFactClassifiable OlLicense where
  getLicenseFactClassifier _ = olLFC
instance LFRaw OlLicense where
  getLicenseFactVersion ole = LFVersion "429ef37c6f3f057e724b04db0a6cd94fa1aa2db9"
  getImpliedNames ole       = CLSR [_license_name ole]
  getImpliedFullName ole    = mkRLSR ole 40 (_license_name ole)
  getImpliedURLs ole        = CLSR [(Just "open-license", _license_uri ole)]
  getImpliedText ole        = mkRLSR ole 30 (_license_content ole)
  getImpliedDescription ole = olTextToRLSR ole (_license_description ole)

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
