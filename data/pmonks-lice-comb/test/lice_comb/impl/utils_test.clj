;
; Copyright © 2023 Peter Monks
;
; This Source Code Form is subject to the terms of the Mozilla Public
; License, v. 2.0. If a copy of the MPL was not distributed with this
; file, You can obtain one at https://mozilla.org/MPL/2.0/.
;
; SPDX-License-Identifier: MPL-2.0
;

(ns lice-comb.impl.utils-test
  (:require [clojure.test               :refer [deftest testing is use-fixtures]]
            [clojure.java.io            :as io]
            [lice-comb.test-boilerplate :refer [fixture test-data-path]]
            [lice-comb.impl.utils       :refer [simplify-uri filepath filename html->text]]))

(use-fixtures :once fixture)

(def simplified-apache2-uri "http://apache.org/license/license-2.0")
(def local-mpl2-html        (str test-data-path "/MPL-2.0/LICENSE.html"))

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
    (is (= simplified-apache2-uri                                   (simplify-uri simplified-apache2-uri)))
    (is (= "http://creativecommons.org/license/by-sa/4.0/legalcode" (simplify-uri "http://creativecommons.org/licenses/by-sa/4.0/legalcode"))))
  (testing "Valid uris that get simplified"
    (is (= simplified-apache2-uri                                           (simplify-uri "http://www.apache.org/licenses/LICENSE-2.0")))
    (is (= simplified-apache2-uri                                           (simplify-uri "https://www.apache.org/licenses/LICENSE-2.0")))
    (is (= simplified-apache2-uri                                           (simplify-uri "http://www.apache.org/licenses/LICENSE-2.0.html")))
    (is (= simplified-apache2-uri                                           (simplify-uri "https://www.apache.org/licenses/LICENSE-2.0.html")))
    (is (= simplified-apache2-uri                                           (simplify-uri "http://www.apache.org/licenses/LICENSE-2.0.html")))
    (is (= simplified-apache2-uri                                           (simplify-uri "https://www.apache.org/licenses/LICENSE-2.0.txt")))
    (is (= simplified-apache2-uri                                           (simplify-uri "https://www.apache.org/licenses/license-2.0.txt")))
    (is (= simplified-apache2-uri                                           (simplify-uri "https://www.apache.org/licenses/license-2.0.md")))
    (is (= simplified-apache2-uri                                           (simplify-uri "http://apache.org/licenses/LICENSE-2.0.pdf")))
    (is (= simplified-apache2-uri                                           (simplify-uri "               http://www.apache.org/licenses/LICENSE-2.0.html             ")))
    (is (= "http://gnu.org/license/agpl"                                    (simplify-uri "https://www.gnu.org/licenses/agpl.txt")))
    (is (= "http://opensource.org/license/mit"                              (simplify-uri "https://opensource.org/license/MIT")))
    (is (= "http://opensource.org/license/mit"                              (simplify-uri "https://opensource.org/license/MIT/")))
    (is (= "http://opensource.org/license/mit"                              (simplify-uri "https://opensource.org/license/mit/")))
    (is (= "http://opensource.org/license/mit"                              (simplify-uri "https://opensource.org/license/MIT.TXT")))
    (is (= "http://opensource.org/license/mit"                              (simplify-uri "https://opensource.org/licence/MIT")))
    (is (= "http://opensource.org/license/mit"                              (simplify-uri "https://opensource.org/licenses/MIT")))
    (is (= "http://opensource.org/license/mit"                              (simplify-uri "https://opensource.org/licences/MIT")))
    (is (= "http://gnu.org/software/classpath/license"                      (simplify-uri "https://www.gnu.org/software/classpath/license.html")))
    (is (= "http://raw.githubusercontent.com/pmonks/lice-comb/main/license" (simplify-uri "https://raw.githubusercontent.com/pmonks/lice-comb/main/LICENSE")))
    (is (= "http://github.com/pmonks/lice-comb/blob/main/license"           (simplify-uri "https://github.com/pmonks/lice-comb/blob/main/LICENSE")))))

(deftest filepath-tests
  (testing "Nil, empty or blank values"
    (is (nil? (filepath nil)))
    (is (= "" (filepath "")))
    (is (= "" (filepath "       ")))
    (is (= "" (filepath "\n")))
    (is (= "" (filepath "\t"))))
  (testing "Files"
    (is (= "/file.txt"                                               (filepath (io/file "/file.txt"))))
    (is (= "/some/path/or/other/file.txt"                           (filepath (io/file "/some/path/or/other/file.txt")))))
  (testing "Strings"
    (is (= "file.txt"                                               (filepath "file.txt")))
    (is (= "/some/path/or/other/file.txt"                           (filepath "/some/path/or/other/file.txt")))
    (is (= "https://www.google.com/"                                (filepath "https://www.google.com/")))
    (is (= "https://www.google.com/"                                (filepath "       https://www.google.com/       ")))
    (is (= "https://github.com/pmonks/lice-comb/blob/main/deps.edn" (filepath "https://github.com/pmonks/lice-comb/blob/main/deps.edn"))))
  (testing "ZipEntries"
    (is (= "file.txt"                                               (filepath (java.util.zip.ZipEntry. "file.txt"))))
    (is (= "/some/path/or/other/file.txt"                           (filepath (java.util.zip.ZipEntry. "/some/path/or/other/file.txt")))))
  (testing "URLs"
    (is (= "https://www.google.com/"                                (filepath (io/as-url "https://www.google.com/"))))
    (is (= "https://github.com/pmonks/lice-comb/blob/main/deps.edn" (filepath (io/as-url "https://github.com/pmonks/lice-comb/blob/main/deps.edn")))))
  (testing "URIs"
    (is (= "https://www.google.com/"                                (filepath (java.net.URI. "https://www.google.com/"))))
    (is (= "https://github.com/pmonks/lice-comb/blob/main/deps.edn" (filepath (java.net.URI. "https://github.com/pmonks/lice-comb/blob/main/deps.edn")))))
  (testing "InputStream"
    (is (thrown? clojure.lang.ExceptionInfo                         (filepath (io/input-stream "deps.edn"))))))

(deftest filename-tests
  (testing "Nil, empty or blank values"
    (is (nil? (filename nil)))
    (is (= "" (filename "")))
    (is (= "" (filename "       ")))
    (is (= "" (filename "\n")))
    (is (= "" (filename "\t"))))
  (testing "Files"
    (is (= "file.txt" (filename (io/file "file.txt"))))
    (is (= "file.txt" (filename (io/file "/some/path/or/other/file.txt")))))
  (testing "Strings"
    (is (= "file.txt" (filename "file.txt")))
    (is (= "file.txt" (filename "/some/path/or/other/file.txt")))
    (is (= ""         (filename "https://www.google.com")))
    (is (= ""         (filename "https://www.google.com/")))
    (is (= "deps.edn" (filename "https://github.com/pmonks/lice-comb/blob/main/deps.edn"))))
  (testing "ZipEntries"
    (is (= "file.txt" (filename (java.util.zip.ZipEntry. "file.txt"))))
    (is (= "file.txt" (filename (java.util.zip.ZipEntry. "/some/path/or/other/file.txt")))))
  (testing "URLs"
    (is (= ""         (filename (io/as-url "https://www.google.com/"))))
    (is (= "deps.edn" (filename (io/as-url "https://github.com/pmonks/lice-comb/blob/main/deps.edn")))))
  (testing "URIs"
    (is (= ""         (filename (java.net.URI. "https://www.google.com/"))))
    (is (= "deps.edn" (filename (java.net.URI. "https://github.com/pmonks/lice-comb/blob/main/deps.edn")))))
  (testing "InputStream"
    (is (thrown? clojure.lang.ExceptionInfo (filename (io/input-stream "deps.edn"))))))

(deftest html->text-tests
  (testing "Nil, empty or blank values"
    (is (nil? (html->text nil)))
    (is (= "" (html->text "")))
    (is (= "" (filename "       ")))
    (is (= "" (filename "\n")))
    (is (= "" (filename "\t"))))
  (testing "Simple HTML"
    (is (= "Hello, world!" (html->text "Hello, world!")))
    (is (= "Hello, world!" (html->text "<html><body><p>Hello, world!</p></body></html>")))
    (is (= "Hello, world!" (html->text "<html><body><h1>Hello, world!</h1></body></html>")))
    (is (= "Hello, world!" (html->text "<html><head><title>Hello, world!</title></head></html>")))
    (is (= ""              (html->text "<html><body><p class=\"Hello, world!\"></p></body></html>"))))
  (testing "Real world HTML"
    (is (= "Mozilla Public License, version 2.0" (subs (html->text (slurp local-mpl2-html)) 0 35)))))
