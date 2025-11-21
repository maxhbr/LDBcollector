;
; Copyright © 2023 Peter Monks
;
; This Source Code Form is subject to the terms of the Mozilla Public
; License, v. 2.0. If a copy of the MPL was not distributed with this
; file, You can obtain one at https://mozilla.org/MPL/2.0/.
;
; SPDX-License-Identifier: MPL-2.0
;

(ns lice-comb.impl.http
  "HTTP helper functionality. Note: this namespace is not part of
  the public API of lice-comb and may change without notice."
  (:require [clojure.string       :as s]
            [clojure.java.io      :as io]
            [hato.client          :as hc]
            [lice-comb.impl.utils :as lciu]))

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
  (if-let [^java.net.URL url-obj (try (io/as-url uri) (catch Exception _ nil))]
    (case (s/lower-case (.getHost url-obj))
      "github.com" (-> uri
                       (s/replace-first #"(?i)github\.com" "raw.githubusercontent.com")
                       (s/replace-first "/blob/"          "/"))
      uri)
    uri))

(defn get-text
  "Attempts to get plain text as a String from the given URI, returning nil if
  unable to do so (including for error conditions - there is no way to
  disambiguate errors from non-text content, for example).

  HTML responses are automatically converted to plain text (using JSoup)."
  [uri]
  (when (lciu/valid-http-uri? uri)
    (try
      (when-let [response (hc/get (cdn-uri uri)
                                  {:http-client @http-client-d
                                   :accept      "text/plain;q=1,text/html;q=0.5,application/xhtml+xml;q=0.5,*/*;q=0"  ; Kindly request that the server give us text/plain... ...though this gets ignored a lot of the time 🙄
                                   :header      {"user agent" "com.github.pmonks/lice-comb"}})]
        (case (:content-type response)
           :text/plain            (:body response)
           :text/html             (lciu/html->text (:body response))
           :application/xhtml+xml (lciu/html->text (:body response))))
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
