;
; Copyright © 2024 Peter Monks
;
; Licensed under the Apache License, Version 2.0 (the "License");
; you may not use this file except in compliance with the License.
; You may obtain a copy of the License at
;
;     http://www.apache.org/licenses/LICENSE-2.0
;
; Unless required by applicable law or agreed to in writing, software
; distributed under the License is distributed on an "AS IS" BASIS,
; WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
; See the License for the specific language governing permissions and
; limitations under the License.
;
; SPDX-License-Identifier: Apache-2.0
;

(ns lice-comb.impl.splitting-test
  (:require [clojure.string             :as s]
            [clojure.test               :refer [deftest testing is use-fixtures]]
            [spdx.licenses              :as slic]
            [spdx.exceptions            :as sexc]
            [lice-comb.test-boilerplate :refer [fixture]]
            [lice-comb.impl.splitting   :refer [strip-leading-and-trailing-operators split-on-operators]]))

(use-fixtures :once fixture)

(deftest strip-leading-and-trailing-operators-tests
  (testing "Nil, blank, etc."
    (is (nil? (strip-leading-and-trailing-operators nil)))
    (is (nil? (strip-leading-and-trailing-operators "")))
    (is (nil? (strip-leading-and-trailing-operators "   ")))
    (is (nil? (strip-leading-and-trailing-operators " \n   \r  \t\t\t "))))
  (testing "Strings without any operators"
    (is (= "Foo"                                            (strip-leading-and-trailing-operators "Foo")))
    (is (= "hand"                                           (strip-leading-and-trailing-operators "hand")))
    (is (= "android"                                        (strip-leading-and-trailing-operators "android")))
    (is (= "ornery"                                         (strip-leading-and-trailing-operators "ornery")))
    (is (= "stator"                                         (strip-leading-and-trailing-operators "stator")))
    (is (= "withhold"                                       (strip-leading-and-trailing-operators "withhold")))
    (is (= "The quick brown fox jumped over the lazy dogs." (strip-leading-and-trailing-operators "The quick brown fox jumped over the lazy dogs."))))
  (testing "Strings without leading or trailing operators"
    (is (= "Foo and bar"                                     (strip-leading-and-trailing-operators "Foo and bar")))
    (is (= "android or stator"                               (strip-leading-and-trailing-operators "android or stator")))
    (is (= "ornery or hand"                                  (strip-leading-and-trailing-operators "ornery or hand")))
    (is (= "ornery and/or hand"                              (strip-leading-and-trailing-operators "ornery and/or hand")))
    (is (= "withhold and-or hand"                            (strip-leading-and-trailing-operators "withhold and-or hand")))
    (is (= "withhold and or with and/or and-or and\\or hand" (strip-leading-and-trailing-operators "withhold and or with and/or and-or and\\or hand"))))
  (testing "Operators only"
    (is (nil? (strip-leading-and-trailing-operators "and")))
    (is (nil? (strip-leading-and-trailing-operators "AND  ")))
    (is (nil? (strip-leading-and-trailing-operators "    aNd")))
    (is (nil? (strip-leading-and-trailing-operators "or")))
    (is (nil? (strip-leading-and-trailing-operators "  OR")))
    (is (nil? (strip-leading-and-trailing-operators "oR    ")))
    (is (nil? (strip-leading-and-trailing-operators "  with")))
    (is (nil? (strip-leading-and-trailing-operators "WITH   ")))
    (is (nil? (strip-leading-and-trailing-operators "wItH")))
    (is (nil? (strip-leading-and-trailing-operators "and/or")))
    (is (nil? (strip-leading-and-trailing-operators "   AND-OR  ")))
    (is (nil? (strip-leading-and-trailing-operators "and   \n     and")))
    (is (nil? (strip-leading-and-trailing-operators "    or or    ")))
    (is (nil? (strip-leading-and-trailing-operators "  and or with and/or with\tand or with and-or with or and  "))))
  (testing "Leading operators"
    (is (= "Foo" (strip-leading-and-trailing-operators "and Foo")))
    (is (= "Foo" (strip-leading-and-trailing-operators "AND Foo")))
    (is (= "Foo" (strip-leading-and-trailing-operators "aNd Foo")))
    (is (= "Foo" (strip-leading-and-trailing-operators "or Foo")))
    (is (= "Foo" (strip-leading-and-trailing-operators "OR     Foo")))
    (is (= "Foo" (strip-leading-and-trailing-operators "oR Foo")))
    (is (= "Foo" (strip-leading-and-trailing-operators "with Foo")))
    (is (= "Foo" (strip-leading-and-trailing-operators "WITH Foo")))
    (is (= "Foo" (strip-leading-and-trailing-operators "wItH Foo")))
    (is (= "Foo" (strip-leading-and-trailing-operators "w/ Foo")))
    (is (= "Foo" (strip-leading-and-trailing-operators "and/or Foo  ")))
    (is (= "Foo" (strip-leading-and-trailing-operators "   AND-OR \n\t Foo")))
    (is (= "Foo" (strip-leading-and-trailing-operators "and/or with and or and-or Foo"))))
  (testing "Trailing operators"
    (is (= "Foo" (strip-leading-and-trailing-operators "Foo and")))
    (is (= "Foo" (strip-leading-and-trailing-operators "Foo AND")))
    (is (= "Foo" (strip-leading-and-trailing-operators "Foo aNd")))
    (is (= "Foo" (strip-leading-and-trailing-operators "Foo or")))
    (is (= "Foo" (strip-leading-and-trailing-operators "Foo OR")))
    (is (= "Foo" (strip-leading-and-trailing-operators "Foo oR")))
    (is (= "Foo" (strip-leading-and-trailing-operators "  Foo with  ")))
    (is (= "Foo" (strip-leading-and-trailing-operators "Foo WITH")))
    (is (= "Foo" (strip-leading-and-trailing-operators "Foo w/")))
    (is (= "Foo" (strip-leading-and-trailing-operators "Foo    \t\r      wItH")))
    (is (= "Foo" (strip-leading-and-trailing-operators "Foo and/or")))
    (is (= "Foo" (strip-leading-and-trailing-operators "Foo   AND-OR    ")))
    (is (= "Foo" (strip-leading-and-trailing-operators " Foo and   or and/or\nwith and-or\t")))))

(deftest split-on-operators-tests
  (testing "Nil, blank, etc."
    (is (nil? (split-on-operators nil)))
    (is (nil? (split-on-operators "")))
    (is (nil? (split-on-operators "   ")))
    (is (nil? (split-on-operators " \n   \r  \t\t\t "))))
  (testing "Strings without any operators"
    (is (= ["Foo"]                                            (split-on-operators "Foo")))
    (is (= ["Apache"]                                         (split-on-operators "Apache")))
    (is (= ["Apache MIT BSD"]                                 (split-on-operators "Apache MIT BSD")))
    (is (= ["ApacheandMIT"]                                   (split-on-operators "ApacheandMIT")))
    (is (= ["Apacheand MIT"]                                  (split-on-operators "Apacheand MIT")))
    (is (= ["Apache andMIT"]                                  (split-on-operators "Apache andMIT")))
    (is (= ["ApacheorMIT"]                                    (split-on-operators "ApacheorMIT")))
    (is (= ["Apacheor MIT"]                                   (split-on-operators "Apacheor MIT")))
    (is (= ["Apache orMIT"]                                   (split-on-operators "Apache orMIT")))
    (is (= ["ApachewithMIT"]                                  (split-on-operators "ApachewithMIT")))
    (is (= ["Apachewith MIT"]                                 (split-on-operators "Apachewith MIT")))
    (is (= ["Apache withMIT"]                                 (split-on-operators "Apache withMIT")))
    (is (= ["Apachew/MIT"]                                    (split-on-operators "Apachew/MIT")))
    (is (= ["Apachew/ MIT"]                                   (split-on-operators "Apachew/ MIT")))
    (is (= ["The quick brown fox jumped over the lazy dogs."] (split-on-operators "The quick brown fox jumped over the lazy dogs."))))
  (testing "Strings containing words that contain an operator, but which should not be split"
    (is (= ["android"]   (split-on-operators "android")))
    (is (= ["hand"]      (split-on-operators "hand")))
    (is (= ["ornery"]    (split-on-operators "ornery")))
    (is (= ["stator"]    (split-on-operators "stator")))
    (is (= ["withhold"]  (split-on-operators "withhold")))
    (is (= ["forthwith"] (split-on-operators "forthwith"))))
  (testing "Simple and splits"
    (is (= ["Apache" :and "MIT"] (split-on-operators "Apache and MIT")))
    (is (= ["Apache" :and "MIT"] (split-on-operators "Apache AND MIT")))
    (is (= ["Apache" :and "MIT"] (split-on-operators "Apache aNd MIT")))
    (is (= ["Apache" :and "MIT"] (split-on-operators "   Apache & MIT")))
    (is (= ["Apache" :and "MIT"] (split-on-operators "Apache &MIT  ")))
    (is (= ["Apache" :and "MIT"] (split-on-operators "   Apache&MIT   "))))
  (testing "Simple or splits"
    (is (= ["Apache" :or "MIT"]              (split-on-operators "Apache or MIT")))
    (is (= ["Apache" :or "MIT"]              (split-on-operators "Apache OR MIT")))
    (is (= ["Apache" :or "MIT"]              (split-on-operators "Apache oR MIT")))
    (is (= ["MIT" :or "Lesser GPL"]          (split-on-operators "MIT or Lesser GPL")))
    (is (= ["GNU Lesser" :or "MIT"]          (split-on-operators "GNU Lesser OR MIT")))
    (is (= ["GNU Lesser" :or "Lesser GPL"]   (split-on-operators "GNU Lesser OR Lesser GPL")))     ; This one is evil...
    (is (= ["GNU Library" :or "Library GPL"] (split-on-operators "GNU Library OR Library GPL"))))  ; Ditto
  (testing "Simple with splits"
    (is (= ["GPL" :with "CE"]     (split-on-operators "GPL with CE  ")))
    (is (= ["Apache" :with "MIT"] (split-on-operators "Apache with MIT")))
    (is (= ["Apache" :with "MIT"] (split-on-operators "Apache WITH MIT")))
    (is (= ["Apache" :with "MIT"] (split-on-operators "Apache wItH MIT")))
    (is (= ["Apache" :with "MIT"] (split-on-operators "Apache w/ MIT")))
    (is (= ["Apache" :with "MIT"] (split-on-operators "Apache w/MIT"))))
  (testing "Simple and/or splits"
    (is (= ["MIT" "GPL"] (split-on-operators "MIT and/or GPL")))
    (is (= ["MIT" "GPL"] (split-on-operators "  MIT and-or GPL  ")))
    (is (= ["MIT" "GPL"] (split-on-operators "MIT\nand\\or\nGPL"))))
  (testing "Strings with multiple operators"
    (is (= ["Apache" :and "MIT"]           (split-on-operators "Apache and AND MIT")))
    (is (= ["Apache" :or "MIT"]            (split-on-operators "Apache\nOR\noR\tMIT")))
    (is (= ["Apache" :and "MIT" :or "BSD"] (split-on-operators "\nApache\nAND\nMIT\nOR\nBSD\n\n\n\t")))
    (is (= ["Apache" :or "GPL" :with "CE"] (split-on-operators "Apache or GPL with CE"))))
  (testing "Strings with multiple nonsensical operators (which get cleaned up elsewhere)"
    (is (= ["EPL-2.0" :or "GPL-2.0-or-later" :with "Classpath Exception"]   (split-on-operators "EPL-2.0 OR GPL-2.0-or-later WITH Classpath Exception")))
    (is (= ["Apache License 2.0" :with :or "MIT licence"]                   (split-on-operators "Apache License 2.0 with or MIT licence")))
    (is (= ["Apache Licence 2.0" :or :and :or :and :or :and :or :and "MIT"] (split-on-operators "or and Apache Licence 2.0 or and or and or and or and MIT and or and"))))
  (testing "Exception cases for and"
    (is (= ["COMMON DEVELOPMENT AND DISTRIBUTION LICENSE Version 1.0"]                       (split-on-operators "COMMON DEVELOPMENT AND DISTRIBUTION LICENSE Version 1.0")))
    (is (= ["COMMON DEVELOPMENT  AND   DISTRIBUTION LICENSE Version 1.0"]                    (split-on-operators "COMMON DEVELOPMENT  AND   DISTRIBUTION LICENSE Version 1.0")))
    (is (= ["Common Development & Distribution Licence Version 1.1"]                         (split-on-operators "Common Development & Distribution Licence Version 1.1")))
    (is (= ["Common Development  &  Distribution Licence Version 1.1"]                       (split-on-operators "Common Development  &  Distribution Licence Version 1.1")))
    (is (= ["Copyright & all rights reserved Lean Pixel"]                                    (split-on-operators "Copyright & all rights reserved Lean Pixel")))
    (is (= ["Copyright and all rights reserved"]                                             (split-on-operators "Copyright and all rights reserved")))
    (is (= ["BSD with attribution and HPND disclaimer"]                                      (split-on-operators "BSD with attribution and HPND disclaimer")))
    (is (= ["HPND with US Government export control warning and acknowledgment"]             (split-on-operators "HPND with US Government export control warning and acknowledgment")))
    (is (= ["HPND with US Government export control warning and modification rqmt"]          (split-on-operators "HPND with US Government export control warning and modification rqmt")))
    (is (= ["Historical Permission Notice and Disclaimer"]                                   (split-on-operators "Historical Permission Notice and Disclaimer")))
    (is (= ["IBM PowerPC Initialization and Boot Software"]                                  (split-on-operators "IBM PowerPC Initialization and Boot Software")))
    (is (= ["LZMA SDK License (versions 9.22 and beyond)"]                                   (split-on-operators "LZMA SDK License (versions 9.22 and beyond)")))
    (is (= ["Nara Institute of Science and Technology License (2003)"]                       (split-on-operators "Nara Institute of Science and Technology License (2003)")))
    (is (= ["Open LDAP Public License v2.0 (or possibly 2.0A and 2.0B)"]                     (split-on-operators "Open LDAP Public License v2.0 (or possibly 2.0A and 2.0B)")))
    (is (= ["Unicode License Agreement - Data Files and Software"]                           (split-on-operators "Unicode License Agreement - Data Files and Software")))
    (is (= ["W3C Software Notice and License"]                                               (split-on-operators "W3C Software Notice and License")))
    (is (= ["W3C Software Notice and Document License"]                                      (split-on-operators "W3C Software Notice and Document License")))
    (is (= ["bzip2 and libbzip2 License"]                                                    (split-on-operators "bzip2 and libbzip2 License")))
    (is (= ["Creative Commons Attribution Non Commercial Share Alike 2.0 England and Wales"] (split-on-operators "Creative Commons Attribution Non Commercial Share Alike 2.0 England and Wales")))
    (is (= ["Creative Commons Attribution Share Alike 2.0 England and Wales"]                (split-on-operators "Creative Commons Attribution Share Alike 2.0 England and Wales")))
    (is (= ["Creative Commons Public Domain Dedication and Certification"]                   (split-on-operators "Creative Commons Public Domain Dedication and Certification")))
    (is (= ["Academy of Motion Picture Arts and Sciences BSD"]                               (split-on-operators "Academy of Motion Picture Arts and Sciences BSD")))
    (is (= ["FSF Unlimited License (With License Retention and Warranty Disclaimer)"]        (split-on-operators "FSF Unlimited License (With License Retention and Warranty Disclaimer)"))))
  (testing "Exception cases for or"
    (is (= ["GNU General Public License v3.0 or later"]                           (split-on-operators "GNU General Public License v3.0 or later")))
    (is (= ["GNU General Public License, Version 3 (or later)"]                   (split-on-operators "GNU General Public License, Version 3 (or later)")))
    (is (= ["GNU Lesser or Library General Public License, version 2.1"]          (split-on-operators "GNU Lesser or Library General Public License, version 2.1")))
    (is (= ["GNU Lesser General Public License, version 2.1 or newer"]            (split-on-operators "GNU Lesser General Public License, version 2.1 or newer")))
    (is (= ["GNU Lesser or Library General Public License, version 2.1 or newer"] (split-on-operators "GNU Lesser or Library General Public License, version 2.1 or newer")))
    (is (= ["GNU Library or Lesser General Public License, version 2.1 or newer"] (split-on-operators "GNU Library or Lesser General Public License, version 2.1 or newer")))
    (is (= ["GNU General Public License, v2.0 or greater"]                        (split-on-operators "GNU General Public License, v2.0 or greater")))
    (is (= ["GNU General Public License, version 3.0 or any later version"]       (split-on-operators "GNU General Public License, version 3.0 or any later version")))
    (is (= ["LGPL-3.0-or-later"]                                                  (split-on-operators "LGPL-3.0-or-later"))))
  (testing "Exception cases for with"
    ;####TODO!!!!
    )
  (testing "Cursed values"
    (is (= ["CDDL" "GPLv2+CE"] (split-on-operators "CDDL/GPLv2+CE"))))
  (testing "No splitting of any names in the SPDX license and exception lists"
    (let [lic-names (map #(:name (slic/id->info %)) (slic/ids))
          exc-names (map #(:name (sexc/id->info %)) (sexc/ids))]
      (is (every? true? (map #(= % (s/join (split-on-operators %))) lic-names)))
      (is (every? true? (map #(= % (s/join (split-on-operators %))) exc-names))))))
