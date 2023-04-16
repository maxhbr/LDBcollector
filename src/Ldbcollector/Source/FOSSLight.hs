{-# LANGUAGE DeriveGeneric     #-}
{-# LANGUAGE LambdaCase        #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE TemplateHaskell   #-}
module Ldbcollector.Source.FOSSLight
  ( FOSSLight (..)
  ) where

import           Ldbcollector.Model

import           Control.Applicative
import           Control.Exception                (handle)
import           Data.Aeson                       as A
import qualified Data.ByteString.Lazy             as B
import           Data.Csv                         as C
import qualified Data.Map                         as Map
import qualified Data.Text                        as T
import qualified Data.Text.Encoding.Error         as T
import qualified Data.Vector                      as V
import qualified Database.SQLite.Simple           as S
import qualified Database.SQLite.Simple.FromField as S
import qualified Database.SQLite.Simple.FromRow   as S
import qualified Database.SQLite.Simple.Internal  as S
import qualified Database.SQLite.Simple.Ok        as S
import qualified Database.SQLite.Simple.Types     as S
import qualified System.IO                        as IO


instance S.FromField LicenseName where
    fromField = fmap newLN . S.fromField

-- CREATE TABLE `LICENSE_NICKNAME` (
--   `LICENSE_NAME` varchar(200) NOT NULL COMMENT '라이선스 NAME',
--   `LICENSE_NICKNAME` varchar(200) NOT NULL COMMENT '라이선스 닉네임',
--   PRIMARY KEY (`LICENSE_NAME`,`LICENSE_NICKNAME`)
-- ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
data FOSSLight_Nick
  = FOSSLight_Nick LicenseName LicenseName
  deriving (Show, Eq, Generic)
instance ToJSON FOSSLight_Nick
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
  deriving (Show, Eq, Generic)
instance S.FromField FOSSLight_License_Type where
  fromField f@(S.Field (S.SQLText txt) _) = case T.unpack txt of
    "CP"  -> S.Ok FOSSLight_License_Type_Copyleft
    "NA"  -> S.Ok FOSSLight_License_Type_Proprietary
    "PF"  -> S.Ok FOSSLight_License_Type_Proprietary_Free
    "PMS" -> S.Ok FOSSLight_License_Type_Permissive
    "WCP" -> S.Ok FOSSLight_License_Type_Weak_Copyleft
    _     -> S.returnError S.ConversionFailed f "failed to parse FOSSLight_License_Type"
instance ToJSON FOSSLight_License_Type
instance ToLicenseType FOSSLight_License_Type where
    toLicenseType FOSSLight_License_Type_Copyleft = Copyleft
    toLicenseType FOSSLight_License_Type_Proprietary = Proprietary
    toLicenseType FOSSLight_License_Type_Proprietary_Free = ProprietaryFree
    toLicenseType FOSSLight_License_Type_Permissive = Permissive
    toLicenseType FOSSLight_License_Type_Weak_Copyleft = WeaklyProtective
    toLicenseType FOSSLight_License_Type_UNKNOWN = UnknownLicenseType Nothing


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
  , _fossLight_WEBPAGE                   :: Maybe Text              --  8    `WEBPAGE` varchar(2000) DEFAULT NULL COMMENT '라이선스를 만든 기관에서 제공하는 WEB PAGE 주소',
  , _fossLight_DESCRIPTION               :: Maybe Text              --  9    `DESCRIPTION` text DEFAULT NULL COMMENT '부가설명 및 collab link등',
  , _fossLight_LICENSE_TEXT              :: Maybe Text              -- 10    `LICENSE_TEXT` mediumtext DEFAULT NULL COMMENT '라이선스 원문',
  , _fossLight_ATTRIBUTION               :: Maybe Text              -- 11    `ATTRIBUTION` text DEFAULT NULL COMMENT '고지문구 추가 사항',
  , _fossLight_USE                       :: Bool                    -- 12    `USE_YN` char(1) DEFAULT 'Y' COMMENT '사용여부',
  , _fossLight_CREATOR                   :: ()                      -- 13    `CREATOR` varchar(50) DEFAULT NULL COMMENT '등록자',
  , _fossLight_CREATED_DATE              :: ()                      -- 14    `CREATED_DATE` datetime DEFAULT current_timestamp() COMMENT '등록일',
  , _fossLight_MODIFIER                  :: ()                      -- 15    `MODIFIER` varchar(50) DEFAULT NULL COMMENT '수정자',
  , _fossLight_MODIFIED_DATE             :: ()                      -- 16    `MODIFIED_DATE` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT '수정일',
  , _fossLight_REQ_LICENSE_TEXT          :: Bool                    -- 17    `REQ_LICENSE_TEXT_YN` char(1) DEFAULT 'N' COMMENT 'LICENSE TEXT 필수 입력 여부, MIT LIKE, BSD LIKE만 적용',
  , _fossLight_RESTRICTION               :: Maybe Text              -- 18    `RESTRICTION` varchar(100) DEFAULT NULL,
  } deriving (Show, Eq, Generic)
instance ToJSON FOSSLight_License

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
        <*> fmap ynToBool S.field
        <*> fmap ynToBool S.field
        <*> fmap ynToBool S.field
        <*> S.field
        <*> S.field
        <*> S.field
        <*> S.field
        <*> S.field
        <*> fmap ynToBool S.field
        <*> S.field
        <*> S.field
        <*> S.field
        <*> S.field
        <*> fmap ynToBool S.field
        <*> S.field

data FOSSLightFact
  = FOSSLightFact
  { _FOSSLightFact_License :: FOSSLight_License
  , _FOSSLightFact_Nicks   :: [LicenseName]
  } deriving (Show, Eq, Generic)
instance ToJSON FOSSLightFact


instance LicenseFactC FOSSLightFact where
    getType _ = "FOSSLight"
    getApplicableLNs (FOSSLightFact license nicks) =
        LN (_fossLight_name license)
        `AlternativeLNs`
        map LN (maybeToList (_fossLight_SHORT_IDENTIFIER license))
        `ImpreciseLNs`
        map LN nicks
    getImpliedStmts (FOSSLightFact license _) = [LicenseType (toLicenseType (_fossLight_type license))]

newtype FOSSLight = FOSSLight FilePath

instance Source FOSSLight where
    getSource _ = Source "FOSSLight"
    getFacts (FOSSLight sqlite) = let
        extractLicensesFromSqlite :: IO ([FOSSLight_License],[FOSSLight_Nick])
        extractLicensesFromSqlite = do
          conn <- S.open sqlite
          license_names <- S.query_ conn "SELECT License_ID,LICENSE_NAME from LICENSE_MASTER" :: IO [(Int,LicenseName)]
          licenses <- concat <$>
            mapM (\(i, name) -> do
              let nameString = "id=" ++ show i ++ " name=" ++ show name
              debugLogIO $ "get License for " ++ nameString
              let
                  handleUnicodeException :: T.UnicodeException -> IO [FOSSLight_License]
                  handleUnicodeException e = do
                    debugLogIO (nameString ++ " error=" ++ show e)
                    return []
                  handleResultError :: S.ResultError -> IO [FOSSLight_License]
                  handleResultError e = do
                    debugLogIO (nameString ++ " error=" ++ show e)
                    return []
                  q = S.query_ conn ((S.Query . T.pack) $ "SELECT * from LICENSE_MASTER where LICENSE_ID=" ++ show i) :: IO [FOSSLight_License]
              handle handleUnicodeException . handle handleResultError $ q :: IO [FOSSLight_License]
              ) license_names
          nicks <- S.query_ conn "SELECT * from LICENSE_NICKNAME" :: IO [FOSSLight_Nick]
          S.close conn
          return (licenses, nicks)
      in do
        sqliteFileExists <- doesFileExist sqlite
        if sqliteFileExists
            then do
                (licenses, nicks) <- extractLicensesFromSqlite
                let rawFromLicense (license@FOSSLight_License { _fossLight_name = name } ) = let
                            nicksForLicense = map (\(FOSSLight_Nick _ nick) -> nick) $ filter (\n@(FOSSLight_Nick name' _) -> name == name') nicks
                        in FOSSLightFact license nicksForLicense
                    facts = map (wrapFact . rawFromLicense) licenses

                return (V.fromList facts)
            else do
                stderrLogIO ("missing file: " ++ sqlite)
                return mempty
