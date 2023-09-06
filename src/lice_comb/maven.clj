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

(ns lice-comb.maven
  "Functionality related to finding and determining license information from
  Maven POMs."
  (:require [clojure.string                  :as s]
            [clojure.java.io                 :as io]
            [clojure.data.xml                :as xml]
            [clojure.java.shell              :as sh]
            [clojure.tools.logging           :as log]
            [xml-in.core                     :as xi]
            [lice-comb.matching              :as lcmtch]
            [lice-comb.impl.matching         :as lcim]
            [lice-comb.impl.expressions-info :as lciei]
            [lice-comb.impl.http             :as lcihttp]
            [lice-comb.impl.utils            :as lciu]))

(def ^:private local-maven-repo-d
  (delay
    (try
      ; The command:
      ;     mvn help:evaluate -Dexpression=settings.localRepository -q -DforceStdout
      ; determines where the local repository is located.
      (let [sh-result (sh/sh "mvn" "help:evaluate" "-Dexpression=settings.localRepository" "-q" "-DforceStdout")]
        (if (zero? (:exit sh-result))
          (s/trim (:out sh-result))
          (str (System/getProperty "user.home") "/.m2/repository")))
      (catch java.io.IOException _
        (str (System/getProperty "user.home") "/.m2/repository")))))

; TODO: make this configurable
(def ^:private remote-maven-repos #{"https://repo.maven.apache.org/maven2" "https://repo.clojars.org"})

(defn pom-uri-for-gav
  "Attempts to locate the POM for the given GAV, which is a URI that may point
  to a file in the local Maven repository or a remote Maven repository (e.g. on
  Maven Central or Clojars)."
  ([{:keys [group-id artifact-id version]}] (pom-uri-for-gav group-id artifact-id version))
  ([group-id artifact-id version]
   (when (and (not (s/blank? group-id))
              (not (s/blank? artifact-id))
              (not (s/blank? version)))
     (let [gav-path  (str (s/replace group-id "." "/") "/" artifact-id "/" version "/" artifact-id "-" version ".pom")
           local-pom (io/file (str @local-maven-repo-d "/" gav-path))]
       (if (and (.exists local-pom)
                (.isFile local-pom))
         (.toURI local-pom)
         (first (filter lcihttp/uri-resolves? (map #(str % "/" gav-path) remote-maven-repos))))))))

(defn- licenses-from-pair
  "Attempts to determine the license(s) (a map) from a POM license name/URL
  pair. Returns nil if no matches were found."
  [{:keys [name url]}]
  ; 1. Look in the name field(s)
  (if-let [name-expressions (lciei/prepend-source "<name>" (lcmtch/name->expressions-info name))]
    name-expressions
    ; 2. If the names didn't give us any licenses, look in the url field(s) (this tends to be slower and less accurate)
    (when-let [uri-ids (lciei/prepend-source "<url>" (lcmtch/uri->ids-info url))]
      uri-ids)))

(xml/alias-uri 'pom "http://maven.apache.org/POM/4.0.0")

(defn- xml-find-all-alts
  "As for xi/find-all, but supports an alternative fallback set of tags (to
  help with namespace messes in pom.xml files)."
  [xml ks1 ks2]
  (if-let [result (seq (xi/find-all xml ks1))]
    result
    (seq (xi/find-all xml ks2))))

(defn- xml-find-first-string
  "As for xi/find-first, but assumes the target is a single content tag (and
  returns that, or nil if it's blank or the tag doesn't exist."
  [xml ks]
  (when-let [result (first (xi/find-first xml ks))]
    (when-not (s/blank? result)
      result)))

(defn- xml-find-first-string-alts
  "As for xml-find-first-string, but supports an alternative fallback set of
  tags (to help with namespace messes in pom.xml files)."
  [xml ks1 ks2]
  (if-let [result (xml-find-first-string xml ks1)]
    result
    (xml-find-first-string xml ks2)))

(defmulti pom->expressions-info
  "Attempt to detect the license expression(s) (a map) reported in a pom.xml
  file. pom may be a java.io.InputStream, or anything that can be opened by
  clojure.java.io/input-stream.

  Note that if an InputStream is provided:
  1. it's the caller's responsibility to open and close it
  2. a filepath *must* be provided along with the stream (the 2nd arg)

  The result has metadata attached that describes how the identifiers in the
  expression(s) were determined."
  {:arglists '([pom] [pom filepath])}
  (fn [& args] (type (first args))))

; Note: a few rare pom.xml files are missing the xmlns declation (e.g. software.amazon.ion/ion-java) - so we look for both namespaced and non-namespaced versions of all tags
(defmethod pom->expressions-info java.io.InputStream
  [pom-is filepath]
  (lciei/prepend-source filepath
                        (let [pom-xml (xml/parse pom-is)]
                          (if-let [pom-licenses (xml-find-all-alts pom-xml [::pom/project ::pom/licenses] [:project :licenses])]
                            ; <licenses> block exists - process it
                            (let [name-uri-pairs (some->> pom-licenses
                                                          (filter map?)                                                    ; Get rid of non-tag content (whitespace etc.)
                                                          (filter #(or (= ::pom/license (:tag %)) (= :license (:tag %))))  ; Get rid of non <license> tags (which shouldn't exist, but Maven POMs are a shitshow...)
                                                          (map #(identity (let [name (xml-find-first-string-alts % [::pom/license ::pom/name] [:license :name])
                                                                                url  (xml-find-first-string-alts % [::pom/license ::pom/url]  [:license :url])]
                                                                            (when (or name url)
                                                                              {:name name :url url}))))
                                                          set)
                                  licenses       (into {} (map licenses-from-pair name-uri-pairs))]
                              (lcim/manual-fixes licenses))
                            ; License block doesn't exist, so attempt to lookup the parent pom and get it from there
                            (let [parent       (seq (xi/find-first pom-xml [::pom/project ::pom/parent]))
                                  parent-no-ns (seq (xi/find-first pom-xml [:project      :parent]))
                                  parent-gav   (merge {}
                                                      (when parent       {:group-id    (lciu/strim (first (xi/find-first parent       [::pom/groupId])))
                                                                          :artifact-id (lciu/strim (first (xi/find-first parent       [::pom/artifactId])))
                                                                          :version     (lciu/strim (first (xi/find-first parent       [::pom/version])))})
                                                      (when parent-no-ns {:group-id    (lciu/strim (first (xi/find-first parent-no-ns [:groupId])))
                                                                          :artifact-id (lciu/strim (first (xi/find-first parent-no-ns [:artifactId])))
                                                                          :version     (lciu/strim (first (xi/find-first parent-no-ns [:version])))}))]
                              (when-not (empty? parent-gav)
                                (pom->expressions-info (pom-uri-for-gav parent-gav))))))))   ; Note: naive (stack consuming) recursion, which is fine here as pom hierarchies are rarely very deep

(defmethod pom->expressions-info :default
  ([pom] (pom->expressions-info pom (lciu/filepath pom)))
  ([pom filepath]
   (when pom
     (with-open [pom-is (io/input-stream pom)]
       (if-let [expressions (pom->expressions-info pom-is filepath)]
         expressions
         (log/info (str "'" filepath "'") "contains no license information"))))))

(defn pom->expressions
  "Attempt to detect the license expression(s) (a set) reported in a pom.xml
  file. pom may be a java.io.InputStream, or anything that can be opened by
  clojure.java.io/input-stream.

  Note that if an InputStream is provided:
  1. it's the caller's responsibility to open and close it
  2. a filepath *must* be provided along with the stream (the 2nd arg)

  The result has metadata attached that describes how the identifiers in the
  expression(s) were determined."
  ([pom] (pom->expressions pom (lciu/filepath pom)))
  ([pom filepath]
   (some-> (pom->expressions-info pom filepath)
           keys
           set)))

(defn init!
  "Initialises this namespace upon first call (and does nothing on subsequent
  calls), returning nil. Consumers of this namespace are not required to call
  this fn, as initialisation will occur implicitly anyway; it is provided to
  allow explicit control of the cost of initialisation to callers who need it."
  []
  (lcmtch/init!)
  @local-maven-repo-d
  nil)
