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

(ns lice-comb.data
  "Data handling functionality."
  (:require [lice-comb.utils :as u]))

(defn uri-for-data
  [file]
  (when file
    (str (u/getenv "LICE_COMB_DATA_DIR" "https://raw.githubusercontent.com/pmonks/lice-comb/data") file)))
