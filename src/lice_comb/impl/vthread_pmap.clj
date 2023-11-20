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

(in-ns 'lice-comb.impl.utils)

(defn- lice-comb-virtual-thread-factory
  "A lice-comb specific virtual thread factory."
  []
  (-> (Thread/ofVirtual)
      (.name "lice-comb-pmap*-vthread-" 0)
      (.factory)))

(defn pmap*
  "Efficient version of pmap which avoids the overhead of lazy-seq, and uses
  JDK 21+ virtual threads."
  [f coll]
  (let [executor (java.util.concurrent.Executors/newThreadPerTaskExecutor (lice-comb-virtual-thread-factory))
        futures  (mapv #(.submit executor (reify java.util.concurrent.Callable (call [_] (f %)))) coll)
        ret      (mapv #(.get ^java.util.concurrent.Future %) futures)]
    (.shutdownNow executor)
    ret))
