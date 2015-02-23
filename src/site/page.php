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

require dirname(__FILE__) . "/layout.php";
