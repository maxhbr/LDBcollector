<?php // -*- mode: html -*-

$contextfile = dirname (__FILE__) . "/../../data/context.json";
$pagename = basename ($argv[1], ".json");
$data = json_decode (file_get_contents ($argv[1]), true);
$context = json_decode (file_get_contents ($contextfile), true);

$logos = array ();
if (array_key_exists ("foaf:logo", $data))
{
    $logos = (is_array ($data["foaf:logo"]) ?
              $data["foaf:logo"] :
              array ( $data["foaf:logo"] ));
}

function render_linked_property ($name) {
    global $data, $context;

    if (!isset ($data[$name]))
        return;

    $ret = "";
    if (is_array ($data[$name]))
    {
       foreach ($data[$name] as $value) {
           $ret .= render_linked_property_entry ($name, $value);
       }
    }
    else
    {
       $ret .= render_linked_property_entry ($name, $data[$name]);
    }

    return $ret;
}

function render_linked_property_entry ($name, $value) {
    global $data, $context;

    $display = "";
    $domain = "";
    $propurl = "";
    $url_prefix = "";

    list ($prefix, $propname) = explode (':', $name);

    if (strpos ($value, ':') !== False)
    {
        list ($url_prefix, $url_name) = explode (':', $value);
    }

    if ($url_prefix and isset ($context["@context"][$url_prefix]))
    {
        $display = $url_name;
        $propurl = $context["@context"][$url_prefix];
        $value = $propurl . $url_name;
    }
    else
    {
        $propurl = $context["@context"][$prefix];
        $host = parse_url ($value, PHP_URL_HOST);
        $path = parse_url ($value, PHP_URL_PATH);
        if (empty ($path) or $path == "/") {
            $display = $host;
        }
        else
        {
            $parts = explode ("/", $value);
            $display = array_pop ($parts);
            if ($prefix === "spdx")
            {
                $value = "http://spdx.org/licenses/$value";
            }

            if (!empty ($host) && $host !== "licensedb.org")
            {
                $domain = " ($host)";
            }
        }
    }

    return "<li>" .
        "<span class=\"prefix\">$prefix:</span>$propname: " .
        "<a property=\"$propurl$propname\" " .
        "href=\"$value\">$display</a>$domain</li>";
}

function render_literal_property ($name) {
    global $data, $context;

    if (!isset ($data[$name]))
        return;

    list ($prefix, $propname) = explode (':', $name);

    return "<li>" .
        "<span class=\"prefix\">$prefix:</span>$propname: " .
        "<span property=\"$name\">${data['li:id']}</span></li>";
}

function add_section (&$sections, $data)
{
    if (empty ($data))
      return;

    array_push ($sections, $data);
}

function sidebar ()
{
    global $logos;

    if (!empty ($logos)) {
        echo '<div class="logo">';
        $count = 0;
        foreach ($logos as $url)
        {
            $count++;
            echo "<a class=\"logo$count\" property=\"foaf:logo\" ";
            if ($count > 1) { echo 'style="display: none"'; }
            echo "href=\"$url\"><img src=\"$url\" /></a>\n";
        }
        echo '</div><hr />';
    }

    $sections = array ();

    echo "<ul>\n";

    add_section ($sections,
                 render_literal_property ("li:id").
                 render_linked_property ("li:earlierVersion").
                 render_linked_property ("li:laterVersion"));

    add_section ($sections,
                 render_literal_property ("dc:title").
                 render_literal_property ("dc:identifier").
                 render_literal_property ("dc:hasVersion").
                 render_linked_property ("dc:creator"));

    $count = 0;
    $logodata = "";
    foreach ($logos as $url) {
        $count++;
        $logodata .= "<li><span class=\"prefix\">foaf:</span>".
            "logo: <button class=\"selected logo$count\">" .
            basename($url, ".png") . "</button></li>";
    };

    add_section ($sections, $logodata);

    add_section ($sections,
                 render_linked_property ("li:plaintext").
                 render_linked_property ("cc:legalcode"));

    add_section ($sections, render_linked_property ("cc:permits"));
    add_section ($sections, render_linked_property ("cc:requires"));
    add_section ($sections, render_linked_property ("cc:prohibits"));
    add_section ($sections, render_linked_property ("spdx:licenseId"));

    echo join ("<hr />", $sections);

    echo "</ul>\n";
}


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
    <title>GNU General Public License</title>
    <script type="text/javascript" src="jquery-1.7.1.min.js"></script>
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

      div.column1 { float: left; width: 60%; min-width: 30em; max-width: 52em; }
      div.column2 { float: left; width: 30%; min-width: 20em; max-width: 30em; }

      div.footer,
      div.main,
      div.sidebar {
          background: #ddd;
          padding: 1em;
          margin: 2em;
          border: 4px solid #fff;
          box-shadow: 0 1px 16px #888;
      }

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
          <span property="dc:title">GNU General Public License</span><br />
          <small>version <span property="dc:hasVersion">3.0</span></small>
        </h1>

        <div rel="https://licensedb.org/ns#notice">

          <div class="notice-properties" style="float:right; margin-top: 0.5em;">
            <input id="orlater" type="checkbox" checked="checked" />
            <span class="prefix">li:</span>orlater
            <span style="display: none;" property="https://licensedb.org/ns#orlater"
                  datatype="http://www.w3.org/2001/XMLSchema-datatypes#boolean">true</span>

            <input id="orlater" type="checkbox" checked="checked" />
            <span class="prefix">li:</span>short
            <span style="display: none;" property="https://licensedb.org/ns#short"
                  datatype="http://www.w3.org/2001/XMLSchema-datatypes#boolean">true</span>
          </div>

          <h3><span class="prefix">li:</span>notice</h3>
          <pre property="https://licensedb.org/ns#text">License GPLv3+: GNU GPL version 3 or later &lt;http://gnu.org/licenses/gpl.html&gt;
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.
</pre>
        </div>

        <div rel="https://licensedb.org/ns#notice">

          <div class="notice-properties" style="float:right; margin-top: 0.5em;">
            <input id="orlater" type="checkbox" checked="checked" />
            <span class="prefix">li:</span>orlater
            <span style="display: none;" property="https://licensedb.org/ns#orlater"
                  datatype="http://www.w3.org/2001/XMLSchema-datatypes#boolean">true</span>

            <input id="orlater" type="checkbox" />
            <span class="prefix">li:</span>short
            <span style="display: none;" property="https://licensedb.org/ns#short"
                  datatype="http://www.w3.org/2001/XMLSchema-datatypes#boolean">false</span>
          </div>

          <h3><span class="prefix">li:</span>notice</h3>
          <pre property="https://licensedb.org/ns#text">This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see &lt;http://www.gnu.org/licenses/&gt;.
</pre>
        </div>

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
        <?php sidebar () ?>
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

  </body>
</html>
