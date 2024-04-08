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
  "Functionality related to combing Maven POMs for license information.

  In this namespace abbreviations are used for Maven's groupId, artifactId, and
  version concepts.  So for example:
  * `GA` means groupId & artifactId
  * `GAV` means groupId, artifactId & version
  
  In function calls where a version isn't required or provided, the library will
  determine and use the latest available version, as determined from (in order):
  1. your local Maven cache (usually ~/.m2/repository)
  2. Maven Central
  3. Clojars
  
  Other/custom Maven artifact repositories are not currently supported."
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

(def default-local-maven-repo
  "A String containing a file path for the default local Maven artifact
  cache that the library uses.  Attempts to use this Maven client command to
  determine this value:

    mvn help:evaluate -Dexpression=settings.localRepository -q -DforceStdout

  but falls back on a \"best guess\" if the Maven client isn't installed or
  cannot be executed."
  (try
    ; The command:
    ;     mvn help:evaluate -Dexpression=settings.localRepository -q -DforceStdout
    ; determines where the local repository is located.
    (let [sh-result (sh/sh "mvn" "help:evaluate" "-Dexpression=settings.localRepository" "-q" "-DforceStdout")]
      (if (zero? (:exit sh-result))
        (s/trim (:out sh-result))
        (str (System/getProperty "user.home") (str separator ".m2" separator "repository"))))
    (catch java.io.IOException _
      (str (System/getProperty "user.home") (str separator ".m2" separator "repository")))))

(def ^:private local-maven-repo-a (atom default-local-maven-repo))

(defn local-maven-repo
  "The current local Maven repo in use, as a String containing a file path."
  []
  @local-maven-repo-a)

(defn set-local-maven-repo!
  "Sets the local Maven repo to use from this point onward. The argument is a
  String containing a file path that must be a readable directory that exists
  (throws ex-info if these conditions are not met)."
  [dir]
  (let [d (io/file dir)]
    (if (and (.exists      d)
             (.isDirectory d)
             (.canRead     d))
      (swap! local-maven-repo-a (constantly dir))
      (throw (ex-info (str dir " either does not exist, is not a directory, or is not readable.") {}))))
  nil)

(def default-remote-maven-repos
  "A map containing the default remote Maven artifact repositories that the
  library uses. Each key is a string that's the short identifier of the repo
  (e.g. \"clojars\"), and each value is the base URL of that artifact repository
  (e.g. \"https://repo.clojars.org\")."
  {"central" "https://repo1.maven.org/maven2"
   "clojars" "https://repo.clojars.org"})

(def ^:private remote-maven-repos-a (atom default-remote-maven-repos))

(defn remote-maven-repos
  "The current remote Maven repos in use, as a map in the format described in
  `default-remote-maven-repos`."
  []
  @remote-maven-repos-a)

(defn set-remote-maven-repos!
  "Sets the remote Maven repos to use from this point onward. The argument is a
  map in the format described in `default-remote-maven-repos`.

  For most use cases you should merge `default-remote-maven-repos` with whatever
  additional repos you wish to provide (the rare exceptions being situations
  such as a dev environment that contains a custom Maven artifact repository
  that proxies/caches Maven Central and/or Clojars)."
  [repos]
  (swap! remote-maven-repos-a (constantly repos))
  nil)

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
  HTTP-accessible resource on a remote Maven repository (e.g. Maven Central,
  Clojars) that resolves."
  ([{:keys [group-id artifact-id]}] (ga->metadata-uri group-id artifact-id))
  ([group-id artifact-id]
   (when (and (not (s/blank? group-id))
              (not (s/blank? artifact-id)))
     (let [ga-path              (str (s/replace group-id "." "/") "/" artifact-id)
           local-metadata-paths (map #(str ga-path "/maven-metadata-" % ".xml") (keys @remote-maven-repos-a))]
       (if-let [local-metadata-file (first (filter #(and (.exists ^java.io.File %) (.isFile ^java.io.File %))
                                                   (map #(io/file (str @local-maven-repo-a "/" %)) (map #(s/replace % "/" separator) local-metadata-paths))))]
         (.toURI ^java.io.File local-metadata-file)
         (when-let [remote-uri (first (filter lcihttp/uri-resolves? (map #(str % "/" ga-path "/maven-metadata.xml") (vals @remote-maven-repos-a))))]
           (java.net.URI. remote-uri)))))))

(defn gav->metadata-uri
  "Returns a java.net.URI pointing to the maven-metadata.xml for the given GAV,
  or nil if one cannot be found.  The returned URI is guaranteed to be
  resolvable - either to a file that exists in the local Maven cache, or to an
  HTTP-accessible resource on a remote Maven repository (e.g. Maven Central,
  Clojars) that resolves."
  ([{:keys [group-id artifact-id version]}] (gav->metadata-uri group-id artifact-id version))
  ([group-id artifact-id version]
   (when (and (not (s/blank? group-id))
              (not (s/blank? artifact-id))
              (not (s/blank? version)))
     (let [gav-path             (str (s/replace group-id "." "/") "/" artifact-id "/" version)
           local-metadata-paths (map #(str gav-path "/maven-metadata-" % ".xml") (keys @remote-maven-repos-a))]
       (if-let [local-metadata-file (first (filter #(and (.exists ^java.io.File %) (.isFile ^java.io.File %))
                                                   (map #(io/file (str @local-maven-repo-a "/" %)) (map #(s/replace % "/" separator) local-metadata-paths))))]
         (.toURI ^java.io.File local-metadata-file)
         (when-let [remote-uri (first (filter lcihttp/uri-resolves? (map #(str % "/" gav-path "/maven-metadata.xml") (vals @remote-maven-repos-a))))]
           (java.net.URI. remote-uri)))))))

(defn ga-latest-version
  "Determines the latest version of the given GA as a String, or nil if it
  cannot be determined.

  Note that this could be a SNAPSHOT, RC, or other pre-release version."
  [group-id artifact-id]
  (when-let [metadata-uri (ga->metadata-uri group-id artifact-id)]
    (with-open [metadata-is (io/input-stream metadata-uri)]
      (let [metadata-xml (xml/parse metadata-is)]
        (if-let [latest-version (xml-find-first-string metadata-xml [:metadata :versioning :latest])]
          latest-version
          (last (xi/find-all metadata-xml [:metadata :versioning :versions :version])))))))

(defn ga-release-version
  "Determines the release version (if any) of the given GA as a String, or nil
  if it cannot be determined or the GA doesn't have a released version yet."
  [group-id artifact-id]
  (when-let [metadata-uri (ga->metadata-uri group-id artifact-id)]
    (with-open [metadata-is (io/input-stream metadata-uri)]
      (let [metadata-xml (xml/parse metadata-is)]
        (xml-find-first-string metadata-xml [:metadata :versioning :release])))))

(defn- snapshot-version?
  "Is version a SNAPSHOT?"
  [version]
  (and (not (s/blank? version))
       (s/ends-with? (s/upper-case version) "-SNAPSHOT")))

(defn- resolve-snapshot-version
  "If version is a SNAPSHOT, resolves the version string used in the filenames
  (which is different to the public version string)."
  [group-id artifact-id version]
  (if (snapshot-version? version)
    (when-let [metadata-uri (gav->metadata-uri group-id artifact-id version)]
      (with-open [metadata-is (io/input-stream metadata-uri)]
        (let [metadata-xml (xml/parse metadata-is)
              timestamp    (xml-find-first-string metadata-xml [:metadata :versioning :snapshot :timestamp])
              build-number (xml-find-first-string metadata-xml [:metadata :versioning :snapshot :buildNumber])]
          (str (s/replace version #"(?i)SNAPSHOT" (str timestamp "-" build-number))))))
    version))

(defn- release-version?
  "Is version a RELEASE?"
  [version]
  (and (not (s/blank? version))
       (= (s/upper-case version) "RELEASE")))

(defn gav->pom-uri
  "Returns a java.net.URI pointing to the POM for the given GAV, or nil if one
  cannot be found.  The returned URI is guaranteed to be resolvable - either to
  a file that exists in the local Maven cache, or to an HTTP-accessible resource
  on a remote Maven repository (e.g. Maven Central, Clojars) that resolves.

  If version is not provided, determines the latest version (which may be a
  SNAPSHOT) and uses that."
  ([{:keys [group-id artifact-id version]}] (gav->pom-uri group-id artifact-id version))
  ([group-id artifact-id]                   (gav->pom-uri group-id artifact-id nil))
  ([group-id artifact-id version]
   (when (and (not (s/blank? group-id))
              (not (s/blank? artifact-id)))
     (let [version      (-> (or version (ga-latest-version group-id artifact-id))
                            (s/replace #"(?i)-SNAPSHOT\z" "-SNAPSHOT")  ; Normalise case of SNAPSHOT versions
                            (s/replace #"(?i)\ARELEASE\z" "RELEASE"))   ; Normalise case of RELEASE versions
           version      (if (release-version? version) (ga-release-version group-id artifact-id) version)
           file-version (resolve-snapshot-version group-id artifact-id version)
           gav-path     (str (s/replace group-id "." "/") "/" artifact-id "/" version "/" artifact-id "-" file-version ".pom")
           local-pom (io/file (str @local-maven-repo-a separator (s/replace gav-path "/" separator)))]
       (if (and (.exists local-pom)
                (.isFile local-pom))
         (.toURI local-pom)
         (when-let [remote-uri (first (filter lcihttp/uri-resolves? (map #(str % "/" gav-path) (vals @remote-maven-repos-a))))]
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
  "Returns an expressions-info map for the given GA and (optionally) V.

  If version is not provided, the latest version is looked up (which involves
  file and potentially also network I/O)."
  ([group-id artifact-id] (gav->expressions-info group-id artifact-id nil))
  ([group-id artifact-id version]
   (when-let [version (or version (ga-latest-version group-id artifact-id))]
     (when-let [pom-uri (gav->pom-uri group-id artifact-id version)]
       (with-open [pom-is (io/input-stream pom-uri)]
         (pom->expressions-info pom-is (str pom-uri)))))))

(defn gav->expressions
  "Returns a set of SPDX expressions (Strings) for the given GA and optionally
  V.

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
  @local-maven-repo-a
  nil)
