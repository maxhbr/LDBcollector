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
  "Functionality related to combing Maven POMs for license information."
  (:require [clojure.string                  :as s]
            [clojure.java.io                 :as io]
            [clojure.java.shell              :as sh]
            [clojure.data.xml                :as xml]
            [clojure.tools.logging           :as log]
            [xml-in.core                     :as xi]
            [lice-comb.matching              :as lcmtch]
            [lice-comb.impl.matching         :as lcim]
            [lice-comb.impl.expressions-info :as lciei]
            [lice-comb.impl.http             :as lcihttp]
            [lice-comb.impl.utils            :as lciu]))

(def ^:private separator java.io.File/separator)

(def ^:private local-maven-repo-d
  (delay
    (try
      ; The command:
      ;     mvn help:evaluate -Dexpression=settings.localRepository -q -DforceStdout
      ; determines where the local repository is located.
      (let [sh-result (sh/sh "mvn" "help:evaluate" "-Dexpression=settings.localRepository" "-q" "-DforceStdout")]
        (if (zero? (:exit sh-result))
          (s/trim (:out sh-result))
          (str (System/getProperty "user.home") (str separator ".m2" separator "repository"))))
      (catch java.io.IOException _
        (str (System/getProperty "user.home") (str separator ".m2" separator "repository"))))))

; TODO: make this configurable
(def ^:private remote-maven-repos {"central" "https://repo1.maven.org/maven2"
                                   "clojars" "https://repo.clojars.org"})

(xml/alias-uri 'pom "http://maven.apache.org/POM/4.0.0")

(defn- licenses-from-pair
  "Attempts to determine the license(s) (a map) from a POM license name/URL
  pair. Returns nil if no matches were found."
  [{:keys [name url]}]
  ; 1. Look in the name field(s)
  (if-let [name-expressions (lciei/prepend-source "<licenses><license><name>" (lcmtch/name->expressions-info name))]
    name-expressions
    ; 2. If the names didn't give us any licenses, look in the url field(s) (this tends to be slower and less accurate)
    (when-let [uri-expressions (lciei/prepend-source "<licenses><license><url>" (lcmtch/uri->expressions-info url))]
      uri-expressions)))

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

(defn ga->metadata-uri
  "Returns a java.net.URI pointing to the maven-metadata.xml for the given GA,
  or nil if one cannot be found.  The returned URI is guaranteed to be
  resolvable - either to a file that exists in the local Maven cache, or to an
  HTTP-accessible resource on a remote Maven repository (i.e. Maven Central or
  Clojars) that resolves."
  ([{:keys [group-id artifact-id]}] (ga->metadata-uri group-id artifact-id))
  ([group-id artifact-id]
   (when (and (not (s/blank? group-id))
              (not (s/blank? artifact-id)))
     (let [ga-path              (str (s/replace group-id "." "/") "/" artifact-id)
           local-metadata-paths (map #(str ga-path "/maven-metadata-" % ".xml") (keys remote-maven-repos))]
       (if-let [local-metadata-file (first (filter #(and (.exists ^java.io.File %) (.isFile ^java.io.File %))
                                                   (map #(io/file (str @local-maven-repo-d "/" %)) (map #(s/replace % "/" separator) local-metadata-paths))))]
         (.toURI ^java.io.File local-metadata-file)
         (when-let [remote-uri (first (filter lcihttp/uri-resolves? (map #(str % "/" ga-path "/maven-metadata.xml") (vals remote-maven-repos))))]
           (java.net.URI. remote-uri)))))))

(defn ga-latest-version
  "Determines the latest version of the given GA as a String, or nil if a
  version cannot be determined."
  [group-id artifact-id]
  (when-let [metadata-uri (ga->metadata-uri group-id artifact-id)]
    (with-open [metadata-is (io/input-stream metadata-uri)]
      (let [metadata-xml (xml/parse metadata-is)]
        (if-let [latest-version (xml-find-first-string metadata-xml [:metadata :versioning :latest])]
          latest-version
          (last (xi/find-all metadata-xml [:metadata :versioning :versions :version])))))))

(defn gav->pom-uri
  "Returns a java.net.URI pointing to the POM for the given GAV, or nil
  if one cannot be found.  The returned URI is guaranteed to be resolvable -
  either to a file that exists in the local Maven cache, or to an HTTP-
  accessible resource on a remote Maven repository (i.e. Maven Central or
  Clojars) that resolves."
  ([{:keys [group-id artifact-id version]}] (gav->pom-uri group-id artifact-id version))
  ([group-id artifact-id]                   (gav->pom-uri group-id artifact-id nil))
  ([group-id artifact-id version]
   (when (and (not (s/blank? group-id))
              (not (s/blank? artifact-id)))
     (let [version   (or version (ga-latest-version group-id artifact-id))
           gav-path  (str (s/replace group-id "." "/") "/" artifact-id "/" version "/" artifact-id "-" version ".pom")
           local-pom (io/file (str @local-maven-repo-d separator (s/replace gav-path "/" separator)))]
       (if (and (.exists local-pom)
                (.isFile local-pom))
         (.toURI local-pom)
         (when-let [remote-uri (first (filter lcihttp/uri-resolves? (map #(str % "/" gav-path) (vals remote-maven-repos))))]
           (java.net.URI. remote-uri)))))))

(defmulti pom->expressions-info
  "Returns an expressions-info map for the given POM file (an InputStream or
  something that can have an io/input-stream opened on it), or nil if no
  expressions were found.

  If an InputStream is provided, it is the caller's responsibility to open and
  close it, and a filepath associated with the InputStream *must* be provided as
  the second parameter (it is optional for other types of input).

  Note: throws on XML parsing error"
  {:arglists '([pom] [pom filepath])}
  (fn [& args] (type (first args))))

; Note: a few rare pom.xml files are missing the xmlns declation (e.g. software.amazon.ion/ion-java) - so we look for both namespaced and non-namespaced versions of all tags
(defmethod pom->expressions-info java.io.InputStream
  [pom-is filepath]
  (try
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
                              ; License block doesn't exist, so attempt to lookup the parent pom and try again with it
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
                                  (pom->expressions-info (gav->pom-uri parent-gav)))))))   ; Note: naive (stack consuming) recursion, which is fine here as pom hierarchies are rarely very deep
  (catch javax.xml.stream.XMLStreamException xse
    (throw (javax.xml.stream.XMLStreamException. (str "XML error parsing " filepath) xse)))))

(defmethod pom->expressions-info :default
  ([pom] (pom->expressions-info pom (lciu/filepath pom)))
  ([pom filepath]
   (when pom
     (with-open [pom-is (io/input-stream pom)]
       (if-let [expressions (pom->expressions-info pom-is filepath)]
         expressions
         (log/info (str "'" filepath "'") "contains no license information"))))))

(defn pom->expressions
  "Returns a set of SPDX expressions (Strings) for the given POM file (an
  InputStream or something that can have an io/input-stream opened on it), or
  nil if no expressions were found.

  If an InputStream is provided, it is the caller's responsibility to open and
  close it, and a filepath associated with the InputStream *must* be provided as
  the second parameter (it is optional for other types of input)."
  ([pom] (pom->expressions pom (lciu/filepath pom)))
  ([pom filepath]
   (some-> (pom->expressions-info pom filepath)
           keys
           set)))

(defn gav->expressions-info
  "Returns an expressions-info map for the given Maven GA (group-id,
  artifact-id) and optionally V (version).

  If version is not provided, the latest version is looked up (which involves
  file and potentially also network I/O)."
  ([group-id artifact-id] (gav->expressions-info group-id artifact-id nil))
  ([group-id artifact-id version]
   (when-let [version (or version (ga-latest-version group-id artifact-id))]
     (when-let [pom-uri (gav->pom-uri group-id artifact-id version)]
       (with-open [pom-is (io/input-stream pom-uri)]
         (pom->expressions-info pom-is (str pom-uri)))))))

(defn gav->expressions
  "Returns a set of SPDX expressions (Strings) for the given Maven GA (group-id,
  artifact-id) and optionally V (version).

  If version is not provided, the latest version is looked up (which involves
  file and potentially also network I/O)."
  ([group-id artifact-id] (gav->expressions group-id artifact-id nil))
  ([group-id artifact-id version]
   (some-> (gav->expressions-info group-id artifact-id version)
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
