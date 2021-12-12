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
  "Public API namespace for lice-comb."
  (:require [clojure.string     :as s]
            [clojure.java.io    :as io]
            [clojure.data.xml   :as xml]
            [xml-in.core        :as xi]
            [clojure.java.shell :as sh]
            [lice-comb.spdx     :as spdx]))

(def ^:private local-maven-repo
  (let [sh-result (sh/sh "mvn" "help:evaluate" "-Dexpression=settings.localRepository" "-q" "-DforceStdout")]
    (if (= 0 (:exit sh-result))
      (s/trim (:out sh-result))
      (throw (ex-info "Unable to determine local Maven repository location - is Maven installed correctly and in the PATH?" sh-result)))))

(def ^:private remote-maven-repos #{"https://repo1.maven.org/maven2" "https://repo.clojars.org"})

(defn- uri-resolves?
  "Does the given URI resolve (i.e. does the resource it points to exist)?"
  [^java.net.URI uri]
  (and uri
       (let [http (doto (.openConnection (.toURL uri))
                        (.setRequestMethod "HEAD"))]
         (= 200 (.getResponseCode http)))))

(defn- pom-uri-for-gav
  "Attempts to locate the POM for the given GAV, which is a URI that may point to a file in the local Maven repository or a remote Maven repository (e.g. on Maven Central or Clojars)."
  [group-id artifact-id version]
  (when (and (not (s/blank? group-id))
             (not (s/blank? artifact-id))
             (not (s/blank? version)))
    (let [gav-path  (str (s/replace "." "/" group-id) "/" artifact-id "/" version "/" artifact-id "-" version ".pom")
          local-pom (io/file (str local-maven-repo "/" gav-path))]
      (if (and (.exists local-pom)
               (.isFile local-pom))
        (.toURI local-pom)
        (first (filter uri-resolves? (map #(java.net.URI. (str % "/" gav-path)) remote-maven-repos)))))))

(defn- license-from-pair
  "Attempts to determine the license from a POM license name/URL pair."
  [{:keys [name url]}]
  (if-let [license (spdx/uri->id url)]
    license
    (spdx/name->ids name)))

(xml/alias-uri 'pom "http://maven.apache.org/POM/4.0.0")

(defmulti from-pom
  "Attempt to detect the license(s) reported in a pom.xml file. pom may be a java.io.InputStream, or anything that can be opened by clojure.java.io/input-stream."
  (fn [pom] (type pom)))

(defmethod from-pom java.io.InputStream
  [pom-is]
  (let [pom-xml             (xml/parse pom-is)
        licenses            (xi/find-all pom-xml [::pom/project ::pom/licenses ::pom/license])
        licenses-without-ns (xi/find-all pom-xml [:project      :licenses      :license])]; Note: a few rare pom.xml files are missing an xmlns declation (e.g. software.amazon.ion/ion-java) - this catches those
    (if (and (empty? licenses)
             (empty? licenses-without-ns))
      ; License block doesn't exist, so attempt to lookup the parent pom
      (if-let [parent (xi/find-first pom-xml [::pom/project ::pom/parent])]
        (let [group-id       (s/trim (xi/find-first parent [::pom/groupId]))
              artifact-id    (s/trim (xi/find-first parent [::pom/artifactId]))
              version        (s/trim (xi/find-first parent [::pom/version]))]
          (when-let [parent-pom-uri (pom-uri-for-gav group-id artifact-id version)]
            (from-pom parent-pom-uri)))
        (when-let [parent (xi/find-first pom-xml [:project :parent])]
          (let [group-id       (s/trim (xi/find-first parent [:groupId]))
                artifact-id    (s/trim (xi/find-first parent [:artifactId]))
                version        (s/trim (xi/find-first parent [:version]))]
            (when-let [parent-pom-uri (pom-uri-for-gav group-id artifact-id version)]
              (from-pom parent-pom-uri)))))
      ; License block exists - process it
      (let [name-uri-pairs (seq
                             (distinct
                               (concat (map #(hash-map :name %1 :url %2) (xi/find-all licenses [::pom/name]) (xi/find-all licenses [::pom/url]))
                                       (map #(hash-map :name %1 :url %2) (xi/find-all licenses [:name])      (xi/find-all licenses [:url])))))]
        (seq (distinct (keep license-from-pair name-uri-pairs)))))))

(defmethod from-pom :default
  [pom]
  (when pom
    (with-open [pom-is (io/input-stream pom)]
      (from-pom pom-is))))
