<?php

$content = file_get_contents ($argv[1])

?><!DOCTYPE html PUBLIC "-//W3C//DTD XHTML+RDFa 1.0//EN"
"http://www.w3.org/MarkUp/DTD/xhtml-rdfa-1.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" 
      xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
      xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
      xmlns:cc="http://creativecommons.org/ns#"
      xmlns:spdx="http://spdx.org/rdf/terms#"
      xmlns:li="https://licensedb.org/ns/#"
      xml:lang="en-US" lang="en-US">

  <head profile="http://www.w3.org/1999/xhtml/vocab">
    <meta http-equiv="Content-type" content="text/html; charset=utf-8" />
    <title>License Database vocabulary</title>
    <style>
      html, body, div, span, h1, h2, h3, h4, h5, h6, p, blockquote,
      pre, a, abbr, acronym, address, big, cite, code, del, dfn, em,
      img, ins, q, samp, small, strike, strong, sub, sup, tt, var, dl,
      dt, dd, ol, ul, li, fieldset, form, label, legend, table,
      caption, tbody, tfoot, thead, tr, th, td {
        margin: 0; padding: 0; border: 0; outline: 0; text-decoration: none;
        vertical-align: baseline; background: transparent; color: black;
      }
      ol, ul { list-style: none; }
      blockquote, q { quotes: none; }
      blockquote:before, blockquote:after, q:before, q:after { content: ''; content: none; }
      table { border-collapse: collapse; border-spacing: 0; }
      ins { text-decoration: none; }
      del { text-decoration: line-through; }

      html { font-size: 100%; -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; }
      body { color: #333; background: #fff; }
      body, p {
        font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
        font-size: 13px; line-height: 18px;
      }

      p { margin-bottom: 9px; }

      h1, h2, h3, h4, h5, h6 { font-weight: bold; text-rendering: optimizelegibility; }
      h1 { font-size: 30px; line-height: 36px; margin: 36px 0; }
      h2 { font-size: 24px; line-height: 36px; margin: 36px 0; }
      h3 { font-size: 18px; line-height: 27px; margin: 18px 0; }
      h4 { font-size: 14px; line-height: 18px; margin: 18px 0 0 0; }
      h5 { font-size: 12px; line-height: 18px; }
      h6 { font-size: 11px; line-height: 18px; text-transform: uppercase; }

      #header {
          width: 100%;
          border-bottom: 2px solid #222;
          background-image: linear-gradient(top, #004EAD 0%, #0068E8 54%);
          background-image: -o-linear-gradient(top, #004EAD 0%, #0068E8 54%);
          background-image: -moz-linear-gradient(top, #004EAD 0%, #0068E8 54%);
          background-image: -webkit-linear-gradient(top, #004EAD 0%, #0068E8 54%);
          background-image: -ms-linear-gradient(top, #004EAD 0%, #0068E8 54%);
          background-image: -webkit-gradient(linear, left top, left bottom,
                            color-stop(0, #004EAD), color-stop(0.54, #0068E8));
      }

      #menu { font-size: 18px; line-height: 27px; float: right; margin: 27px 18px 0 0; }
      #menu ul li { display: inline-block; margin: 18px; }
      #menu ul li a, #menu ul li a:visited { color: #fff; }

      #content { width: 42em; padding-left: 108px; }

      #footer { width: 100%; margin-top: 36px; padding: 6px 0 36px 0; border-top: 2px solid #222; }
      #footer p { margin-left: 108px; width: 42em; }
      #footer p.indent { padding-left: 2em; }

      h1, h2, h3, h4, h5, h6, p, span { color: #333; }
      span.prefix { color: #999;    }
      a {           color: #004ead; }
      a:visited {   color: #002757; }

      #footer { background: #555; }
      #footer p, #footer span, #footer a, #footer a:visited  { color: #eee; }
    </style>
  </head>

  <body>
    <div id="header">
      <a href="http://licensedb.org/" title="home"><img src="licensedb.png" style="margin: 1em;" /></a>
      <div id="menu">
        <ul>
          <li><a href="https://licensedb.org/about/">About</a></li>
          <li><a href="https://gitorious.org/licensedb/licensedb/">Download</a></li>
          <li><a href="https://licensedb.org/ns/">Vocabulary</a></li>
        </ul>
      </div>
    </div>

    <div id="content"><?php echo $content ?></div>

    <script type="text/javascript" language="JavaScript">
      function license_info () {
        var l = document.getElementById("license");
        l.style.display = 'block';
        l.scrollIntoView ();
      }
    </script>
    <div id="footer">
      <p class="copyright">
        &copy; 2012 <a href="https://frob.nl">Kuno Woudt</a>,
        <a rel="license" href="http://www.apache.org/licenses/LICENSE-2.0.html">Apache 2.0</a>
        <button onclick="license_info(); return false;">More information</button>
      </p>
      <div id="license" style="display: none;">
        <p>
          Licensed under the Apache License, Version 2.0 (the
          "License"); you may not use this file except in compliance
          with the License.  You may obtain a copy of the License at
        </p>
        <p class="indent">
          <a href="http://www.apache.org/licenses/LICENSE-2.0"
             >http://www.apache.org/licenses/LICENSE-2.0</a>
        </p>
        <p>
          Unless required by applicable law or agreed to in writing,
          software distributed under the License is distributed on an
          "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
          either express or implied.  See the License for the specific
          language governing permissions and limitations under the
          License.
        </p>
      </div>
    </div>

  </body>
</html>
