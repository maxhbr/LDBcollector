<?php // -*- mode: html -*-

require (dirname (__FILE__)."/metadata.php");

$contextfile = dirname (__FILE__) . "/../../data/context.json";
$pagename = basename ($argv[1], ".json");
$data = json_decode (file_get_contents ($argv[1]), true);
$context = json_decode (file_get_contents ($contextfile), true);
$logos = get_logos ($data);
$title = get_single_literal_value ("dc:title", $data, $context);

?><!DOCTYPE html>
<html version="HTML+RDFa 1.1" lang="en" xml:lang="en"
      xmlns="http://www.w3.org/1999/xhtml"
      xmlns:cc="http://creativecommons.org/ns#"
      xmlns:li="https://licensedb.org/ns#"
      xmlns:spdx="http://spdx.org/rdf/terms#"
      xmlns:dc="http://purl.org/dc/terms/"
      xmlns:foaf="http://xmlns.com/foaf/0.1/"
      xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
  <head>
    <meta charset="UTF-8"/>
    <title><?=$title?></title>
    <script type="text/javascript" src="https://licensedb.org/jquery.js"></script>
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
      body { color: #333; background: #ccc; }
      body, p {
        font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
        font-size: 13px; line-height: 18px;
      }

      p { margin-bottom: 9px; }

      h1, h2, h3, h4, h5, h6 { font-weight: bold; text-rendering: optimizelegibility; }
      h1 { font-size: 30px; line-height: 36px; margin: 36px 0; }
      h1 small { font-size: 18px; }
      h2 { font-size: 24px; line-height: 36px; margin: 36px 0; }
      h3 { font-size: 18px; line-height: 27px; margin: 18px 0; }
      h4 { font-size: 14px; line-height: 18px; margin: 18px 0 0 0; }
      h5 { font-size: 12px; line-height: 18px; }
      h6 { font-size: 11px; line-height: 18px; text-transform: uppercase; }

      dt { margin: 1em 0 0 0;  font-weight: bolder; }
      dd { margin: 0.5em 0 0 3em; }

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

      hr { border: 1px solid #eee; }

      div.column1 { float: left; width: 69%; min-width: 30em; max-width: 52em; }
      div.column2 { float: left; width: 30%; min-width: 20em; max-width: 32em; }

      div.footer,
      div.main,
      div.sidebar {
          background: #ddd;
          padding: 1em;
          margin: 2em;
          border: 4px solid #fff;
          box-shadow: 0 1px 16px #888;
      }

      div.notice-properties { float:right; margin-top: 0.5em; }

      pre { font-size: 12px; overflow: auto; }

      div.logo { padding: 1em; text-align: center; }
    </style>
  </head>
  <body>

    <div about="<?php echo $data['@id']; ?>"
          typeof="li:License cc:License">

      <div class="column1">
      <div class="main">
        <h1>
          <a href="<?=$data["@id"]?>">
          <span property="dc:title"><?=$title?></span>
          <?php if (isset ($data["dc:hasVersion"])): ?>
          </a>
          <br />
          <small>version <span property="dc:hasVersion"><?=$data["dc:hasVersion"]?></span></small>
          <?php endif; ?>
        </h1>
        <?php echo notices ($data, $context); ?>
      </div>

      <div class="footer">
        <p>
          You're viewing metadata from <a href="https://licensedb.org">The License Database</a>.
          Get this data as <a href="<?=$pagename?>.json">JSON-LD</a> or
          <a href="<?=$pagename?>.rdf">RDF</a>.
        </p>

        <p>
          To the extent possible under law, the License Database contributors
          have waived all copyright and related or neighboring rights to this work.
          See <a href="https://licensedb.org/license">the license page</a> for more details.
        </p>
      </div>
    </div>

    <div class="column2">
      <div class="sidebar">
        <?php sidebar ($data, $context, $logos) ?>
      </div>
    </div>

    <script>
      $('div.sidebar').find ('button').bind ('click', function (event) {
        $('div.sidebar').find ('a[property="foaf:logo"]').hide ();
        $('div.sidebar').find ('button').removeClass ('selected');
        var logo = $(this).attr ('class');
        $(this).addClass ('selected');
        $('div.sidebar').find ('a.' + logo).show ();
      });
    </script>

    <script type="text/javascript">
      var pkBaseURL = (("https:" == document.location.protocol) ? "https://frob.nl/piwik/" : "http://frob.nl/piwik/");
      document.write(unescape("%3Cscript src='" + pkBaseURL + "piwik.js' type='text/javascript'%3E%3C/script%3E"));
    </script>
    <script type="text/javascript">
      try {
        var piwikTracker = Piwik.getTracker(pkBaseURL + "piwik.php", 4);
        piwikTracker.trackPageView();
        piwikTracker.enableLinkTracking();
      } catch( err ) {}
    </script><noscript><p><img src="https://frob.nl/piwik/piwik.php?idsite=4" style="border:0" alt="" /></p></noscript>

  </body>
</html>
