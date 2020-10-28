{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE OverloadedStrings #-}
module Collectors.IfrOSS
  ( loadIfrOSSFacts
  , ifrOSSLFC
  , ifrOSSKindToText
  ) where

import qualified Prelude as P
import           MyPrelude hiding (id)

import qualified Data.Text as T
import qualified Data.Vector as V

import           Model.License
import           Collectors.Common

ifrOSSLFC :: LicenseFactClassifier
ifrOSSLFC = LFC "ifrOSS"
ifrOSSURL :: URL
ifrOSSURL = "https://ifross.github.io/ifrOSS/Lizenzcenter"

ifrOSSKindToText :: CopyleftKind -> Maybe String
ifrOSSKindToText StrongCopyleft = Just "Bei Lizenzen mit einem strengen Copyleft-Effekt wird der Lizenznehmer verpflichtet von der ursprünglichen Software abgeleitete Werke ebenfalls nur unter den Bedingungen der Ursprungslizenz weiterzuverbreiten."
ifrOSSKindToText WeakCopyleft   = Just "Lizenzen mit beschränktem Copyleft-Effekt haben ebenfalls einen Copyleft-Effekt, der aber nicht alle Berbeitungen und abgeleiteten Werke umfasst, sondern definierte Ausnahmen enthält."
ifrOSSKindToText SaaSCopyleft   = ifrOSSKindToText StrongCopyleft
ifrOSSKindToText Copyleft       = Just $ unwords [ fromJust $ ifrOSSKindToText StrongCopyleft
                                                 , fromJust $ ifrOSSKindToText WeakCopyleft]
ifrOSSKindToText MaybeCopyleft  = Nothing
ifrOSSKindToText NoCopyleft     = Just "Lizenzen ohne Copyleft-Effekt zeichnen sich dadurch aus, dass sie dem Lizenznehmer alle Freiheiten einer Open Source Lizenz einräumen und für Veränderungen der Software keine Bedingungen hinsichtlich des zu verwendenden Lizenztyps enthalten. Damit kann der Lizenznehmer veränderte Versionen der Software unter beliebigen Lizenzbedingungen weiterverbreiten, also auch in proprietäre Software überführen."

data IfrCopyleftKind
  = IfrStrongCopyleft
  | IfrStrongCopyleft_GPLlike
  | IfrWeakCopyleft
  | IfrWeakCopyleft_MPLlike
  | IfrLicenseWithChoice
  | IfrLicenseWithSpecialRights
  | IfrNoCopyleft
  deriving (Eq, Show, Generic)
instance ToJSON IfrCopyleftKind

ifrOSSIfrKindToText :: IfrCopyleftKind -> String
ifrOSSIfrKindToText IfrStrongCopyleft           = fromJust $ ifrOSSKindToText StrongCopyleft
ifrOSSIfrKindToText IfrStrongCopyleft_GPLlike   = unwords [ fromJust $ ifrOSSKindToText StrongCopyleft
                                                          , "Die hier aufgeführten Lizenzen enthalten die verschiedenen GPL-Versionen und davon abgeleitete Lizenztexte. Zudem finden sich hier einige GPL-Varianten mit Ausnahmeregelungen vom strengen Copyleft. Diese Lizenzen mit Ausnahmen können auch als beschränktes Copyleft verstanden werden."]
ifrOSSIfrKindToText IfrWeakCopyleft             = fromJust $ ifrOSSKindToText WeakCopyleft
ifrOSSIfrKindToText IfrWeakCopyleft_MPLlike     = unwords [ fromJust $ ifrOSSKindToText WeakCopyleft
                                                          , "Sofern Modifikationen der Software unter MPLartigen Lizenzen in eigenen Dateien realisiert werden, können diese Dateien auch unter anderen, z.B. proprietären Lizenzbedingungen weiterverbreitet werden. Damit soll die Kombination von Software unter verschiedenen Lizenztypen erleichtert werden."]
ifrOSSIfrKindToText IfrLicenseWithChoice        = "Diese Lizenzen sehen unterschiedliche rechtliche Folgen vor, je nachdem wie umfangreich eine Modifikation ist. Zudem werden dem Lizenznehmer verschiedene Wahlmöglichkeiten eingeräumt, wie Weiterentwicklungen weiterverbreitet werden können."
ifrOSSIfrKindToText IfrLicenseWithSpecialRights = "Die Lizenzen mit Sonderrechten gewähren den Lizenznehmern zwar alle diejenigen Rechte, die Freie Software ausmachen, sehen aber zugleich besondere Privilegien für den Lizenzgeber bei Weiterentwicklungen durch den Lizenznehmer vor. Diese Lizenzen werden zumeist bei Programmen verwendet, die ursprünglich proprietär vertrieben wurden."
ifrOSSIfrKindToText IfrNoCopyleft               = fromJust $ ifrOSSKindToText NoCopyleft

copyleftKindFromIfrOSSKind :: IfrCopyleftKind -> Maybe CopyleftKind
copyleftKindFromIfrOSSKind IfrStrongCopyleft           = Just StrongCopyleft
copyleftKindFromIfrOSSKind IfrStrongCopyleft_GPLlike   = Just StrongCopyleft
copyleftKindFromIfrOSSKind IfrWeakCopyleft             = Just WeakCopyleft
copyleftKindFromIfrOSSKind IfrWeakCopyleft_MPLlike     = Just WeakCopyleft
copyleftKindFromIfrOSSKind IfrLicenseWithChoice        = Just MaybeCopyleft
copyleftKindFromIfrOSSKind IfrLicenseWithSpecialRights = Nothing
copyleftKindFromIfrOSSKind IfrNoCopyleft               = Just NoCopyleft

data IfrOSSFact
  = IfrOSSFact
  { ifrName :: LicenseName
  , ifrId   :: Maybe LicenseName
  , ifrKind :: IfrCopyleftKind
  , ifrURL  :: URL
  }
  deriving (Show, Generic)
instance ToJSON IfrOSSFact
instance LicenseFactClassifiable IfrOSSFact where
  getLicenseFactClassifier _ = ifrOSSLFC
instance LFRaw IfrOSSFact where
  getImpliedNames i          = CLSR (ifrName i : maybeToList (ifrId i))
  getImpliedURLs i           = CLSR [(Nothing, ifrURL i)]
  getImpliedComments i       = mkSLSR i [ifrOSSIfrKindToText (ifrKind i)]
  getImpliedCopyleft i       = case copyleftKindFromIfrOSSKind (ifrKind i) of
    Just c  -> mkSLSR i c
    Nothing -> NoSLSR

rawIfrOSSFacts :: [IfrOSSFact]
rawIfrOSSFacts = let
    noCopyleftLics =
      [ (Nothing, "4Suite License (v. 1.1)", "https://web.archive.org/web/20060210220828/http://4suite.org/COPYRIGHT.doc")
      , (Nothing, "Academic Free License (AFL) (v. 1.0)", "https://web.archive.org/web/20020808082753/http://www.rosenlaw.com:80/afl.html")
      , (Nothing, "Academic Free License (AFL) (v. 1.1)", "https://web.archive.org/web/20030224125640/http://www.rosenlaw.com:80/afl.html")
      , (Nothing, "Academic Free License (AFL) (v. 1.2)", "https://web.archive.org/web/20030515043719/http://www.rosenlaw.com:80/afl1.2.html")
      , (Nothing, "Academic Free License (AFL) (v. 2.0)", "https://web.archive.org/web/20041212013430/http://rosenlaw.com:80/afl2.0.html")
      , (Nothing, "Academic Free License (AFL) (v. 2.1)", "https://web.archive.org/web/20080413164801/http://rosenlaw.com:80/afl21.htm")
      , (Nothing, "Academic Free License (AFL) (v. 3.0)", "https://web.archive.org/web/20080317004542/http://www.rosenlaw.com/AFL3.0.htm")
      , (Nothing, "Apache License (v. 1.0)", "http://www.apache.org/licenses/LICENSE-1.0")
      , (Nothing, "Apache License (v. 1.1)", "http://www.apache.org/licenses/LICENSE-1.1")
      , (Nothing, "Apache License (v. 2.0)", "http://www.apache.org/licenses/LICENSE-2.0.html")
      , (Nothing, "Beerware License", "http://people.freebsd.org/~phk/")
      , (Nothing, "Boost Software License (Einordnung unklar)", "http://www.boost.org/LICENSE_1_0.txt")
      , (Nothing, "BSD 2-clause \"Simplified\" or \"FreeBSD\" License", "http://www.freebsd.org/copyright/freebsd-license.html")
      , (Nothing, "BSD 3-clause \"New\" or \"Revised\" License", "https://spdx.org/licenses/BSD-3-Clause")
      , (Nothing, "BSD 4-clause \"Original\" or \"Old\" License", "https://www.freebsd.org/copyright/license.html")
      , (Nothing, "CeCILL-B Free Software License Agreement", "http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html")
      , (Nothing, "Christian Software Public License", "http://pudge.net/jesux/cspl.html")
      , (Nothing, "CNRI Open Source License Agreement", "http://www.handle.net/python_licenses/python1.6_9-5-00.html")
      , (Nothing, "Condor Public License (v. 1.1)", "http://www.cs.wisc.edu/condor/license.html#condor")
      , (Nothing, "Contrat de License de Logiciel Libre CeCILL-B", "http://www.cecill.info/licences/Licence_CeCILL-B_V1-fr.html")
      , (Nothing, "Cougaar Open Source License", "https://web.archive.org/web/20100818181228/http://cougaar.org/twiki/bin/view/Main/LicenseText")
      , (Nothing, "Cryptix General License", "http://www.cryptix.org/LICENSE.TXT")
      , (Nothing, "Curl License", "https://github.com/curl/curl/blob/master/COPYING")
      , (Nothing, "Do What The Fuck You Want To Public License (v. 1.0)", "https://commons.wikimedia.org/wiki/Template:WTFPL-1")
      , (Nothing, "Do What The Fuck You Want To Public License (v. 2.0)", "http://www.wtfpl.net/txt/copying/ ")
      , (Nothing, "Eclipse Distribution License (v 1.0)", "https://www.eclipse.org/org/documents/edl-v10.php")
      , (Nothing, "Educational Community License (v. 1.0)", "https://web.archive.org/web/20050326095112/http://www.sakaiproject.org:80/license.html")
      , (Nothing, "Educational Community License (v. 2.0)", "https://web.archive.org/web/20100617144451/http://www.osedu.org/licenses/ECL-2.0")
      , (Nothing, "Eiffel Forum License (v. 1.0)", "http://www.eiffel-nice.org/license/forum.txt")
      , (Nothing, "Eiffel Forum License (v. 2.0)", "http://www.eiffel-nice.org/license/eiffel-forum-license-2.html")
      , (Nothing, "Entessa Public License (v. 1.0)", "http://web.archive.org/web/20050419215723/www.openseal.org/epl/")
      , (Nothing, "EU DataGrid Software License (v. 2.0)", "https://web.archive.org/web/20021229214435/http://eu-datagrid.web.cern.ch:80/eu-datagrid/license.html")
      , (Nothing, "Fair License", "https://web.archive.org/web/20040803105645/http://rhid.com/fair")
      , (Nothing, "Free Fuzzy Logic Library Open Source License", "http://ffll.sourceforge.net/license.txt")
      , (Nothing, "FreeType Project License", "http://git.savannah.gnu.org/cgit/freetype/freetype2.git/tree/docs/FTL.TXT")
      , (Nothing, "FSF Unlimited License", "https://fedoraproject.org/wiki/Licensing/FSF_Unlimited_License")
      , (Nothing, "Galen Open Source License (GOSL)", "http://www.opengalen.org/gosl.html")
      , (Nothing, "Globus Toolkit Public License", "https://web.archive.org/web/20070626151228/http://tyne.dl.ac.uk/StarterKit/gt2/toolkit/download/license.html")
      , (Nothing, "Globus Toolkit Public License (GTPL) (v. 2.0)", "http://www.globus.org/toolkit/license.html")
      , (Nothing, "ICU License", "https://web.archive.org/web/20080524220901/http://source.icu-project.org:80/repos/icu/icu/trunk/license.html")
      , (Nothing, "ImageMagick Terms and Conditions for Use, Reproduction, and Distribution", "http://www.imagemagick.org/script/license.php")
      , (Nothing, "Independent JPEG Group License", "https://fedoraproject.org/wiki/Licensing:IJG?rd=Licensing/IJG")
      , (Nothing, "ISC License", "http://mirbsd.org/ISC-Licence")
      , (Nothing, "Historical Permission Notice and Disclaimer (HPND)", "https://web.archive.org/web/20030923051149/http://www.geocities.com/brucedodson.rm/hist_pnd.htm")
      , (Nothing, "Horde Apache-like License", "http://www.horde.org/licenses/asl.php")
      , (Nothing, "Horde BSD-like License", "http://www.horde.org/licenses/bsdl.php")
      , (Nothing, "Indiana University Extreme! Lab Software License, Version 1.2", "http://www.extreme.indiana.edu/license.txt")
      , (Nothing, "Intel Open Source License for CDSA/CSSM Implementation", "http://www.opensource.org/licenses/intel-open-source-license.php")
      , (Nothing, "ISC License", "https://www.isc.org/downloads/software-support-policy/isc-license/")
      , (Nothing, "JasPer License Version 2.0", "http://www.ece.uvic.ca/~frodo/jasper/LICENSE")
      , (Nothing, "JSON License", "http://www.json.org/license.html")
      , (Nothing, "Libpng License", "http://www.libpng.org/pub/png/src/libpng-LICENSE.txt")
      , (Nothing, "Lua Copyright notice", "http://www.lua.org/copyright.html")
      , (Nothing, "Lucent Public License Version (v. 1)", "https://web.archive.org/web/20030520193826/http://plan9.bell-labs.com/hidden/lpl4-2-03.html")
      , (Nothing, "Lucent Public License Version (v. 1.02)", "https://web.archive.org/web/20080514131645/http://plan9.bell-labs.com/plan9/license.html")
      , (Nothing, "Microsoft Permissive License (Ms-PL)", "https://web.archive.org/web/20070512223652/http://www.microsoft.com:80/resources/sharedsource/licensingbasics/permissivelicense.mspx (Einordnung unklar)")
      , (Nothing, "Microsoft Public License (Ms-PL)", "https://web.archive.org/web/20080104234143/http://www.microsoft.com:80/resources/sharedsource/licensingbasics/publiclicense.mspx (Einordnung unklar)")
      , (Nothing, "MirOS License", "http://mirbsd.org/MirOS-Licence")
      , (Nothing, "MIT License", "https://spdx.org/licenses/MIT.html#licenseText")
      , (Nothing, "Mozart License", "http://mozart.github.io/license-info/license.html")
      , (Nothing, "Naumen Public License", "http://www.worldlii.org/int/other/PubRL/2009/42.html")
      , (Nothing, "NTP License", "https://www.eecis.udel.edu/~mills/ntp/html/copyright.html")
      , (Nothing, "NUnit License", "http://nunit.org/docs/2.4/license.html")
      , (Nothing, "Open Group Test Suite License", "http://www.opengroup.org/testing/downloads/The_Open_Group_TSL.txt")
      , (Nothing, "Open Media Group Open Source License", "https://web.archive.org/web/20090213173457/http://www.openmediagroup.com/license.html")
      , (Nothing, "OpenLDAP Public License (v. 1.1)", "http://www.openldap.org/devel/gitweb.cgi?p=openldap.git;a=blob;f=LICENSE;hb=806557a5ad59804ef3a44d5abfbe91d706b0791f")
      , (Nothing, "OpenLDAP Public License (v. 1.2)", "http://www.openldap.org/devel/gitweb.cgi?p=openldap.git;a=blob;f=LICENSE;hb=42b0383c50c299977b5893ee695cf4e486fb0dc7")
      , (Nothing, "OpenLDAP Public License (v. 1.3)", "http://www.openldap.org/devel/gitweb.cgi?p=openldap.git;a=blob;f=LICENSE;hb=e5f8117f0ce088d0bd7a8e18ddf37eaa40eb09b1")
      , (Nothing, "OpenLDAP Public License (v. 1.4)", "http://www.openldap.org/devel/gitweb.cgi?p=openldap.git;a=blob;f=LICENSE;hb=c9f95c2f3f2ffb5e0ae55fe7388af75547660941")
      , (Nothing, "OpenLDAP Public License (v. 2.0)", "http://www.openldap.org/devel/gitweb.cgi?p=openldap.git;a=blob;f=LICENSE;hb=cbf50f4e1185a21abd4c0a54d3f4341fe28f36ea")
      , (Nothing, "OpenLDAP Public License (v. 2.0.1)", "http://www.openldap.org/devel/gitweb.cgi?p=openldap.git;a=blob;f=LICENSE;hb=b6d68acd14e51ca3aab4428bf26522aa74873f0e")
      , (Nothing, "OpenLDAP Public License (v. 2.1)", "http://www.openldap.org/devel/gitweb.cgi?p=openldap.git;a=blob;f=LICENSE;hb=b0d176738e96a0d3b9f85cb51e140a86f21be715")
      , (Nothing, "OpenLDAP Public License (v. 2.2)", "http://www.openldap.org/devel/gitweb.cgi?p=openldap.git;a=blob;f=LICENSE;hb=470b0c18ec67621c85881b2733057fecf4a1acc3")
      , (Nothing, "OpenLDAP Public License (v. 2.3)", "http://www.mibsoftware.com/librock/librock/license/oldap2_3.txt")
      , (Nothing, "OpenLDAP Public License (v. 2.4)", "http://www.openldap.org/devel/gitweb.cgi?p=openldap.git;a=blob;f=LICENSE;hb=cd1284c4a91a8a380d904eee68d1583f989ed386")
      , (Nothing, "OpenLDAP Public License (v. 2.5)", "http://www.openldap.org/devel/gitweb.cgi?p=openldap.git;a=blob;f=LICENSE;hb=6852b9d90022e8593c98205413380536b1b5a7cf")
      , (Nothing, "OpenLDAP Public License (v. 2.6)", "http://www.openldap.org/devel/gitweb.cgi?p=openldap.git;a=blob;f=LICENSE;hb=1cae062821881f41b73012ba816434897abf4205")
      , (Nothing, "OpenLDAP Public License (v. 2.7)", "http://www.openldap.org/doc/admin21/license.html")
      , (Nothing, "OpenLDAP Public License (v. 2.8)", "http://www.openldap.org/software/release/license.html")
      , (Nothing, "OpenSSL License (Einordnung unklar)", "http://www.openssl.org/source/license.html")
      , (Nothing, "Pangeia Informatica Copyright (v. 1.2)", "http://www.chkrootkit.org/COPYRIGHT")
      , (Nothing, "Phorum License (v. 2.0)", "http://phorum.org/license.txt")
      , (Nothing, "PHP License (v. 3.0)", "http://www.php.net/license/3_0.txt")
      , (Nothing, "PHP License (v. 3.1)", "http://www.php.net/license/3_01.txt")
      , (Nothing, "PostgreSQL License", "https://www.postgresql.org/about/licence/")
      , (Nothing, "Privaria Attribution Assurance License", "https://web.archive.org/web/20050305170641/http://eepatents.com/privaria/#license")
      , (Nothing, "Python 2.0.1 License", "https://www.python.org/download/releases/2.0.1/license/")
      , (Nothing, "Python 2.4.2 license", "http://www.python.org/download/releases/2.4.2/license/")
      , (Nothing, "Python Software Foundation License (v. 2)", "https://www.python.org/download/releases/2.7.7/license/")
      , (Nothing, "Ruby License", "http://www.ruby-lang.org/en/LICENSE.txt")
      , (Nothing, "Sendmail License", "http://www.sendmail.org/ftp/LICENSE")
      , (Nothing, "skyBuilders Open Source License", "http://www.skybuilders.com/OpenSourceLicense.html")
      , (Nothing, "SpeechWorks Public License - Software (v. 1.1)", "http://www.speech.cs.cmu.edu/openvxi/OpenVXI_1_4/License.txt")
      , (Nothing, "Standard ML of New Jersey Copyright Notice", "http://cm.bell-labs.com/cm/cs/what/smlnj/license.html")
      , (Nothing, "Suneido Free Software License", "http://suneido.com/wp-content/uploads/delightful-downloads/2014/10/free_license.txt")
      , (Nothing, "Tcl/Tk License Terms", "http://www.tcl.tk/software/tcltk/license.html")
      , (Nothing, "Tea Software License", "http://teatrove.sourceforge.net/license.html")
      , (Nothing, "The SpeechWorks Public License (v. 1.1 )", "http://www.speech.cs.cmu.edu/openvxi/OpenVXI_1_4/License.txt")
      , (Nothing, "Trusster Open Source License (v. 1.0a)", "https://github.com/trusster/trusster/blob/master/truss/cpp/src/truss_verification_top.cpp")
      , (Nothing, "Udanax Open-Source License", "http://udanax.xanadu.com/license.html")
      , (Nothing, "Universal Permissive License (v. 1.0)", "http://www.oracle.com/technetwork/licenses/upl-license-2927578.html")
      , (Nothing, "University of Illinois/NCSA Open Source License (NSCA)", "https://web.archive.org/web/20100814031321/http://otm.illinois.edu/uiuc_openSource")
      , (Nothing, "Unlicense", "http://unlicense.org/")
      , (Nothing, "Vovida Software License v 1.0", "https://web.archive.org/web/20050410031206/http://www.vovida.org/document/VOCAL-1.4.0/license.txt")
      , (Nothing, "W3C Software and Document Notice and License", "http://www.w3.org/Consortium/Legal/copyright-software.html")
      , (Nothing, "Wide Open License (WOL)", "http://www.dspguru.com/wol2.htm")
      , (Nothing, "X11 License", "http://www.xfree86.org/3.3.6/COPYRIGHT2.html#3")
      , (Nothing, "X Window System License", "https://web.archive.org/web/20050406051821/%20http://www.x.org/Downloads_terms.html")
      , (Nothing, "X.Net License", "http://www.xnetinc.com/xiua/copyright.htm")
      , (Nothing, "XFree86 Licence", "http://www.xfree86.org/legal/licenses.html")
      , (Nothing, "xinetd License", "https://web.archive.org/web/20080325072754/www.xinetd.org/cgi-bin/cvsweb.cgi/xinetd/COPYRIGHT?rev=1.1.1.1;content-type=text%2Fplain")
      , (Nothing, "Zlib license", "http://www.gzip.org/zlib/zlib_license.html")
      , (Nothing, "Zope Public License (v. 1.1)", "http://old.zope.org/Resources/License/ZPL-1.1")
      , (Nothing, "Zope Public License (v. 2.0)", "http://old.zope.org/Resources/License/ZPL-2.0")
      , (Nothing, "Zope Public License (v. 2.1)", "https://web.archive.org/web/20060426220850/http://www.zope.org:80/Resources/ZPL/")
      ]
    strongCopyleftGPLLics =
      [ (Nothing, "Affero General Public License (v. 1)", "http://www.affero.org/oagpl.html")
      , (Nothing, "Affero General Public License (v. 2)", "http://www.affero.org/agpl2.html")
      , (Nothing, "Alternate Route Open Source License (v. 1.1)", "http://www.wsdot.wa.gov/eesc/bridge/alternateroute/arosl.htm")
      , (Nothing, "CrossPoint Quelltextlizenz", "http://www.crosspoint.de/srclicense.html")
      , (Nothing, "eCos License (v. 2.0)", "http://www.gnu.org/licenses/ecos-license.html")
      , (Nothing, "FreeCard License", "http://freecard.sourceforge.net/website/licence/license.php")
      , (Nothing, "GNU Affero General Public License (AGPL-3.0) (v. 3.0)", "http://www.fsf.org/licensing/licenses/agpl-3.0.html")
      , (Nothing, "GNU Classpath - GPL with special exception", "http://www.gnu.org/software/classpath/license.html")
      , (Nothing, "GNU Emacs General Public License", "http://www.free-soft.org/gpl_history/emacs_gpl.html")
      , (Nothing, "GNU General Public License (GPL) (v. 1.0)", "http://www.gnu.org/copyleft/copying-1.0.html")
      , (Nothing, "GNU General Public License (GPL) (v. 2.0)", "http://www.gnu.org/licenses/old-licenses/gpl-2.0.html")
      , (Nothing, "GNU General Public License (GPL) (v. 3.0)", "http://www.fsf.org/licensing/licenses/gpl.html")
      , (Nothing, "GNU General Public License (GPL) (v. 3.0)", "http://www.gnu.de/gpl-ger.html (Inoffizielle deutsche Übersetzung)")
      , (Nothing, "GNU General Public License v2.0 w/Bison exception", "https://github.com/ifrOSS/Lizenzcenter/blob/Neue-Gliederung/Bison-exception-2.2")
      , (Nothing, "GNU General Public License v2.0 w/Classpath exception", "http://www.gnu.org/software/classpath/license.html")
      , (Nothing, "GNU General Public License v2.0 w/Font exception", "http://www.gnu.org/licenses/gpl-faq.html#FontException")
      , (Nothing, "GNU General Public License v2.0 w/GCC Runtime Library exception", "https://gcc.gnu.org/git/?p=gcc.git;a=blob;f=gcc/libgcc1.c;h=762f5143fc6eed57b6797c82710f3538aa52b40b;hb=cb143a3ce4fb417c68f5fa2691a1b1b1053dfba9")
      , (Nothing, "GNU General Public License v3.0 w/Autoconf exception", "http://www.gnu.org/licenses/autoconf-exception-3.0.html")
      , (Nothing, "GNU General Public License v3.0 w/GCC Runtime Library exception (RLE 3.0)", "http://www.gnu.org/licenses/gcc-exception-3.0.html")
      , (Nothing, "GNU General Public License v3.0 w/GCC Runtime Library exception (RLE 3.1)", "http://www.gnu.org/licenses/gcc-exception-3.1.html")
      , (Nothing, "Honest Public License (HPL) (v 1.0)", "https://web.archive.org/web/20080215154706/http://www.projectpier.org/manual/tour/licence")
      , (Nothing, "Honest Public License (HPL) (v 1.1)", "https://web.archive.org/web/20150815003528/http://gnugeneration.com/licenses/HPLv1.1.txt")
      , (Nothing, "Nethack General Public License", "http://www.nethack.org/common/license.html")
      , (Nothing, "Open RTLinux Patent License", "https://web.archive.org/web/20120222184907/http://rtlinuxfree.com/openpatentlicense.html")
      , (Nothing, "RedHat eCos Public License (v. 2.0)", "http://sources.redhat.com/ecos/license-overview.html")
      , (Nothing, "Simple Public License (v. 2.0)", "https://web.archive.org/web/20080906145432/http://www.law.washington.edu/Casrip/License/SimplePublicLicense.html")
      ]
    strongCopyleftLics =
      [ (Nothing, "Arphic Public License", "http://ftp.gnu.org/non-gnu/chinese-fonts-truetype/LICENSE")
      , (Nothing, "CeCILL Free Software License Agreement (v. 1.0)", "http://www.cecill.info/licences/Licence_CeCILL_V1-US.html")
      , (Nothing, "CeCILL Free Software License Agreement (v. 1.1)", "http://www.cecill.info/licences/Licence_CeCILL_V1.1-US.html")
      , (Nothing, "CeCILL Free Software License Agreement (v. 2.0)", "http://www.cecill.info/licences/Licence_CeCILL_V2-en.html")
      , (Nothing, "CeCILL Free Software License Agreement (v. 2.1)", "http://www.cecill.info/licences/Licence_CeCILL_V2.1-en.html")
      , (Nothing, "Contrat de License de Logiciel Libre CeCILL (v. 1.0)", "http://www.cecill.info/licences/Licence_CeCILL_V1-fr.html")
      , (Nothing, "Contrat de License de Logiciel Libre CeCILL  (v. 2.0)", "http://www.cecill.info/licences/Licence_CeCILL_V2-fr.html")
      , (Nothing, "Contrat de License de Logiciel Libre CeCILL  (v. 2.1)", "http://www.cecill.info/licences/Licence_CeCILL_V2.1-fr.html")
      , (Nothing, "Common Public License (v. 0.5)", "http://www.eclipse.org/legal/cpl-v05.html")
      , (Nothing, "Common Public License (v. 1.0)", "http://www.eclipse.org/legal/cpl-v10.html")
      , (Nothing, "Deutsche Freie Softwarelizenz (d-fsl)", "http://www.d-fsl.org/")
      , (Nothing, "Eclipse Public License (v. 1.0)", "http://www.eclipse.org/legal/epl-v10.html")
      , (Nothing, "European Union Public License (v. 1.0)", "http://ec.europa.eu/idabc/en/document/7330.html")
      , (Nothing, "European Union Public Licence (v. 1.1)", "https://joinup.ec.europa.eu/page/eupl-text-11-12")
      , (Nothing, "European Union Public Licence (v. 1.2)", "https://joinup.ec.europa.eu/page/eupl-text-11-12")
      , (Nothing, "German Free Software License", "https://www.hbz-nrw.de/produkte/open-access/lizenzen/dfsl/german-free-software-license")
      , (Nothing, "IBM Public License", "http://oss.software.ibm.com:80/developerworks/opensource/license10.html")
      , (Nothing, "Intel Open Source License", "https://opensource.org/licenses/intel-open-source-license.php")
      , (Nothing, "IPA Font License", "https://ipafont.ipa.go.jp/old/ipafont/download.html#en")
      , (Nothing, "No Limit Public License", "http://spdx.org/licenses/NLPL")
      , (Nothing, "Non-Profit Open Software License 3.0", "https://spdx.org/licenses/NPOSL-3.0.html")
      , (Nothing, "Open Group Public License", "http://www.opengroup.org/openmotif/license")
      , (Nothing, "Open Software License 1.0", "http://web.archive.org/web/20021201193408/http://rosenlaw.com:80/osl.html")
      , (Nothing, "Open Software License 2.0", "http://web.archive.org/web/20041020171434/http://www.rosenlaw.com/osl2.0.html")
      , (Nothing, "Open Software License 2.1", "http://web.archive.org/web/20050212003940/http://www.rosenlaw.com/osl21.htm")
      , (Nothing, "Open Software License 3.0", "https://web.archive.org/web/20110721200508/http://www.rosenlaw.com:80/OSL3.0.htm")
      , (Nothing, "Reciprocal Public License (v. 1.0)", "https://web.archive.org/web/20030424114621fw_/http://www.technicalpursuit.com:80/Biz_RPL.html")
      , (Nothing, "Reciprocal Public License (v. 1.1)", "https://opensource.org/licenses/RPL-1.1")
      , (Nothing, "Reciprocal Public License (v. 1.3)", "https://web.archive.org/web/20080828191234/http://www.technicalpursuit.com/licenses/RPL_1.3.html")
      , (Nothing, "Reciprocal Public License (v. 1.5)", "http://lists.opensource.org/pipermail/license-discuss_lists.opensource.org/attachments/20070724/6944e582/attachment.txt")
      , (Nothing, "SIL Open Font License (v. 1.0)", "http://scripts.sil.org/cms/scripts/page.php?item_id=OFL10_web")
      , (Nothing, "SIL Open Font License (v. 1.1)", "http://scripts.sil.org/cms/scripts/page.php?item_id=OFL_web")
      , (Nothing, "Salutation Public License", "http://web.archive.org/web/20050323201906/http://www.salutation.org/lite/lite_license.htm")
      , (Nothing, "Software AG License Terms (Quip License) (v. 1.3)", "http://www.cse.uconn.edu/~dqg/cse350/xml/quip/License.txt")
      , (Nothing, "VOSTROM Public License for Open Source", "http://pwhois.org/license.who")
      ]
    weakCopyleftMPLLics =
      [ (Nothing, "Common Development and Distribution License (CDDL) (v. 1.0)", "http://oss.oracle.com/licenses/CDDL")
      , (Nothing, "Common Development and Distribution License, Version 1.1 (CDDL v 1.1)", "https://javaee.github.io/glassfish/LICENSE")
      , (Nothing, "Common Public Attribution License (v. 1.0)", "https://www.agnitas.de/e-marketing-manager/email-marketing-software/openemm/license/")
      , (Nothing, "Computer Associates Trusted Open Source License (v. 1.1)", "https://web.archive.org/web/20160308205306/http://www.luebeckonline.com/mustervertraege/software-vertraege/open-source-lizenz/computer-associates-trusted-open-source-license-version-11.html")
      , (Nothing, "CUA Office Public License (v. 1.0)", "https://web.archive.org/web/20040212235130/http://cuaoffice.sourceforge.net/CPL.htm")
      , (Nothing, "Erlang Public License (v. 1.1)", "http://www.erlang.org/EPLICENSE")
      , (Nothing, "gSOAP Public License (v. 1.0)", "https://web.archive.org/web/20020822050424/http://www.cs.fsu.edu:80/~engelen/license.html")
      , (Nothing, "gSOAP Public License (v.  1.1)", "https://web.archive.org/web/20021104130030/http://www.cs.fsu.edu:80/~engelen/license.html")
      , (Nothing, "gSOAP Public License (v.  1.2)", "https://web.archive.org/web/20030420224716/http://www.cs.fsu.edu:80/~engelen/license.html")
      , (Nothing, "gSOAP Public License (v.  1.3)", "https://web.archive.org/web/20030608134559/http://www.cs.fsu.edu:80/~engelen/license.html")
      , (Nothing, "gSOAP Public License (v. 1.3a)", "https://web.archive.org/web/20050923110600/http://www.cs.fsu.edu:80/~engelen/license.html")
      , (Nothing, "gSOAP Public License (v. 1.3b)", "http://www.cs.fsu.edu/~engelen/license.html")
      , (Nothing, "ICS Open Source Public License", "http://web.archive.org/web/20030625151406/http://www.opencontrol.org/OSPL.htm")
      , (Nothing, "Interbase Public License", "https://web.archive.org/web/20051201062423/http://bdn.borland.com:80/article/0,1410,30198,00.html")
      , (Nothing, "Mozilla Public License (v. 1.0)", "http://www.mozilla.org/MPL/MPL-1.0.html")
      , (Nothing, "Mozilla Public License (v. 1.1)", "http://www.mozilla.org/MPL/MPL-1.1.html")
      , (Nothing, "Mozilla Public License (v. 2.0)", "http://www.mozilla.org/MPL/2.0/")
      , (Nothing, "NASA Open Source Agreement (v. 1.1)", "https://web.archive.org/web/20040426023805/https://www.nas.nasa.gov/Research/Software/Open-Source/NASA_Open_Source_Agreement_1.1.txt")
      , (Nothing, "NASA Open Source Agreement (v. 1.3)", "https://ti.arc.nasa.gov/opensource/nosa/")
      , (Nothing, "Netizen Open Source License (NOSL)", "http://web.archive.org/web/20000815212105/bits.netizen.com.au/licenses/NOSL/")
      , (Nothing, "Nokia Open Source License", "http://www.opensource.org/licenses/nokia.php")
      , (Nothing, "Open Public License (v. 1.0)", "https://web.archive.org/web/20140411111551/http://old.koalateam.com/jackaroo/OPL_1_0.TXT")
      , (Nothing, "Open Telecom Public License", "http://www.ifross.de/Fremdartikel/otpl.htm")
      , (Nothing, "Openbravo Public License", "http://www.openbravo.com/legal/license.html")
      , (Nothing, "OpenC++ License Terms", "http://opencxx.sourceforge.net/license/")
      , (Nothing, "RedHat eCos Public License (v. 1.1)", "http://ecos.sourceware.org/old-license.html")
      , (Nothing, "Ricoh Source Code Public License", "http://web.archive.org/web/20060427194554/http://www.risource.org/RPL/RPL-1.0A.shtml")
      , (Nothing, "SNIA Public License Version (v.1.1)", "https://web.archive.org/web/20050214120435/https://www.snia.org/smi/developers/open_source")
      , (Nothing, "SugarCRM Public License (v. 1.1.3)", "https://web.archive.org/web/20160622020613/http://www.sugarcrm.com/page/sugarcrm-public-license/en")
      , (Nothing, "Sun Industry Standards Source License (v. 1.0)", "https://web.archive.org/web/20000816085057/http://openoffice.org:80/project/www/sissl_license.html")
      , (Nothing, "Sun Industry Standards Source License (v. 1.1)", "http://www.openoffice.org/licenses/sissl_license.html")
      , (Nothing, "Sun Industry Standards Source License (v. 1.2)", "http://gridscheduler.sourceforge.net/Gridengine_SISSL_license.html")
      , (Nothing, "Sun Public License", "http://java.sun.com/spl.html")
      , (Nothing, "Sun Public License v1.0", "http://www.opensource.org/licenses/sunpublic.php")
      , (Nothing, "Sybase Open Watcom Public License 1.0", "ftp://ftp.openwatcom.org/install/license.txt")
      , (Nothing, "Zend Engine License (v. 2.0)", "https://web.archive.org/web/20130517195954/http://www.zend.com/license/2_00.txt")
      , (Nothing, "Zenplex Public License", "http://web.archive.org/web/20041010201945/www.zenplex.org/zpl_txt.html")
      , (Nothing, "Zimbra Public License (ZPL) (v. 1.2)", "https://web.archive.org/web/20080205064641/http://www.zimbra.com/license/zimbra_public_license_1.2.html")
      , (Nothing, "Zimbra Publice License (v. 1.3)", "https://web.archive.org/web/20120617001845/http://www.zimbra.com/license/zimbra-public-license-1-3.html")
      , (Nothing, "Zimbra Publice License (v. 1.4)", "https://www.zimbra.com/legal/zimbra-public-license-1-4/")
      ]
    weakCopyleftLics =
      [ (Nothing, "Adaptive Public License (v.1.0)", "https://web.archive.org/web/20070722115014/http://www.mamook.net/mediawiki/index.php/Adaptive_Public_License")
      , (Nothing, "Apple Public Source License (v. 2.0)", "https://web.archive.org/web/20060323040828/https://opensource.apple.com/apsl/2.0.txt")
      , (Nothing, "BitTorrent Open Source License (v. 1.0)", "https://sources.gentoo.org/cgi-bin/viewvc.cgi/gentoo-x86/licenses/BitTorrent?diff_format=s&revision=1.1.1.1&view=markup")
      , (Nothing, "Bremer Lizenz für freie Softwarebibliotheken (OSCI-Lizenz) (v. 1.0)", "http://www1.osci.de/sixcms/media.php/13/Bremer_Lizenz.pdf (.pdf-Dokument)")
      , (Nothing, "CeCILL-C Free Software License Agreement", "http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html")
      , (Nothing, "Code Project Open License (CPOL) (v. 1.02)", "https://www.codeproject.com/info/cpol10.aspx")
      , (Nothing, "Contrat de License de Logiciel Libre CeCILL-C", "http://www.cecill.info/licences/Licence_CeCILL-C_V1-fr.html")
      , (Nothing, "Cougaar Open Source License Agreement", "https://web.archive.org/web/20060618122747/http://cougaar.org:80/docman/view.php/17/126/old_cosl_license.html (Einordnung unklar)")
      , (Nothing, "Eclipse Public License (v. 2.0)", "https://www.eclipse.org/org/documents/epl-2.0/EPL-2.0.html")
      , (Nothing, "GNU Library General Public License (LGPL) (v. 2.0)", "http://www.gnu.org/copyleft/library.html")
      , (Nothing, "GNU Lesser General Public License (LGPL) (v. 2.1)", "http://www.gnu.org/licenses/old-licenses/lgpl-2.1.html")
      , (Nothing, "GNU Lesser General Public License (LGPL) (v. 3.0)", "http://www.gnu.org/licenses/lgpl.html")
      , (Nothing, "GNU Lesser General Public License (LGPL) (v. 3.0)", "http://www.gnu.de/lgpl-ger.html (Inoffizielle deutsche Übersetzung)")
      , (Nothing, "Hi-Potent Open Source License", "http://web.archive.org/web/20030804175518/www.hi-potent.com/license.html")
      , (Nothing, "Jabber Open Source License", "http://archive.jabber.org/core/JOSL.pdf")
      , (Nothing, "Microsoft Reciprocal License (Ms-RL)", "https://web.archive.org/web/20080105011633/http://www.microsoft.com:80/resources/sharedsource/licensingbasics/reciprocallicense.mspx")
      , (Nothing, "Motosoto Open Source License (v. 0.9.1)", "http://opensource.org/licenses/motosoto.php")
      , (Nothing, "Open CASCADE Technology Public License (v. 6.6)", "https://www.opencascade.com/content/occt-public-license")
      , (Nothing, "wxWindows License (v. 1.0)", "https://web.archive.org/web/20001121033400/http://www.wxwindows.org:80/licence.htm")
      , (Nothing, "wxWindows Library License (v. 3.0)", "https://web.archive.org/web/20001121041000/http://www.wxwindows.org:80/licence3.txt")
      , (Nothing, "wxWindows Library License (v. 3.1)", "https://www.wxwidgets.org/about/licence/")
      , (Nothing, "Yahoo! Public License (YPL) (v. 1.1)", "https://web.archive.org/web/20120617001853/http://www.zimbra.com/license/yahoo_public_license_1.0.html")
      ]
    withChoiceLics =
      [ (Nothing, "ANTLR 2 License", "http://www.antlr2.org/license.html")
      , (Nothing, "Artistic License (v. 1.0)", "http://www.perlfoundation.org/artistic_license_1_0 (Einordnung unklar)")
      , (Nothing, "Artistic License (v. 2.0)", "http://www.perlfoundation.org/artistic_license_2_0")
      , (Nothing, "Clarified Artistic License", "http://www.statistica.unimib.it/utenti/dellavedova/software/artistic2.html")
      , (Nothing, "Frameworx Open License (v. 1.0)", "https://spdx.org/licenses/Frameworx-1.0.html")
      , (Nothing, "Keith Devens' Open Source License", "https://web.archive.org/web/20100604220226/http://www.keithdevens.com/software/license/")
      , (Nothing, "LaTeX Project Public License (LPPL) (v. 1.0)", "http://www.latex-project.org/lppl/lppl-1-0.html")
      , (Nothing, "LaTeX Project Public License (LPPL) (v. 1.1)", "http://www.latex-project.org/lppl/lppl-1-1.html")
      , (Nothing, "LaTeX Project Public License (LPPL) (v. 1.2)", "http://www.latex-project.org/lppl/lppl-1-2.html")
      , (Nothing, "LaTeX Project Public License (LPPL) (v. 1.3b)", "https://www.latex-project.org/lppl/lppl-1-3b/")
      , (Nothing, "LaTeX Project Public License (LPPL) (v. 1.3b)", "http://www.latex-project.org/lppl/lppl-1-3b-de.html (Inoffizielle deutsche Übersetzung)")
      , (Nothing, "LaTeX Project Public License (LPPL) (v. 1.3c)", "http://www.latex-project.org/lppl/lppl-1-3c.html")
      , (Nothing, "Physnet Package License", "http://web.archive.org/web/20060821203230/http://35.9.69.219/home/modules/license.html")
      , (Nothing, "Ruby License", "http://www.ruby-lang.org/en/about/license.txt")
      , (Nothing, "SFL License Agreement", "https://web.archive.org/web/20160416132210/http://legacy.imatix.com/html/sfl/sfl4.htm")
      , (Nothing, "SGI Free Software License B (v. 1.0)", "https://web.archive.org/web/20130114073135/http://oss.sgi.com/projects/FreeB/SGIFreeSWLicB.1.0.html (Einordnung unklar)")
      , (Nothing, "SGI Free Software License B (v. 1.1)", "https://web.archive.org/web/20170414231252/http://oss.sgi.com:80/projects/FreeB/SGIFreeSWLicB.1.1.doc (Einordnung unklar)")
      , (Nothing, "Sleepycat License", "https://fedoraproject.org/wiki/Licensing/Sleepycat")
      , (Nothing, "Sleepycat Software Product License", "http://genome.jouy.inra.fr/doc/docs/sleepycat/license.html")
      , (Nothing, "Vim License", "http://web.archive.org/web/20070207020422/https://www.vim.org/htmldoc/uganda.html#license")
      ]
    withSpecialRightsLics =
      [ (Nothing, "Apple Public Source License 1.0", "https://www.apple.com/publicsource/license.html (Einordnung unklar)")
      , (Nothing, "Apple Public Source License 1.1", "https://opensource.apple.com/source/IOSerialFamily/IOSerialFamily-7/APPLE_LICENSE (Einordnung unklar)")
      , (Nothing, "Apple Public Source License (v. 1.2)", "https://web.archive.org/web/20060209125840/http://www.opensource.apple.com/apsl/1.2.txt (Einordnung unklar)")
      , (Nothing, "Macromedia Open Source License Agreement (v. 1.0)", "https://web.archive.org/web/20020627100645/http://www.macromedia.com/v1/handlers/index.cfm?ID=23075")
      , (Nothing, "Netscape Public License (NPL) (v. 1.0)", "https://web.archive.org/web/19990422030305/http://www.mozilla.org/NPL/NPL-1.0.html")
      , (Nothing, "Netscape Public License (NPL) (v. 1.1)", "https://web.archive.org/web/20020202113823/http://www.mozilla.org:80/MPL/NPL-1.1.html")
      , (Nothing, "OCLC Research Public License (v. 1.0)", "https://web.archive.org/web/20020817035019/http://www.oclc.org/research/software/license/")
      , (Nothing, "OCLC Research Public License (v. 2.0)", "https://web.archive.org/web/20060217100845/http://www.oclc.org/research/software/license/v2final.htm")
      , (Nothing, "Open Map Software License Agreement", "https://web.archive.org/web/20160528102034/http://openmap.bbn.com:80/license.html")
      , (Nothing, "Q Public License (v. 1.0) (QPL)", "https://web.archive.org/web/20101115061537/http://doc.trolltech.com:80/4.0/qpl.html")
      , (Nothing, "RealNetworks Community Source License - Research and Development Use (RCSL R&D) (v 2.0)", "https://web.archive.org/web/20060924224843/https://www.helixcommunity.org/content/rcsl")
      , (Nothing, "RealNetworks Community Source License - Research and Development Use (RCSL R&D) (v 3.0)", "https://web.archive.org/web/20141226113418/https://helixcommunity.org/content/rcsl")
      , (Nothing, "RealNetworks Public Source License (RPSL) (v. 1.0)", "https://community.helixcommunity.org/content/rpsl")
      ]
    mkRaws kind = map (\(i, n, u) -> IfrOSSFact n i kind u)
  in mkRaws IfrNoCopyleft noCopyleftLics
  ++ mkRaws IfrStrongCopyleft_GPLlike strongCopyleftGPLLics
  ++ mkRaws IfrStrongCopyleft strongCopyleftLics
  ++ mkRaws IfrWeakCopyleft_MPLlike weakCopyleftMPLLics
  ++ mkRaws IfrWeakCopyleft weakCopyleftLics
  ++ mkRaws IfrLicenseWithChoice withChoiceLics
  ++ mkRaws IfrLicenseWithSpecialRights withSpecialRightsLics

loadIfrOSSFacts :: IO Facts
loadIfrOSSFacts = do
  logThatFactsAreLoadedFrom "ifrOSS"
  return . V.fromList $ map (LicenseFact (Just ifrOSSURL)) rawIfrOSSFacts
