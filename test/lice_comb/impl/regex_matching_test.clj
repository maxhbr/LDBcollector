;
; Copyright © 2023 Peter Monks
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

(ns lice-comb.impl.regex-matching-test
  (:require [clojure.test                  :refer [deftest testing is use-fixtures]]
            [clojure.set                   :as set]
            [rencg.api                     :as rencg]
            [lice-comb.impl.utils          :as lcu]
            [lice-comb.test-boilerplate    :refer [fixture testing-with-data]]
            [lice-comb.impl.regex-matching :refer [init! version-re only-or-later-re agpl-re lgpl-re gpl-re gnu-re matches]]))

(use-fixtures :once fixture)

(deftest init!-tests
  (testing "Nil response"
    (is (nil? (init!)))))

(def agpl-licenses-and-ids {
  "AGPL"                                                       '("AGPL-3.0-only")
  "AGPL v3"                                                    '("AGPL-3.0-only")
  "AGPLv3"                                                     '("AGPL-3.0-only")
  "Affero GNU Public License v3"                               '("AGPL-3.0-only")
  "Affero General Public License"                              '("AGPL-3.0-only")
  "Affero General Public License v3 or later (at your option)" '("AGPL-3.0-or-later")
  "Affero General Public License version 3 or lator"           '("AGPL-3.0-or-later")
  "Affero General Public License,"                             '("AGPL-3.0-only")
  "GNU AFFERO GENERAL PUBLIC LICENSE Version 3"                '("AGPL-3.0-only")
  "GNU AFFERO GENERAL PUBLIC LICENSE, Version 3"               '("AGPL-3.0-only")
  "GNU AGPL-V3 or later"                                       '("AGPL-3.0-or-later")
  "GNU AGPLv3"                                                 '("AGPL-3.0-only")
  "GNU Affero General Public Licence"                          '("AGPL-3.0-only")
  "GNU Affero General Public License (AGPL)"                   '("AGPL-3.0-only")
  "GNU Affero General Public License (AGPL) version 3.0"       '("AGPL-3.0-only")
  "GNU Affero General Public License 3.0 (AGPL-3.0)"           '("AGPL-3.0-only")
  "GNU Affero General Public License Version 3"                '("AGPL-3.0-only")
  "GNU Affero General Public License v3"                       '("AGPL-3.0-only")
  "GNU Affero General Public License v3.0"                     '("AGPL-3.0-only")
  "GNU Affero General Public License v3.0 only"                '("AGPL-3.0-only")
  "GNU Affero General Public License, version 3"               '("AGPL-3.0-only")
  })

(def lgpl-licenses-and-ids {
  "GNU General Lesser Public License (LGPL) version 3.0"                                 '("LGPL-3.0-only")
  "GNU LESSER GENERAL PUBLIC LICENSE"                                                    '("LGPL-3.0-only")
  "GNU LESSER GENERAL PUBLIC LICENSE - Version 2.1"                                      '("LGPL-2.1-only")
  "GNU LESSER GENERAL PUBLIC LICENSE Version 2.1, February 1999"                         '("LGPL-2.1-only")
  "GNU LESSER GENERAL PUBLIC LICENSE, Version 3.0"                                       '("LGPL-3.0-only")
  "GNU LGPL 3"                                                                           '("LGPL-3.0-only")
  "GNU LGPL v2.1"                                                                        '("LGPL-2.1-only")
  "GNU LGPL v3"                                                                          '("LGPL-3.0-only")
  "GNU LGPL version 3"                                                                   '("LGPL-3.0-only")
  "GNU LGPL-3.0"                                                                         '("LGPL-3.0-only")
  "GNU LGPLv3 "                                                                          '("LGPL-3.0-only")
  "GNU Lesser GPL"                                                                       '("LGPL-3.0-only")
  "GNU Lesser General Public Licence"                                                    '("LGPL-3.0-only")
  "GNU Lesser General Public Licence 3.0"                                                '("LGPL-3.0-only")
  "GNU Lesser General Public License"                                                    '("LGPL-3.0-only")
  "GNU Lesser General Public License (LGPL)"                                             '("LGPL-3.0-only")
  "GNU Lesser General Public License (LGPL) Version 3"                                   '("LGPL-3.0-only")
  "GNU Lesser General Public License - v 3"                                              '("LGPL-3.0-only")
  "GNU Lesser General Public License - v 3.0"                                            '("LGPL-3.0-only")
  "GNU Lesser General Public License - v3"                                               '("LGPL-3.0-only")
  "GNU Lesser General Public License 2.1"                                                '("LGPL-2.1-only")
  "GNU Lesser General Public License v2.1"                                               '("LGPL-2.1-only")
  "GNU Lesser General Public License v3.0"                                               '("LGPL-3.0-only")
  "GNU Lesser General Public License version 3"                                          '("LGPL-3.0-only")
  "GNU Lesser General Public License version 3.0"                                        '("LGPL-3.0-only")
  "GNU Lesser General Public License, Version 2.1"                                       '("LGPL-2.1-only")
  "GNU Lesser General Public License, Version 3"                                         '("LGPL-3.0-only")
  "GNU Lesser General Public License, Version 3 or later"                                '("LGPL-3.0-or-later")
  "GNU Lesser General Public License, v. 3 or later"                                     '("LGPL-3.0-or-later")
  "GNU Lesser General Public License, version 2.1 or newer"                              '("LGPL-2.1-or-later")
  "GNU Lesser General Public License, version 3 or later"                                '("LGPL-3.0-or-later")
  "GNU Lesser General Public License, version 3.0 or (at your option) any later version" '("LGPL-3.0-or-later")
  "GNU Lesser General Pulic License v2.1"                                                '("LGPL-2.1-only")
  "GNU Lesser Genereal Public License"                                                   '("LGPL-3.0-only")
  "GNU Lesser Public License"                                                            '("LGPL-3.0-only")
  "GNU Library General Public License"                                                   '("LGPL-3.0-only")
  "GNU Library or Lesser General Public License (LGPL)"                                  '("LGPL-3.0-only")
  "GNU Library or Lesser General Public License (LGPL) 2.1"                              '("LGPL-2.1-only")
  "GNU Library or Lesser General Public License (LGPL) V2.1"                             '("LGPL-2.1-only")
  "Gnu Lesser Public License"                                                            '("LGPL-3.0-only")
  "L GPL 3"                                                                              '("LGPL-3.0-only")
  "LGPL"                                                                                 '("LGPL-3.0-only")
  "LGPL 2.1"                                                                             '("LGPL-2.1-only")
  "LGPL 3.0"                                                                             '("LGPL-3.0-only")
  "LGPL 3.0 (GNU Lesser General Public License)"                                         '("LGPL-3.0-only")
  "LGPL License"                                                                         '("LGPL-3.0-only")
  "LGPL Open Source license"                                                             '("LGPL-3.0-only")
  "LGPL v3"                                                                              '("LGPL-3.0-only")
  "LGPLv2.1"                                                                             '("LGPL-2.1-only")
  "LGPLv3"                                                                               '("LGPL-3.0-only")
  "LGPLv3+"                                                                              '("LGPL-3.0-or-later")
  "Lesser GPL"                                                                           '("LGPL-3.0-only")
  "Lesser General Public License"                                                        '("LGPL-3.0-only")
  "Lesser General Public License (LGPL)"                                                 '("LGPL-3.0-only")
  "Licensed under GNU Lesser General Public License Version 3 or later (the "            '("LGPL-3.0-or-later")
  "lgpl_v2_1"                                                                            '("LGPL-2.1-only")
  })

(def gpl-licenses-and-ids {
  " GNU GENERAL PUBLIC LICENSE Version 3"                                        '("GPL-3.0-only")
  "GNU"                                                                          '("GPL-3.0-only")
  "GNU GENERAL PUBLIC LICENSE"                                                   '("GPL-3.0-only")
  "GNU GENERAL PUBLIC LICENSE Version 2, June 1991"                              '("GPL-2.0-only")
  "GNU GPL"                                                                      '("GPL-3.0-only")
  "GNU GPL 3"                                                                    '("GPL-3.0-only")
  "GNU GPL V2+"                                                                  '("GPL-2.0-or-later")
  "GNU GPL v 3.0"                                                                '("GPL-3.0-only")
  "GNU GPL v. 3"                                                                 '("GPL-3.0-only")
  "GNU GPL v3"                                                                   '("GPL-3.0-only")
  "GNU GPL v3+"                                                                  '("GPL-3.0-or-later")
  "GNU GPL v3.0"                                                                 '("GPL-3.0-only")
  "GNU GPL, version 3, 29 June 2007"                                             '("GPL-3.0-only")
  "GNU GPLv3+"                                                                   '("GPL-3.0-or-later")
  "GNU General Public License"                                                   '("GPL-3.0-only")
  "GNU General Public License (GPL)"                                             '("GPL-3.0-only")
  "GNU General Public License 2"                                                 '("GPL-2.0-only")
  "GNU General Public License V3"                                                '("GPL-3.0-only")
  "GNU General Public License Version 3"                                         '("GPL-3.0-only")
  "GNU General Public License v2.0"                                              '("GPL-2.0-only")
  "GNU General Public License v3"                                                '("GPL-3.0-only")
  "GNU General Public License v3.0"                                              '("GPL-3.0-only")
  "GNU General Public License v3.0 or later"                                     '("GPL-3.0-or-later")
  "GNU General Public License, Version 2"                                        '("GPL-2.0-only")
  "GNU General Public License, Version 3"                                        '("GPL-3.0-only")
  "GNU General Public License, Version 3 (or later)"                             '("GPL-3.0-or-later")
  "GNU General Public License, version 2"                                        '("GPL-2.0-only")
  "GNU General Public License, version 2 (GPL2)"                                 '("GPL-2.0-only")
  "GNU General Public License, version 3"                                        '("GPL-3.0-only")
  "GNU General Public License, version 3 (GPLv3)"                                '("GPL-3.0-only")
  "GNU General Public License,version 2.0 or (at your option) any later version" '("GPL-2.0-or-later")
  "GNU Public License"                                                           '("GPL-3.0-only")
  "GNU Public License V. 3.0"                                                    '("GPL-3.0-only")
  "GNU Public License V3"                                                        '("GPL-3.0-only")
  "GNU Public License v2"                                                        '("GPL-2.0-only")
  "GNU Public License, Version 2"                                                '("GPL-2.0-only")
  "GNU Public License, Version 2.0"                                              '("GPL-2.0-only")
  "GNU Public License, v2"                                                       '("GPL-2.0-only")
  "GNU public licence V3.0"                                                      '("GPL-3.0-only")
  "GNUv3"                                                                        '("GPL-3.0-only")
  "GPL"                                                                          '("GPL-3.0-only")
  "GPL 2.0+"                                                                     '("GPL-2.0-or-later")
  "GPL 3"                                                                        '("GPL-3.0-only")
  "GPL 3.0"                                                                      '("GPL-3.0-only")
  "GPL V3"                                                                       '("GPL-3.0-only")
  "GPL V3+"                                                                      '("GPL-3.0-or-later")
  "GPL v2"                                                                       '("GPL-2.0-only")
  "GPL v2+"                                                                      '("GPL-2.0-or-later")
  "GPL v3"                                                                       '("GPL-3.0-only")
  "GPL version 3"                                                                '("GPL-3.0-only")
  "GPL-3"                                                                        '("GPL-3.0-only")
  "GPL3"                                                                         '("GPL-3.0-only")
  "GPLv2"                                                                        '("GPL-2.0-only")
  "GPLv3"                                                                        '("GPL-3.0-only")
  "General Public License 3"                                                     '("GPL-3.0-only")
  "General Public License v3.0"                                                  '("GPL-3.0-only")
  "The GNU General Public License"                                               '("GPL-3.0-only")
  "The GNU General Public License v3.0"                                          '("GPL-3.0-only")
  "The GNU General Public License, Version 2  "                                  '("GPL-2.0-only")
  })

(def cc-by-licenses-and-ids {
  "Attribution 3.0 Unported"                                                     '("CC-BY-3.0")
  "Attribution 4.0 International"                                                '("CC-BY-4.0")
  "Attribution-NonCommercial-NoDerivs 3.0 Unported"                              '("CC-BY-NC-ND-3.0")
  "CC Attribution 4.0 International with exception for binary distribution"      '("CC-BY-4.0")
  "CC BY-NC"                                                                     '("CC-BY-NC-4.0")
  "Creative Commons 3.0"                                                         '("CC-BY-3.0")
  "Creative Commons Attribution 2.5 License"                                     '("CC-BY-2.5")
  "Creative Commons Attribution License"                                         '("CC-BY-4.0")
  "Creative Commons Attribution Share Alike 4.0 International"                   '("CC-BY-SA-4.0")
  "Creative Commons Attribution-NonCommercial 3.0"                               '("CC-BY-NC-3.0")
  "Creative Commons Attribution-ShareAlike 3.0 US (CC-SA) license"               '("CC-BY-SA-3.0")
  "Creative Commons Attribution-ShareAlike 3.0 US (CC-SA)"                       '("CC-BY-SA-3.0")
  "Creative Commons Attribution-ShareAlike 3.0 Unported License"                 '("CC-BY-SA-3.0")
  "Creative Commons Attribution-ShareAlike 3.0 Unported"                         '("CC-BY-SA-3.0")
  "Creative Commons Attribution-ShareAlike 3.0"                                  '("CC-BY-SA-3.0")
  "Creative Commons Legal Code Attribution 3.0 Unported"                         '("CC-BY-3.0")
  })

(def gnu-licenses-and-ids (merge agpl-licenses-and-ids lgpl-licenses-and-ids gpl-licenses-and-ids))

(def agpl-licenses (set (keys agpl-licenses-and-ids)))
(def lgpl-licenses (set (keys lgpl-licenses-and-ids)))
(def gpl-licenses  (set (keys gpl-licenses-and-ids)))

(def gnu-licenses (set/union agpl-licenses lgpl-licenses gpl-licenses))

; For testing individual GNU family regex components in isolation
(def agpl-only-re (lcu/re-concat #"(?i)\b" "(" agpl-re ")" version-re only-or-later-re))
(def lgpl-only-re (lcu/re-concat #"(?i)\b" "(" lgpl-re ")" version-re only-or-later-re))
(def gpl-only-re  (lcu/re-concat #"(?i)\b" "(" gpl-re  ")" version-re only-or-later-re))

(def not-nil? (complement nil?))

; Add input to result to make troubleshooting test failures easier
(defn test-regex
  [re s]
  (when-let [result (rencg/re-find-ncg re s)]
    (assoc result :input s)))

(deftest gnu-regex-components-tests
  (testing "GNU Family Regexes - correct matching and non-matching - AGPL component"
    (is (every? not-nil? (map (partial test-regex agpl-only-re) agpl-licenses)))
    (is (every? nil?     (map (partial test-regex agpl-only-re) lgpl-licenses)))
    (is (every? nil?     (map (partial test-regex agpl-only-re) gpl-licenses))))
  (testing "GNU Family Regexes - correct matching and non-matching - LGPL component"
    (is (every? nil?     (map (partial test-regex lgpl-only-re) agpl-licenses)))
    (is (every? not-nil? (map (partial test-regex lgpl-only-re) lgpl-licenses)))
    (is (every? nil?     (map (partial test-regex lgpl-only-re) gpl-licenses))))
  (testing "GNU Family Regexes - correct matching and non-matching - GPL component"
    (is (every? nil?     (map (partial test-regex gpl-only-re) agpl-licenses)))
    (is (every? nil?     (map (partial test-regex gpl-only-re) lgpl-licenses)))
    (is (every? not-nil? (map (partial test-regex gpl-only-re) gpl-licenses)))))

(deftest combined-regex-components-tests
  (testing "GNU Family Regexes - correct matching - combined GNU family regex"
    (is (every? not-nil? (map (partial test-regex gnu-re) gnu-licenses)))))

(deftest match-regexes-tests
  (testing-with-data "GNU Family Regexes - correct identifier results" #(mapcat keys (matches %)) gnu-licenses-and-ids)
  (testing-with-data "CC Family Regexes - correct identifier results"  #(mapcat keys (matches %)) cc-by-licenses-and-ids))
