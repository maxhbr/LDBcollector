<?php // -*- mode: html -*-

$lines = file ($argv[1]);
$wwwroot = $argv[2];
$title = array_shift ($lines);
$content = join ("", $lines);

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
    <title><?=$title ?></title>
    <link rel="stylesheet" href="<?=$wwwroot ?>licensedb.css" type="text/css">
    <script type="text/javascript" src="../jquery.js"></script>
  </head>

  <body>
    <div id="header">
      <a href="http://licensedb.org/" title="home"><img src="https://licensedb.org/licensedb.png" style="margin: 1em;" /></a>
      <div id="menu">
        <ul>
          <li><a href="https://licensedb.org/">About</a></li>
          <li><a href="https://licensedb.org/id/">Database</a></li>
          <li><a href="https://licensedb.org/ns">Vocabulary</a></li>
          <li><a href="https://licensedb.org/license">License</a></li>
        </ul>
      </div>
    </div>
    <div id="contentwrapper">
      <div id="content"><?php echo $content ?></div>
    </div>

    <div id="footer">
      <p class="copyright">
        &copy; 2012 <a href="https://frob.nl">Kuno Woudt</a>, software
        licensed under <a rel="license"
        href="http://www.apache.org/licenses/LICENSE-2.0.html" >Apache
        2.0</a>, database available under <a rel="license"
        href="http://creativecommons.org/publicdomain/zero/1.0/"
        >CC0</a>. See <a href="https://licensedb.org/license">the
        license page</a> for more details.
      </p>
    </div>

  </body>
</html>
