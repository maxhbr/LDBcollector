{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE QuasiQuotes #-}
{-
 - This module parses the tables from https://en.wikipedia.org/wiki/Comparison_of_free_and_open-source_software_licenses
 - it currently only parses the "general comparison" table which is added as quasi quoted string to the source code
 -}
module Collectors.Wikipedia
  ( loadWikipediaFacts
  ) where

import qualified Prelude as P
import           MyPrelude
import           Collectors.Common

import qualified Data.Text as T
import qualified Data.Vector as V
import qualified Data.ByteString.Lazy as B
import           Control.Applicative
import           Data.Csv hiding ((.=))
import qualified Data.Csv as C
import           Data.Aeson as A
import qualified Data.Map as M
import           Text.RawString.QQ

import           Model.License

{-
The following table compares various features of each license and is a general guide to the terms and conditions of each license. The table lists the permissions and limitations regarding the following subjects:

    Linking - linking of the licensed code with code licensed under a different license (e.g. when the code is provided as a library)
    Distribution - distribution of the code to third parties
    Modification - modification of the code by a licensee
    Patent grant - protection of licensees from patent claims made by code contributors regarding their contribution, and protection of contributors from patent claims made by licensees
    Private use - whether modification to the code must be shared with the community or may be used privately (e.g. internal use by a corporation)
    Sublicensing - whether modified code may be licensed under a different license (for example a copyright) or must retain the same license under which it was provided
    Trademark grant - use of trademarks associated with the licensed code or its contributors by a licensee
-}

wikipediaComparisonData :: ByteString
wikipediaComparisonData = [r|License,Author,Latest version,Publication date,Linking,Distribution,Modification,Patent grant,Private use,Sublicensing,TM grant
Academic Free License,Lawrence E. Rosen,3.0,2002,Permissive,Permissive,Permissive,Yes,Yes,Permissive,No
Affero General Public License,Affero Inc,2.0,2007,Copylefted,Copyleft except for the GNU AGPL,Copyleft,?,Yes,?,?
Apache License,Apache Software Foundation,2.0,2004,Permissive,Permissive,Permissive,Yes,Yes,Permissive,No
Apple Public Source License,Apple Computer,2.0,06.08.03,Permissive,?,Limited,?,?,?,?
Artistic License,Larry Wall,2.0,2000,With restrictions,With restrictions,With restrictions,No,Permissive,With restrictions,No
Beerware,Poul-Henning Kamp,42,1987,Permissive,Permissive,Permissive,No,Permissive,Permissive,No
BSD License,Regents of the University of California,3.0,?,Permissive,Permissive,Permissive,Manually,Yes,Permissive,Manually
Boost Software License,?,1.0,17.08.03,Permissive,?,Permissive,?,?,?,?
Creative Commons Zero,Creative Commons,1.0,2009,Public Domain,Public Domain,Public Domain,No,Public Domain,Public Domain,No
CC-BY,Creative Commons,4.0,2002,Permissive,Permissive,Permissive,No,Yes,Permissive,?
CC-BY-SA,Creative Commons,4.0,2002,Copylefted,Copylefted,Copylefted,No,Yes,No,?
CeCILL,CEA / CNRS / INRIA,2.1,"June 21, 2013",Permissive,Permissive,Permissive,No,Permissive,With restrictions,No
Common Development and Distribution License,Sun Microsystems,1.0,"December 1, 2004",Permissive,?,Limited,?,?,?,?
Common Public License,IBM,1.0,May 2001,Permissive,?,Copylefted,?,?,?,?
Cryptix General License,Cryptix Foundation,N/A,1995,Permissive,Permissive,Permissive,Manually,Yes,?,Manually
Eclipse Public License,Eclipse Foundation,2.0,24.08.17,Limited,Limited,Limited,Yes,Yes,Limited,Manually
Educational Community License,Indiana University,1.0,2007,Permissive,?,Permissive,?,?,?,?
European Union Public Licence,European Commission,1.2,May 2017,"Copylefted, with an explicit compatibility list","Copylefted, with an explicit compatibility list","Copylefted, with an explicit compatibility list",Yes,Yes,"Copylefted, with an explicit compatibility list",No
GNU Affero General Public License,Free Software Foundation,3.0,2007,GNU GPLv3 only,Copylefted,Copylefted,Yes,Copylefted,Copylefted,Yes
GNU General Public License,Free Software Foundation,3.0,June 2007,GPLv3 compatible only,Copylefted,Copylefted,Yes,Yes,Copylefted,Yes
GNU Lesser General Public License,Free Software Foundation,3.0,June 2007,With restrictions,Copylefted,Copylefted,Yes,Yes,Copylefted,Yes
IBM Public License,IBM,1.0,01.08.99,Copylefted,?,Copylefted,?,?,?,?
ISC license,Internet Systems Consortium,N/A,June 2003,Permissive,Permissive,Permissive,?,?,?,?
LaTeX Project Public License,LaTeX project,1.3c,?,Permissive,?,Permissive,?,?,?,?
Microsoft Public License,Microsoft,N/A,?,Permissive,Permissive,Permissive,No,Permissive,?,No
MIT license / X11 license,MIT,N/A,1988,Permissive,Permissive,Permissive,Manually,Yes,Permissive,Manually
Mozilla Public License,Mozilla Foundation,2.0,"January 3, 2012",Permissive,Copylefted,Copylefted,Yes,Yes,Copylefted,No
Netscape Public License,Netscape,1.1,?,Limited,?,Limited,?,?,?,?
Open Software License,Lawrence Rosen,3.0,2005,Permissive,Copylefted,Copylefted,Yes,Yes,Copylefted,?
OpenSSL license,OpenSSL Project,N/A,?,Permissive,?,Permissive,?,?,?,?
Python Software Foundation License,Python Software Foundation,2,?,Permissive,?,Permissive,?,?,?,?
Q Public License,Trolltech,?,?,Limited,?,Limited,?,?,?,?
Sleepycat License,Sleepycat Software,N/A,1996,Permissive,With restrictions,Permissive,No,Yes,No,No
Unlicense,unlicense.org,1,December 2010,Permissive/Public domain,Permissive/Public domain,Permissive/Public domain,?,Permissive/Public domain,Permissive/Public domain,?
W3C Software Notice and License,W3C,20021231,"December 31, 2002",Permissive,?,Permissive,?,?,?,?
Do What The Fuck You Want To Public License (WTFPL),"Banlu Kemiyatorn, Sam Hocevar",2,December 2004,Permissive/Public domain,Permissive/Public domain,Permissive/Public domain,No,Yes,Yes,No
XFree86 1.1 License,"The XFree86 Project, Inc",?,?,Permissive,?,Permissive,?,?,?,?
zlib/libpng license,Jean-Loup Gailly and Mark Adler,?,?,Permissive,?,Permissive,?,?,?,?
|]
-- "XCore Open Source License also separate \"Hardware License Agreement\"",XMOS,?,February 2011,Permissive,Permissive,Permissive,Manually,Yes,Permissive,?

tableToShortnameMapping :: Map (Text, Maybe Text) LicenseName
tableToShortnameMapping = M.fromList $ map (\((s1, s2), s3) -> ((s1, handleFieldToMaybe s2), s3))
  [ (("Academic Free License","3.0"), "AFL-3.0")
  , (("Affero General Public License","2.0"), "") -- AGPL-1.0-or-later ?
  , (("Apache License","2.0"), "Apache-2.0")
  , (("Apple Public Source License","2.0"), "") -- AML ?
  , (("Artistic License","2.0"), "Artistic-2.0")
  , (("Beerware","42"), "Beerware")
  , (("BSD License","3.0"), "") -- ?
  , (("Boost Software License","1.0"), "BSL-1.0")
  , (("Creative Commons Zero","1.0"), "CC0-1.0")
  , (("CC-BY","4.0"), "CC-BY-4.0")
  , (("CC-BY-SA","4.0"), "CC-BY-SA-4.0")
  , (("CeCILL","2.1"), "CeCILL-2.1")
  , (("Common Development and Distribution License","1.0"), "CDDL-1.0")
  , (("Common Public License","1.0"), "CPL-1.0")
  , (("Cryptix General License","N/A"), "") -- ?
  , (("Eclipse Public License","2.0"), "EPL-2.0")
  , (("Educational Community License","1.0"), "ECL-1.0")
  , (("European Union Public Licence","1.2"), "EUPL-1.2")
  , (("GNU Affero General Public License","3.0"), "AGPL-3.0-or-later")
  , (("GNU General Public License","3.0"), "GPL-3.0-or-later")
  , (("GNU Lesser General Public License","3.0"), "LGPL-3.0-or-later")
  , (("IBM Public License","1.0"), "IPL-1.0")
  , (("ISC license","N/A"), "ISC")
  , (("LaTeX Project Public License","1.3c"), "") -- ?
  , (("Microsoft Public License","N/A"), "MS-PL")
  , (("MIT license / X11 license","N/A"), "MIT")
  , (("Mozilla Public License","2.0"), "MPL-2.0")
  , (("Netscape Public License","1.1"), "NPL-1.1")
  , (("Open Software License","3.0"), "OSL-1.0")
  , (("OpenSSL license","N/A"), "OpenSSL")
  , (("Python Software Foundation License","2"), "Python-2.0")
  , (("Q Public License","?"), "QPL-1.0")
  , (("Sleepycat License","N/A"), "Sleepycat")
  , (("Unlicense","1"), "Unlicense")
  , (("W3C Software Notice and License","20021231"), "W3C")
  , (("Do What The Fuck You Want To Public License (WTFPL)","2"), "WTFPL")
  , (("XCore Open Source License also separate \"Hardware License Agreement\"","?"), "") -- ?
  , (("XFree86 1.1 License","?"), "XFree86-1.1")
  , (("zlib/libpng license","?"), "Zlib")
  ]

getSPDXIdForWikipediaFact :: WikipediaFact -> Maybe LicenseName
getSPDXIdForWikipediaFact (WikipediaFact name _ version _ _ _ _ _ _ _ _) = (name, version) `M.lookup` tableToShortnameMapping

handleFieldToMaybe :: Text -> Maybe Text
handleFieldToMaybe ""    = Nothing
handleFieldToMaybe "?"   = Nothing
handleFieldToMaybe "N/A" = Nothing
handleFieldToMaybe t     = Just t

-- License,Author,Latest version,Publication date,Linking,Distribution,Modification,Patent grant,Private use,Sublicensing,TM grant
data WikipediaFact
  = WikipediaFact
  { wpfLicenseName :: Text
  , wpfLicenseAuthor :: Maybe Text
  , wpfLicenseVersion :: Maybe Text
  , wpfPublicationDate :: Maybe Text
  , wpfLinking :: Maybe Text
  , wpfDistribution :: Maybe Text
  , wpfModification :: Maybe Text
  , wpfPatentGrant :: Maybe Text
  , wpfPrivateUse :: Maybe Text
  , wpfSublicensing :: Maybe Text
  , wpfTMGrant :: Maybe Text
  } deriving (Show, Generic)
instance FromNamedRecord WikipediaFact where
  parseNamedRecord r = WikipediaFact <$> r C..: "License"
                                     <*> (fmap handleFieldToMaybe (r C..: "Author" :: Parser Text) :: Parser (Maybe Text))
                                     <*> (fmap handleFieldToMaybe (r C..: "Latest version" :: Parser Text) :: Parser (Maybe Text))
                                     <*> (fmap handleFieldToMaybe (r C..: "Publication date" :: Parser Text) :: Parser (Maybe Text))
                                     <*> (fmap handleFieldToMaybe (r C..: "Linking" :: Parser Text) :: Parser (Maybe Text))
                                     <*> (fmap handleFieldToMaybe (r C..: "Distribution" :: Parser Text) :: Parser (Maybe Text))
                                     <*> (fmap handleFieldToMaybe (r C..: "Modification" :: Parser Text) :: Parser (Maybe Text))
                                     <*> (fmap handleFieldToMaybe (r C..: "Patent grant" :: Parser Text) :: Parser (Maybe Text))
                                     <*> (fmap handleFieldToMaybe (r C..: "Private use" :: Parser Text) :: Parser (Maybe Text))
                                     <*> (fmap handleFieldToMaybe (r C..: "Sublicensing" :: Parser Text) :: Parser (Maybe Text))
                                     <*> (fmap handleFieldToMaybe (r C..: "TM grant" :: Parser Text) :: Parser (Maybe Text))
instance ToJSON WikipediaFact where
  toJSON wf = let
      nameToDescriptionMapping :: Map Text Text
      nameToDescriptionMapping = M.fromList [ ("Linking", "linking of the licensed code with code licensed under a different license (e.g. when the code is provided as a library)")
                                            , ("Distribution", "distribution of the code to third parties")
                                            , ("Modification", "modification of the code by a licensee")
                                            , ("Patent grant", "protection of licensees from patent claims made by code contributors regarding their contribution, and protection of contributors from patent claims made by licensees")
                                            , ("Private use", "whether modification to the code must be shared with the community or may be used privately (e.g. internal use by a corporation)")
                                            , ("Sublicensing", "whether modified code may be licensed under a different license (for example a copyright) or must retain the same license under which it was provided")
                                            , ("Trademark grant", "use of trademarks associated with the licensed code or its contributors by a licensee")
                                            ]
      -- generateEntry :: Text -> (Maybe Text) -> Maybe a
      generateEntry _ Nothing = Nothing
      generateEntry key (Just value) = Just $ key .= object [ "value" .= value, "description" .= (M.lookup key nameToDescriptionMapping)]
      mkLinkingEntry = generateEntry "Linking"  (wpfLinking wf)
      mkDistributionEntry = generateEntry "Distribution" (wpfDistribution wf)
      mkModificationEntry = generateEntry "Modification" (wpfModification wf)
      mkPatentGrantEntry = generateEntry "Patent grant" (wpfPatentGrant wf)
      mkPrivateUseEntry = generateEntry "Private use" (wpfPrivateUse wf)
      mkSublicensingEntry = generateEntry "Sublicensing" (wpfSublicensing wf)
      mkTMGrantEntry = generateEntry "Trademark grant" (wpfTMGrant wf)
    in object $ [ "Koordinaten" .= object [ "name" .= (wpfLicenseName wf)
                                          , "version" .= (wpfLicenseVersion wf)
                                          , "spdxId" .= (getSPDXIdForWikipediaFact wf)]
                , "Publication date" .= (wpfPublicationDate wf)
                ] ++ ( catMaybes [ mkLinkingEntry
                                 , mkDistributionEntry
                                 , mkModificationEntry
                                 , mkPatentGrantEntry
                                 , mkPrivateUseEntry
                                 , mkSublicensingEntry
                                 , mkTMGrantEntry
                                 ])
instance LFRaw WikipediaFact where
  getLicenseFactClassifier _ = LFC ["Wikipedia", "WikipediaComparison"]
  getImpliedNames wpf@(WikipediaFact name _ version _ _ _ _ _ _ _ _) = let
      nameByWikipedia = T.unpack $ case version of
        Just v  -> name `T.append` " " `T.append` v
        Nothing -> name
      nameInSPDXMap = getSPDXIdForWikipediaFact wpf
    in case nameInSPDXMap of
      Just spdxId -> [spdxId, nameByWikipedia]
      Nothing     -> [nameByWikipedia]

loadFactsFromComparisonByteString :: ByteString -> Facts
loadFactsFromComparisonByteString s = case (decodeByName s :: Either String (Header, V.Vector WikipediaFact)) of
                                        Right (_, v) -> V.map (LicenseFact "https://en.wikipedia.org/wiki/Comparison_of_free_and_open-source_software_licenses") v
                                        Left err     -> trace err V.empty

loadWikipediaFacts :: IO Facts
loadWikipediaFacts = do
  logThatFactsAreLoadedFrom "Wikipedia License Comparison Table"
  return $ loadFactsFromComparisonByteString wikipediaComparisonData
