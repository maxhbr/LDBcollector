<?php // -*- mode: web -*-

$lines = file ($argv[1]);
$wwwroot = $argv[2];
$title = array_shift ($lines);
$content = join ("", $lines);

// if this is the vocab page, embed the vocabulary.
if ($argv[1] === "src/site/ns.html") {
    $ns_jsonld = json_decode (file_get_contents ("www/ns.jsonld"), true);
    $embedded_vocab = "<script type=\"application/ld+json\">\n"
        . json_encode($ns_jsonld, JSON_HEX_TAG | JSON_HEX_AMP | JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES) . "\n"
        . "\n</script>\n";
} else {
    $embedded_vocab = "";
}

?><!DOCTYPE html>
<html lang="en-US">
  <head>
    <meta charset="utf-8" />
    <title><?=$title ?></title>
    <link rel="stylesheet" href="<?=$wwwroot ?>licensedb.css" type="text/css">
    <?php echo $embedded_vocab; ?>
  </head>

  <body>
    <div id="header">
      <a href="http://licensedb.org/" title="home">
        <img src="https://licensedb.org/licensedb.png" style="margin: 1em;" />
      </a>
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
        &copy; 2015 <a href="https://frob.nl">Kuno Woudt</a>, software licensed
        under <a rel="license" href="http://www.apache.org/licenses/LICENSE-2.0.html">Apache
        2.0</a>, database available under <a rel="license"
        href="http://creativecommons.org/publicdomain/zero/1.0/">CC0</a>.
        See <a href="https://licensedb.org/license">the license page</a> for more details.
      </p>
    </div>

  </body>
</html>
