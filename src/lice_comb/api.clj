;
; Copyright © 2021 Peter Monks
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

(ns lice-comb.api
  "Public API namespace for lice-comb."
  (:require [clojure.string  :as s]
            [lice-comb.spdx  :as spdx]
            [lice-comb.maven :as mvn]
            [lice-comb.utils :as u]))

(defn from-name
  "Attempt to detect the license(s) from a license name (e.g. \"Apache License, Version 2.0\" returns [\"Apache-2.0\"])."
  [license-name]
  (spdx/from-name license-name))

(defn from-uri
  "Attempt to detect the license from a license URI (e.g. \"https://www.apache.org/licenses/LICENSE-2.0\" returns \"Apache-2.0\"). license-uri may be a string, a java.net.URL, or a java.net.URI."
  [license-uri]
  (spdx/uri->id license-uri))

(defn from-text
  "Attempt to detect the license(s) from a block of text. text may be a string, a java.io.InputStream, or anything accepted by clojure.java.io/input-stream."
  [text]
  (spdx/from-text text))

(defn from-pom
  "Attempt to detect the license(s) reported in a pom.xml file. pom may be a string, java.io.File, or java.io.InputStream."
  [pom]
  (mvn/from-pom pom))

(defn from-dir
  "Attempt to detect the license(s) located in a directory. dir may be a string or a java.io.File."
  [dir]
  ;####TODO: Implement me!
  (throw (ex-info "Not yet implemented." {})))

(defn from-zip
  "Attempt to detect the license(s) located in a file in ZIP format (note: this includes JAR files). zip may be a string or a java.io.File."
  [zip]
  ;####TODO: Implement me!
  (throw (ex-info "Not yet implemented." {})))
