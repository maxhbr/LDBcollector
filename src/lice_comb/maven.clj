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
  (:require [clojure.string        :as s]
            [clojure.java.io       :as io]
            [clojure.data.xml      :as xml]
            [clojure.java.shell    :as sh]
            [clojure.tools.logging :as log]
            [xml-in.core           :as xi]
            [lice-comb.matching    :as lcmtch]
            [lice-comb.impl.utils  :as lcu]))

(def ^:private local-maven-repo-d
  (delay
    (try
      (let [sh-result (sh/sh "mvn" "help:evaluate" "-Dexpression=settings.localRepository" "-q" "-DforceStdout")]
        (if (zero? (:exit sh-result))
          (s/trim (:out sh-result))
          (str (System/getProperty "user.home") "/.m2/repository")))
      (catch java.io.IOException _
        (str (System/getProperty "user.home") "/.m2/repository")))))

; TODO: make this configurable
(def ^:private remote-maven-repos #{"https://repo.maven.apache.org/maven2" "https://repo.clojars.org"})

(defn- uri-resolves?
  "Does the given URI resolve (i.e. does the resource it points to exist)?"
  [^java.net.URI uri]
  (and uri
       (let [http (doto ^java.net.HttpURLConnection (.openConnection (.toURL uri))
                        (.setRequestMethod "HEAD"))]
         (= 200 (.getResponseCode http)))))

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
         (first (filter uri-resolves? (map #(java.net.URI. (str % "/" gav-path)) remote-maven-repos))))))))

(defn- licenses-from-pair
  "Attempts to determine the license(s) (a set) from a POM license name/URL pair."
  [{:keys [name url]}]
  ; Attempt to find a match by URL first
  (if-let [licenses (lcmtch/fuzzy-match-uri->license-ids url)]
    licenses
    ; Then match by name
    (if-let [licenses (lcmtch/fuzzy-match-name->license-ids name)]
      licenses
      #{(lcmtch/name->unlisted name)})))  ; Last resort - return an unlisted identifier that includes the name (if any)

(xml/alias-uri 'pom "http://maven.apache.org/POM/4.0.0")

(defmulti pom->ids
  "Attempt to detect the license(s) reported in a pom.xml file. pom may be a
  java.io.InputStream, or anything that can be opened by clojure.java.io/input-stream.

  Note: if an InputStream is provided, it's the caller's responsibility to open
  and close it."
  {:arglists '([pom])}
  type)

; Note: a few rare pom.xml files are missing the xmlns declation (e.g. software.amazon.ion/ion-java) - so we look for both namespaced and non-namespaced versions of all tags here
(defmethod pom->ids java.io.InputStream
  [pom-is]
  (let [pom-xml        (xml/parse pom-is)
        licenses       (seq (xi/find-all pom-xml [::pom/project ::pom/licenses ::pom/license]))
        licenses-no-ns (seq (xi/find-all pom-xml [:project      :licenses      :license]))]
    (if (or licenses licenses-no-ns)
      ; Licenses block exists - process it
      (let [name-uri-pairs (lcu/nset (concat (lcu/map-pad #(hash-map :name (lcu/strim %1) :url (lcu/strim %2)) (xi/find-all licenses       [::pom/name]) (xi/find-all licenses       [::pom/url]))
                                             (lcu/map-pad #(hash-map :name (lcu/strim %1) :url (lcu/strim %2)) (xi/find-all licenses-no-ns [:name])      (xi/find-all licenses-no-ns [:url]))))]
        (lcu/nset (mapcat licenses-from-pair name-uri-pairs)))
      ; License block doesn't exist, so attempt to lookup the parent pom and get it from there
      (let [parent       (seq (xi/find-first pom-xml [::pom/project ::pom/parent]))
            parent-no-ns (seq (xi/find-first pom-xml [:project      :parent]))
            parent-gav   (merge {}
                                (when parent       {:group-id    (lcu/strim (first (xi/find-first parent       [::pom/groupId])))
                                                    :artifact-id (lcu/strim (first (xi/find-first parent       [::pom/artifactId])))
                                                    :version     (lcu/strim (first (xi/find-first parent       [::pom/version])))})
                                (when parent-no-ns {:group-id    (lcu/strim (first (xi/find-first parent-no-ns [:groupId])))
                                                    :artifact-id (lcu/strim (first (xi/find-first parent-no-ns [:artifactId])))
                                                    :version     (lcu/strim (first (xi/find-first parent-no-ns [:version])))}))]
        (when-not (empty? parent-gav)
          (pom->ids (pom-uri-for-gav parent-gav)))))))   ; Note: naive (stack consuming) recursion, which is fine here as pom hierarchies are rarely very deep

(defmethod pom->ids :default
  [pom]
  (when pom
    (with-open [pom-is (io/input-stream pom)]
      (if-let [pom-licenses (pom->ids pom-is)]
        pom-licenses
        (log/info (str "'" pom "'") "contains no license information")))))

(defn init!
  "Initialises this namespace upon first call (and does nothing on subsequent
  calls), returning nil. Consumers of this namespace are not required to call
  this fn, as initialisation will occur implicitly anyway; it is provided to
  allow explicit control of the cost of initialisation to callers who need it."
  []
  @local-maven-repo-d
  nil)
