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

(ns lice-comb.utils-test
  (:require [clojure.test               :refer [deftest testing is use-fixtures]]
            [lice-comb.test-boilerplate :refer [fixture]]
            [lice-comb.impl.utils       :refer [simplify-uri]]))

(use-fixtures :once fixture)

(def simplified-apache2-uri "http://apache.org/licenses/license-2.0")

(deftest simplify-uri-tests
  (testing "Nil, empty or blank values"
    (is (nil? (simplify-uri nil)))
    (is (nil? (simplify-uri "")))
    (is (nil? (simplify-uri "       ")))
    (is (nil? (simplify-uri "\n")))
    (is (nil? (simplify-uri "\t"))))
  (testing "Values that are not uris"
    (is (= "foo"    (simplify-uri "FOO")))
    (is (= "foo"    (simplify-uri "foo")))
    (is (= "foobar" (simplify-uri "   FoObAr    "))))
  (testing "Values that are non-http(s) uris"
    (is (= "ftp://user@host/foo/bar.txt" (simplify-uri "ftp://user@host/foo/bar.txt")))
    (is (= "ftp://user@host/foo/bar.txt" (simplify-uri "FTP://USER@HOST/FOO/BAR.TXT")))
    (is (= "mailto:someone@example.com?subject=this%20is%20the%20subject&cc=someone_else@example.com&body=this%20is%20the%20body"
           (simplify-uri "mailto:someone@example.com?subject=This%20is%20the%20subject&cc=someone_else@example.com&body=This%20is%20the%20body"))))
  (testing "Valid uris that don't get simplified"
    (is (= simplified-apache2-uri                                    (simplify-uri simplified-apache2-uri)))
    (is (= "http://creativecommons.org/licenses/by-sa/4.0/legalcode" (simplify-uri "http://creativecommons.org/licenses/by-sa/4.0/legalcode"))))
  (testing "Valid uris that get simplified"
    (is (= simplified-apache2-uri                                           (simplify-uri "http://www.apache.org/licenses/LICENSE-2.0")))
    (is (= simplified-apache2-uri                                           (simplify-uri "https://www.apache.org/licenses/LICENSE-2.0")))
    (is (= simplified-apache2-uri                                           (simplify-uri "http://www.apache.org/licenses/LICENSE-2.0.html")))
    (is (= simplified-apache2-uri                                           (simplify-uri "https://www.apache.org/licenses/LICENSE-2.0.html")))
    (is (= simplified-apache2-uri                                           (simplify-uri "http://www.apache.org/licenses/LICENSE-2.0.html")))
    (is (= simplified-apache2-uri                                           (simplify-uri "https://www.apache.org/licenses/LICENSE-2.0.txt")))
    (is (= simplified-apache2-uri                                           (simplify-uri "https://www.apache.org/licenses/license-2.0.txt")))
    (is (= simplified-apache2-uri                                           (simplify-uri "http://apache.org/licenses/LICENSE-2.0.pdf")))
    (is (= simplified-apache2-uri                                           (simplify-uri "               http://www.apache.org/licenses/LICENSE-2.0.html             ")))
    (is (= "http://gnu.org/licenses/agpl"                                   (simplify-uri "https://www.gnu.org/licenses/agpl.txt")))
    (is (= "http://gnu.org/software/classpath/license"                      (simplify-uri "https://www.gnu.org/software/classpath/license.html")))
    (is (= "http://raw.githubusercontent.com/pmonks/lice-comb/main/license" (simplify-uri "https://raw.githubusercontent.com/pmonks/lice-comb/main/LICENSE")))
    (is (= "http://github.com/pmonks/lice-comb/blob/main/license"           (simplify-uri "https://github.com/pmonks/lice-comb/blob/main/LICENSE")))))
