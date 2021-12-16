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

(ns build
  "Build script for lice-comb.

For more information, run:

clojure -A:deps -T:build help/doc"
  (:refer-clojure :exclude [test])
  (:require [clojure.tools.build.api :as b]
            [org.corfield.build      :as bb]
            [tools-convenience.api   :as tc]
            [tools-pom.tasks         :as pom]
            [tools-licenses.tasks    :as lic]
            [pbr.tasks               :as pbr]))

(def lib       'com.github.pmonks/lice-comb)
(def version   (format "1.0.%s" (b/git-count-revs nil)))

; Utility fns
(defn- set-opts
  [opts]
  (assoc opts
         :lib          lib
         :version      version
         :write-pom    true
         :validate-pom true
         :pom          {:description      "A Clojure library for software license detection."
                        :url              "https://github.com/pmonks/lice-comb"
                        :licenses         [:license   {:name "Apache License 2.0" :url "http://www.apache.org/licenses/LICENSE-2.0.html"}]
                        :developers       [:developer {:id "pmonks" :name "Peter Monks" :email "pmonks+lice-comb@gmail.com"}]
                        :scm              {:url "https://github.com/pmonks/lice-comb" :connection "scm:git:git://github.com/pmonks/lice-comb.git" :developer-connection "scm:git:ssh://git@github.com/pmonks/lice-comb.git"}
                        :issue-management {:system "github" :url "https://github.com/pmonks/lice-comb/issues"}}))

; Build tasks
(defn clean
  "Clean up the project."
  [opts]
  (bb/clean (set-opts opts)))

(defn check
  "Check the code by compiling it."
  [opts]
  (bb/run-task (set-opts opts) [:check]))

(defn outdated
  "Check for outdated dependencies."
  [opts]
  (bb/run-task (set-opts opts) [:outdated]))

(defn test
  "Run the tests."
  [opts]
  (bb/run-tests (set-opts opts)))

(defn kondo
  "Run the clj-kondo linter."
  [opts]
  (bb/run-task (set-opts opts) [:kondo]))

(defn eastwood
  "Run the eastwood linter."
  [opts]
  (bb/run-task (set-opts opts) [:eastwood]))

(defn lint
  "Run all linters."
  [opts]
  (-> opts
      (kondo)
      (eastwood)))

(defn ci
  "Run the CI pipeline."
  [opts]
  (let [opts (set-opts opts)]
    (outdated opts)
    (check    opts)
    (test     opts)
    (lint     opts)))

(defn licenses
  "Attempts to list all licenses for the transitive set of dependencies of the project, using SPDX license expressions."
  [opts]
  (-> opts
      (set-opts)
      (lic/licenses)))

(defn check-asf-policy
  "Checks this project's dependencies' licenses against the ASF's 3rd party license policy (https://www.apache.org/legal/resolved.html)."
  [opts]
  (-> opts
      (set-opts)
      (lic/check-asf-policy)))

(defn check-release
  "Check that a release can be done from the current directory."
  [opts]
  (-> opts
      (set-opts)
      (ci)
      (pbr/check-release)))

(defn release
  "Release a new version of the library."
  [opts]
  (check-release opts)
  (-> opts
      (set-opts)
      (pbr/release)))

(defn jar
  "Generates a library JAR for the project."
  [opts]
  (-> opts
      (set-opts)
      (pom/pom)
      (bb/jar)))

(defn deploy
  "Deploys the library JAR to Clojars."
  [opts]
  (-> opts
      (set-opts)
      (pbr/deploy)))

(defn docs
  "Generates codox documentation"
  [_]
  (tc/ensure-command "clojure")
  (tc/exec "clojure -Srepro -X:codox"))
