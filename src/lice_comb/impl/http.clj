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
            [hato.client                   :as hc]
            [lice-comb.impl.utils          :as lcu]))

(def ^:private http-client-d (delay (hc/build-http-client {:connect-timeout 1000
                                                           :redirect-policy :always
                                                           :cookie-policy   :none})))

(defn uri-resolves?
  "Does the given URI resolve (i.e. does the resource it points to exist)?

  Note: does not throw - returns false on errors."
  [uri]
  (when (lcu/valid-http-uri? (str uri))
    (try
      (when-let [response (hc/head (str uri)
                                   {:http-client @http-client-d
                                    :header      {"user agent" "com.github.pmonks/lice-comb"}})]
        (= 200 (:status response)))
      (catch Exception _
        false))))

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
  (when (lcu/valid-http-uri? uri)
    (try
      (when-let [response (hc/get (cdn-uri uri)
                                  {:http-client @http-client-d
                                   :accept      "text/plain;q=1,*/*;q=0"  ; Kindly request that the server only return text/plain... ...even though this gets ignored a lot of the time 🙄
                                   :header      {"user agent" "com.github.pmonks/lice-comb"}})]
        (when (= :text/plain (:content-type response))
          (:body response)))
      (catch Exception _
        nil))))

(defn init!
  "Initialises this namespace upon first call (and does nothing on subsequent
  calls), returning nil. Consumers of this namespace are not required to call
  this fn, as initialisation will occur implicitly anyway; it is provided to
  allow explicit control of the cost of initialisation to callers who need it."
  []
  @http-client-d
  nil)
