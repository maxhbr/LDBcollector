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

(ns lice-comb.impl.http
  "HTTP helper functionality. Note: this namespace is not part of
  the public API of lice-comb and may change without notice."
  (:require [clojure.string                :as s]
            [clojure.java.io               :as io]
            [clojure.java.shell            :as sh]
            [hato.client                   :as hc]
            [lice-comb.impl.utils          :as lciu]))

(def ^:private http-client-d (delay (hc/build-http-client {:connect-timeout 1000
                                                           :redirect-policy :always
                                                           :cookie-policy   :none})))

(defn uri-resolves?
  "Does the given URI resolve (i.e. does the resource it points to exist)?

  Note: does not throw - returns false on errors."
  [uri]
  (boolean
    (when (lciu/valid-http-uri? (str uri))
      (try
        (when-let [response (hc/head (str uri)
                                     {:http-client @http-client-d
                                      :header      {"user agent" "com.github.pmonks/lice-comb"}})]
          (= 200 (:status response)))
        (catch Exception _
          false)))))

(defn- cdn-uri
  "Converts raw URIs into CDN URIs, for these 'known' hosts:

  * github.com e.g. https://github.com/pmonks/lice-comb/blob/main/LICENSE -> https://raw.githubusercontent.com/pmonks/lice-comb/main/LICENSE

  If the given URI is not known, returns the input unchanged."
  [uri]
  (if-let [^java.net.URL uri-obj (try (io/as-url uri) (catch Exception _ nil))]
    (case (s/lower-case (.getHost uri-obj))
      "github.com" (-> uri
                       (s/replace #"(?i)github\.com" "raw.githubusercontent.com")
                       (s/replace "/blob/"          "/"))
      uri)  ; Default case
    uri))

(defn get-text
  "Attempts to get plain text as a String from the given URI, returning nil if
  unable to do so (including for error conditions - there is no way to
  disambiguate errors from non-text content, for example)."
  [uri]
  (when (lciu/valid-http-uri? uri)
    (try
      (when-let [response (hc/get (cdn-uri uri)
                                  {:http-client @http-client-d
                                   :accept      "text/plain;q=1,*/*;q=0"  ; Kindly request that the server only return text/plain... ...even though this gets ignored a lot of the time 🙄
                                   :header      {"user agent" "com.github.pmonks/lice-comb"}})]
        (when (= :text/plain (:content-type response))
          (:body response)))
      (catch Exception _
        nil))))

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

(defn gav->pom-uri
  "Returns a java.net.URI pointing to the POM for the given GAV (a map), or nil
  if one cannot be found.  The returned URI is guaranteed to be resolvable -
  either to a file that exists in the local Maven cache, or to an HTTP-
  accessible resource on a remote Maven repository (i.e. Maven Central or
  Clojars) that resolves."
  ([{:keys [group-id artifact-id version]}] (gav->pom-uri group-id artifact-id version))
  ([group-id artifact-id version]
   (when (and (not (s/blank? group-id))
              (not (s/blank? artifact-id))
              (not (s/blank? version)))
     (let [gav-path  (str (s/replace group-id "." "/") "/" artifact-id "/" version "/" artifact-id "-" version ".pom")
           local-pom (io/file (str @local-maven-repo-d "/" gav-path))]
       (if (and (.exists local-pom)
                (.isFile local-pom))
         (.toURI local-pom)
         (when-let [remote-uri (first (filter uri-resolves? (map #(str % "/" gav-path) remote-maven-repos)))]
           (java.net.URI. remote-uri)))))))

(defn init!
  "Initialises this namespace upon first call (and does nothing on subsequent
  calls), returning nil. Consumers of this namespace are not required to call
  this fn, as initialisation will occur implicitly anyway; it is provided to
  allow explicit control of the cost of initialisation to callers who need it."
  []
  @http-client-d
  @local-maven-repo-d
  nil)
