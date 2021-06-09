{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE TemplateHaskell #-}
module Collectors.FOSSLight
  ( loadFOSSLightFacts
  , fossLightLFC
  ) where

import qualified Prelude as P
import           MyPrelude
import           Collectors.Common

import qualified Data.Text as T
import qualified Data.Text.Encoding.Error as T
import qualified Data.Vector as V
import qualified Data.ByteString.Lazy as B
import qualified Data.Map as Map
import           Control.Applicative
import           Control.Exception (handle)
import           Data.Csv as C
import           Data.Aeson as A
import           Data.FileEmbed (embedFile)
import qualified Database.SQLite.Simple as S
import qualified Database.SQLite.Simple.FromRow as S
import qualified Database.SQLite.Simple.FromField as S
import qualified Database.SQLite.Simple.Types as S
import qualified Database.SQLite.Simple.Internal as S
import qualified Database.SQLite.Simple.Ok as S
import qualified System.IO as IO
import qualified System.IO.Temp as IO

import           Model.License

-- CREATE TABLE `LICENSE_NICKNAME` (
--   `LICENSE_NAME` varchar(200) NOT NULL COMMENT '라이선스 NAME',
--   `LICENSE_NICKNAME` varchar(200) NOT NULL COMMENT '라이선스 닉네임',
--   PRIMARY KEY (`LICENSE_NAME`,`LICENSE_NICKNAME`)
-- ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
data FOSSLight_Nick
  = FOSSLight_Nick LicenseName LicenseName
  deriving (Show)
instance S.FromRow FOSSLight_Nick where
    fromRow = FOSSLight_Nick <$> S.field <*> S.field


-- ('201', 'CP', 'Copyleft', '', '', 3, 'Y'),
-- ('201', 'NA', 'Proprietary', '', '', 4, 'Y'),
-- ('201', 'PF', 'Proprietary Free', '', '', 5, 'Y'),
-- ('201', 'PMS', 'Permissive', '', '', 1, 'Y'),
-- ('201', 'WCP', 'Weak Copyleft', '', '', 2, 'Y'),
data FOSSLight_License_Type
  = FOSSLight_License_Type_Copyleft
  | FOSSLight_License_Type_Proprietary
  | FOSSLight_License_Type_Proprietary_Free
  | FOSSLight_License_Type_Permissive
  | FOSSLight_License_Type_Weak_Copyleft
  | FOSSLight_License_Type_UNKNOWN
  deriving (Show)
instance S.FromField FOSSLight_License_Type where
  fromField f@(S.Field (S.SQLText txt) _) = case T.unpack txt of
    "CP"  -> S.Ok FOSSLight_License_Type_Copyleft
    "NA"  -> S.Ok FOSSLight_License_Type_Proprietary
    "PF"  -> S.Ok FOSSLight_License_Type_Proprietary_Free
    "PMS" -> S.Ok FOSSLight_License_Type_Permissive
    "WCP" -> S.Ok FOSSLight_License_Type_Weak_Copyleft
    _     -> S.returnError S.ConversionFailed f "failed to parse FOSSLight_License_Type"


--     CREATE TABLE `LICENSE_MASTER` (
--  1    `LICENSE_ID` int(11) NOT NULL AUTO_INCREMENT COMMENT '라이선스ID',
--  2    `LICENSE_NAME` varchar(200) NOT NULL COMMENT '라이선스 명',
--  3    `LICENSE_TYPE` varchar(6) NOT NULL COMMENT '라이선스 종류',
--  4    `OBLIGATION_DISCLOSING_SRC_YN` char(1) DEFAULT 'N' COMMENT '소스코드공개여부',
--  5    `OBLIGATION_NOTIFICATION_YN` char(1) DEFAULT 'N' COMMENT '고지여부',
--  6    `OBLIGATION_NEEDS_CHECK_YN` char(1) DEFAULT 'N' COMMENT '추후확인필요여부',
--  7    `SHORT_IDENTIFIER` varchar(100) DEFAULT NULL COMMENT '라이선스 약어(SPDX기준인 경우만 설정)',
--  8    `WEBPAGE` varchar(2000) DEFAULT NULL COMMENT '라이선스를 만든 기관에서 제공하는 WEB PAGE 주소',
--  9    `DESCRIPTION` text DEFAULT NULL COMMENT '부가설명 및 collab link등',
-- 10    `LICENSE_TEXT` mediumtext DEFAULT NULL COMMENT '라이선스 원문',
-- 11    `ATTRIBUTION` text DEFAULT NULL COMMENT '고지문구 추가 사항',
-- 12    `USE_YN` char(1) DEFAULT 'Y' COMMENT '사용여부',
-- 13    `CREATOR` varchar(50) DEFAULT NULL COMMENT '등록자',
-- 14    `CREATED_DATE` datetime DEFAULT current_timestamp() COMMENT '등록일',
-- 15    `MODIFIER` varchar(50) DEFAULT NULL COMMENT '수정자',
-- 16    `MODIFIED_DATE` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT '수정일',
-- 17    `REQ_LICENSE_TEXT_YN` char(1) DEFAULT 'N' COMMENT 'LICENSE TEXT 필수 입력 여부, MIT LIKE, BSD LIKE만 적용',
-- 18    `RESTRICTION` varchar(100) DEFAULT NULL,
--       PRIMARY KEY (`LICENSE_ID`),
--       KEY `idx_LICENSE_NAME` (`LICENSE_NAME`),
--       KEY `USE_YN` (`USE_YN`)
--     ) ENGINE=InnoDB AUTO_INCREMENT=672 DEFAULT CHARSET=utf8;
data FOSSLight_License
  = FOSSLight_License
  { _fossLight_id                        :: Int                     --  1    `LICENSE_ID` int(11) NOT NULL AUTO_INCREMENT COMMENT '라이선스ID',
  , _fossLight_name                      :: LicenseName             --  2    `LICENSE_NAME` varchar(200) NOT NULL COMMENT '라이선스 명',
  , _fossLight_type                      :: FOSSLight_License_Type  --  3    `LICENSE_TYPE` varchar(6) NOT NULL COMMENT '라이선스 종류',
  , _fossLight_OBLIGATION_DISCLOSING_SRC :: Bool                    --  4    `OBLIGATION_DISCLOSING_SRC_YN` char(1) DEFAULT 'N' COMMENT '소스코드공개여부',
  , _fossLight_OBLIGATION_NOTIFICATION   :: Bool                    --  5    `OBLIGATION_NOTIFICATION_YN` char(1) DEFAULT 'N' COMMENT '고지여부',
  , _fossLight_OBLIGATION_NEEDS_CHECK    :: Bool                    --  6    `OBLIGATION_NEEDS_CHECK_YN` char(1) DEFAULT 'N' COMMENT '추후확인필요여부',
  , _fossLight_SHORT_IDENTIFIER          :: Maybe LicenseName       --  7    `SHORT_IDENTIFIER` varchar(100) DEFAULT NULL COMMENT '라이선스 약어(SPDX기준인 경우만 설정)',
  , _fossLight_WEBPAGE                   :: () -- Maybe Text        --  8    `WEBPAGE` varchar(2000) DEFAULT NULL COMMENT '라이선스를 만든 기관에서 제공하는 WEB PAGE 주소',
  , _fossLight_DESCRIPTION               :: () -- Maybe Text        --  9    `DESCRIPTION` text DEFAULT NULL COMMENT '부가설명 및 collab link등',
  , _fossLight_LICENSE_TEXT              :: () -- Maybe Text        -- 10    `LICENSE_TEXT` mediumtext DEFAULT NULL COMMENT '라이선스 원문',
  , _fossLight_ATTRIBUTION               :: () -- Maybe Text        -- 11    `ATTRIBUTION` text DEFAULT NULL COMMENT '고지문구 추가 사항',
  , _fossLight_USE                       :: Bool                    -- 12    `USE_YN` char(1) DEFAULT 'Y' COMMENT '사용여부',
  , _fossLight_CREATOR                   :: ()                      -- 13    `CREATOR` varchar(50) DEFAULT NULL COMMENT '등록자',
  , _fossLight_CREATED_DATE              :: ()                      -- 14    `CREATED_DATE` datetime DEFAULT current_timestamp() COMMENT '등록일',
  , _fossLight_MODIFIER                  :: ()                      -- 15    `MODIFIER` varchar(50) DEFAULT NULL COMMENT '수정자',
  , _fossLight_MODIFIED_DATE             :: ()                      -- 16    `MODIFIED_DATE` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT '수정일',
  , _fossLight_REQ_LICENSE_TEXT          :: Bool                    -- 17    `REQ_LICENSE_TEXT_YN` char(1) DEFAULT 'N' COMMENT 'LICENSE TEXT 필수 입력 여부, MIT LIKE, BSD LIKE만 적용',
  , _fossLight_RESTRICTION               :: () -- Maybe Text        -- 18    `RESTRICTION` varchar(100) DEFAULT NULL,
  } deriving (Show)

instance S.FromField () where
  fromField _ = S.Ok ()

instance S.FromRow FOSSLight_License where
    fromRow = let
        ynToBool :: Maybe String -> Bool
        ynToBool (Just "Y") = True
        ynToBool _          = False
      in FOSSLight_License 
        <$> S.field
        <*> S.field
        <*> S.field
        <*> fmap ynToBool (S.field)
        <*> fmap ynToBool (S.field)
        <*> fmap ynToBool (S.field)
        <*> S.field
        <*> S.field
        <*> S.field
        <*> S.field
        <*> S.field
        <*> fmap ynToBool (S.field)
        <*> S.field
        <*> S.field
        <*> S.field
        <*> S.field
        <*> fmap ynToBool (S.field)
        <*> S.field

data FOSSLightFact
  = FOSSLightFact
  { _FOSSLightFact_License :: FOSSLight_License
  , _FOSSLightFact_Nicks :: [LicenseName]
  } deriving (Show)
instance ToJSON FOSSLightFact where
  toJSON (FOSSLightFact license _) =
    object [ "name" A..= _fossLight_name license ] -- TODO

fossLightLFC :: LicenseFactClassifier
fossLightLFC = LFCWithLicense (LFLWithURL "https://github.com/fosslight/fosslight/blob/main/LICENSE" "AGPL-3.0-only") "FOSSLight"
instance LicenseFactClassifiable FOSSLightFact where
  getLicenseFactClassifier _ = fossLightLFC

instance LFRaw FOSSLightFact where
  getImpliedNames (FOSSLightFact lic nicks)       = CLSR (_fossLight_name lic : (maybeToList (_fossLight_SHORT_IDENTIFIER lic) ++ nicks))
  getImpliedJudgement flf@(FOSSLightFact lic _)   = SLSR (getLicenseFactClassifier flf) $ case _fossLight_USE lic of
    True -> NeutralJudgement "This license is allowed for use at LG"
    False -> NegativeJudgement "This license is prohibited to use at LG"
  getImpliedFullName flf@(FOSSLightFact lic _)    = mkRLSR flf 20 $ _fossLight_name lic
  -- getImpliedURLs flf@(FOSSLightFact lic _)        = case _fossLight_WEBPAGE lic of
  --   Just webpage ->  CLSR [(Just "webpage", T.unpack webpage)]
  --   Nothing -> NoCLSR
  -- getImpliedText flf@(FOSSLightFact lic _)        = case _fossLight_LICENSE_TEXT lic of 
  --   Just txt -> mkRLSR flf 10 txt
  --   Nothing -> NoRLSR
  -- getImpliedDescription flf@(FOSSLightFact lic _) = case _fossLight_DESCRIPTION lic of
  --   Just desc -> mkRLSR flf 5 (T.unpack desc)
  --   Nothing -> NoRLSR
  getImpliedCopyleft flf@(FOSSLightFact lic _)    = case _fossLight_type lic of
    FOSSLight_License_Type_Copyleft -> mkSLSR flf StrongCopyleft
    FOSSLight_License_Type_Proprietary -> NoSLSR
    FOSSLight_License_Type_Proprietary_Free -> NoSLSR
    FOSSLight_License_Type_Permissive -> mkSLSR flf NoCopyleft
    FOSSLight_License_Type_Weak_Copyleft -> mkSLSR flf WeakCopyleft
    FOSSLight_License_Type_UNKNOWN -> NoSLSR

{-
 - ############################################################################################
 -}

licensesMasterSqlite :: ByteString
licensesMasterSqlite = B.fromStrict $(embedFile "data/fosslight/fosslight.sqlite.db")

loadFOSSLightFacts :: IO Facts
loadFOSSLightFacts = let
    extractLicensesFromSqlite :: FilePath -> IO.Handle -> IO ([FOSSLight_License],[FOSSLight_Nick])
    extractLicensesFromSqlite tmpfile hfile = do
      B.hPut hfile licensesMasterSqlite
      IO.hClose hfile
      conn <- S.open tmpfile
      license_names <- S.query_ conn "SELECT License_ID,LICENSE_NAME from LICENSE_MASTER" :: IO [(Int,LicenseName)]
      licenses <- fmap concat $
        mapM (\(i, name) -> do
          putStrLn $ "get License for id=" ++ show i ++ " name=" ++ name
          let 
              handleUnicodeException :: T.UnicodeException -> IO [FOSSLight_License]
              handleUnicodeException e = do
                print e
                return []
              handleResultError :: S.ResultError -> IO [FOSSLight_License]
              handleResultError e = do
                print e
                return []
              q = S.query_ conn ((S.Query . T.pack) $ "SELECT * from LICENSE_MASTER where LICENSE_ID=" ++ show i) :: IO [FOSSLight_License]
          handle handleUnicodeException . handle handleResultError $ q :: IO [FOSSLight_License]
          ) license_names
      nicks <- S.query_ conn "SELECT * from LICENSE_NICKNAME" :: IO [FOSSLight_Nick]
      S.close conn
      return (licenses, nicks)
  in do 
    logThatFactsAreLoadedFrom "FOSSLight"

    (licenses, nicks) <- IO.withSystemTempFile "fosslight.sqlite.db" extractLicensesFromSqlite
    let rawToFact = LicenseFact (Just "https://github.com/fosslight/fosslight/blob/main/install/db/fosslight_create.sql")
        rawFromLicense (license@FOSSLight_License { _fossLight_name = name } ) = let
            nicksForLicense = map (\(FOSSLight_Nick _ nick) -> nick) $ filter (\n@(FOSSLight_Nick name' _) -> name == name') nicks
          in FOSSLightFact license nicksForLicense
        facts = map (rawToFact . rawFromLicense) licenses

    logThatOneHasFoundFacts "FOSSLight" facts
    return (V.fromList facts)
