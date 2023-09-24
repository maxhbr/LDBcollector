{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE TemplateHaskell #-}

module Ldbcollector.Source.ChooseALicense
  ( ChooseALicense (..),
  )
where

import Data.List.Split qualified as Split
import Data.Vector qualified as V
import Data.Yaml qualified as Y
import Ldbcollector.Model hiding (ByteString)
import Text.Blaze.Html5 qualified as H

data CALData = CALData
  { _id :: Maybe LicenseName,
    _name :: Maybe LicenseName,
    _title :: Maybe LicenseName,
    _spdxId :: Maybe LicenseName,
    _nickname :: Maybe LicenseName,
    _featured :: Maybe Bool,
    _hidden :: Maybe Bool,
    _description :: Maybe Text,
    _how :: Maybe Text,
    _cal_permissions :: [Text],
    _cal_conditions :: [Text],
    _cal_limitations :: [Text]
    --   , _content :: ByteString
  }
  deriving (Show, Eq, Ord, Generic)

instance FromJSON CALData where
  parseJSON = withObject "CALData" $ \v ->
    CALData
      <$> pure Nothing
      <*> v .:? "name"
      <*> v .:? "title"
      <*> (fmap (setNS "spdx") <$> v .:? "spdx-id")
      <*> v .:? "nickname"
      <*> v .:? "featured"
      <*> v .:? "hidden"
      <*> v .:? "description"
      <*> v .:? "how"
      <*> v .:? "permissions" .!= []
      <*> v .:? "conditions" .!= []
      <*> v .:? "limitations" .!= []

instance ToJSON CALData

instance LicenseFactC CALData where
  getType _ = "ChooseALicense"
  getApplicableLNs (CALData {_id = id, _name = name, _spdxId = spdxId, _title = title, _nickname = nickname}) =
    case catMaybes [id, spdxId, name, title] of
      best : others -> LN best `AlternativeLNs` map LN others `ImpreciseLNs` map LN (maybeToList nickname)
      _ -> undefined
  getImpliedStmts
    caldata@( CALData
                { _cal_permissions = permissions,
                  _cal_conditions = conditions,
                  _cal_limitations = limitations
                }
              ) =
      map
        (MaybeStatement . fmap LicenseComment)
        [ _description caldata,
          _how caldata
        ]
        ++ [LicensePCLR (PCLR permissions conditions limitations [])]
  toMarkup
    ( CALData
        { _id = id,
          _name = name,
          _title = title,
          _spdxId = spdxId,
          _nickname = nickname,
          _featured = featured,
          _hidden = hidden,
          _description = description,
          _how = how,
          _cal_permissions = cal_permissions,
          _cal_conditions = cal_conditions,
          _cal_limitations = cal_limitations
        }
      ) = do
      case description of
        Just description' -> H.span (H.toMarkup description')
        Nothing -> pure ()
      H.h5 "Permissions"
      H.ul $ mapM_ (H.li . H.toMarkup) cal_permissions
      H.h5 "Conditions"
      H.ul $ mapM_ (H.li . H.toMarkup) cal_conditions
      H.h5 "Limitations"
      H.ul $ mapM_ (H.li . H.toMarkup) cal_limitations

newtype ChooseALicense
  = ChooseALicense FilePath

readTxt :: FilePath -> IO (Maybe CALData)
readTxt txt = do
  logFileReadIO txt
  let fromFilename = takeBaseName (takeBaseName txt)
  contents <- readFile txt
  let contentLines = lines contents
  let parts = (map unlines . Split.splitOn ["---"]) contentLines

  case parts of
    _ : yaml : others -> do
      case Y.decodeEither' ((fromString . ("---\n" ++)) yaml) of
        Left err -> do
          debugLogIO (show err)
          return Nothing
        Right calData -> return (Just calData {_id = Just ((newNLN "cal" . pack) fromFilename)})
    _ -> return Nothing -- (return . Add . LicenseName . fromString) fromFilename

instance HasOriginalData ChooseALicense where
  getOriginalData (ChooseALicense dir) =
    FromUrl "https://choosealicense.com" $
      FromUrl "https://github.com/github/choosealicense.com/" $
        FromFile dir NoPreservedOriginalData

instance Source ChooseALicense where
  getSource _ = Source "ChooseALicense"
  getSourceDescription _ = Just "ChooseALicense.com aims to provide **accurate**, **non-judgmental**, and **understandable** information about popular **open source licenses** in order to **help people make informed decisions** about the projects they start, maintain, contribute to, and use."
  getFacts (ChooseALicense dir) = do
    txts <- glob (dir </> "*.txt")
    V.fromList . map wrapFact . catMaybes <$> mapM readTxt txts
