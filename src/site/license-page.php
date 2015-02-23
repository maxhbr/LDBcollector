<?php // -*- mode: html -*-

require (dirname (__FILE__)."/metadata.php");

$contextfile = dirname (__FILE__) . "/../../data/context.jsonld";
$pagename = basename ($argv[1], ".jsonld");
$data = json_decode (file_get_contents ($argv[1]), true);

$embedded_vocab = "<script type=\"application/ld+json\">\n"
    . json_encode($data, JSON_HEX_TAG | JSON_HEX_AMP | JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES) . "\n"
    . "\n</script>\n";

$context = json_decode (file_get_contents ($contextfile), true);
$logos = get_logos ($data);
$title = get_single_english_literal ("dc:title", $data, $context);

// creative commons is inconsistent about including their name in the dc:title
// FIXME: this should be fixed in src/build/turtle-cc.py
if (substr($pagename, 0, 3) == 'CC-') {
    if (strpos ($title, 'Creative Commons') === false) {
        $title = 'Creative Commons ' . $title;
    }
}

$version = false;
if (isset ($data["dc:hasVersion"])) {
    if (strpos ($title, $data["dc:hasVersion"]) === false) {
        $version = $data["dc:hasVersion"];
    }
}

$wwwroot = "../";

ob_start();

?>
<article class="license-details">
    <h1>
        <a href="<?=$data["@id"]?>">
            <?= $title ?>
        </a>
        <?php if ($version): ?>
            <br />
            <small>version <span><?= $version ?></span></small>
        <?php endif; ?>
    </h1>

    <section class="sidebar">
        <?= sidebar($data, $context, $logos) ?>
    </section>
    <section class="license-body">
        <?= plaintext($data) ?>
    </section>
</article>

<?php

$content = ob_get_contents();
ob_end_clean();

require dirname(__FILE__) . "/layout.php";
