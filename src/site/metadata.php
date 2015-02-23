<?php

/* A quick guess of the relative image size by picking the final integer
   in the url.  Sufficient to sort FSF and CC license logos on size. */
function guess_logo_size ($url)
{
    $matches = NULL;
    if (preg_match ("/.*[^0-9]([0-9]+)[^0-9]*$/", $url, $matches))
    {
        return $matches[1];
    }

    return 0;
}

function cmp_logos ($a, $b)
{
    return guess_logo_size ($a) < guess_logo_size ($b);
}

function get_logos ($data)
{
    $logos = array ();
    if (array_key_exists ("foaf:logo", $data))
    {
        $logos = (is_array ($data["foaf:logo"]) ?
                  $data["foaf:logo"] :
                  array ( $data["foaf:logo"] ));
    }

    /* Sort larger images first. */
    usort ($logos, 'cmp_logos');

    return $logos;
}

function render_linked_property ($name, $data, $context)
{
    if (!isset ($data[$name]))
        return;

    $ret = "";
    if (is_array ($data[$name]))
    {
       foreach ($data[$name] as $value) {
           $ret .= render_linked_property_entry ($name, $value, $data, $context);
       }
    }
    else
    {
        $ret .= render_linked_property_entry ($name, $data[$name], $data, $context);
    }

    return $ret;
}

function render_linked_property_entry ($name, $value, $data, $context)
{
    if (is_array ($value))
    {
        $ret = "";
        foreach ($value as $v) {
            $ret .= render_linked_property_entry ($name, $v, $data, $context);
        }

        return $ret;
    }

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
            if (empty ($display))
            {
                $display = array_pop ($parts);
            }

            if ($prefix === "li" && $propname === "id")
            {
                $value = "https://licensedb.org/id/$value";
            }
        }
    }

    return "<li>" .
        "<span class=\"prefix\">$prefix:</span>$propname: " .
        "<a href=\"$value\">$display</a>$domain</li>\n";
}

function get_single_english_literal ($name, $data, $context)
{
    if (!isset($data[$name])) {
        return false;
    }

    $value = $data[$name];
    if (!is_array ($value)) {
        return $value;
    }

    if (isset ($value["@literal"])) {
        return $value["@literal"];
    }

    if (isset ($value["@value"])) {
        return $value["@value"];
    }

    foreach ($value as $literal) {
        if (!is_array ($literal)) {
            return $literal;
        }
    }

    // FIXME: don't just grab whichever one looks good enough, but score them and
    // return the best match

    foreach ($value as $literal) {
        if (!isset ($literal["@language"])) {
            return $literal["@value"];
        } else if (substr($literal["@language"], 0, 2) == "en") {
            // just grab the first english value
            return $literal["@value"];
        }
    }

    $value = array_shift ($value);
    return $value["@value"];
}


function get_single_literal_value ($name, $data, $context)
{
    /* A literal in JSON-LD may be just a string, or an object with
       @literal and @language keys.  And a particular property may
       have multiple values, which are expressed in JSON-LD as a list
       (or as an array in PHP).

       The code below deals with all these cases, and picks one
       of the values instead of displaying all.
    */

    if (!isset($data[$name])) {
        return false;
    }

    $value = $data[$name];
    if (!is_array ($value))
        return $value;

    if (isset ($value["@literal"]))
    {
        return $value["@literal"];
    }

    if (isset ($value["@value"]))
    {
        return $value["@value"];
    }

    foreach ($value as $literal)
    {
        if (!is_array ($literal))
        {
            return $literal;
        }
    }

    $value = array_shift ($value);
    if (isset ($value["@literal"]))
    {
        return $value["@literal"];
    }

    return $value["@value"];
}

function render_literal_property ($name, $data, $context)
{
    if (!isset ($data[$name]))
        return False;

    list ($prefix, $propname) = explode (':', $name);

    $value = get_single_literal_value ($name, $data, $context);

    return "<li>" .
        "<span class=\"prefix\">$prefix:</span>$propname: " .
        "<span property=\"$name\">$value</span></li>";
}

function add_section (&$sections, $data)
{
    if (empty ($data))
      return;

    array_push ($sections, $data);
}

function plaintext_fallback () {


    return "<p class=\"plaintext\">No plain text version available, please see the links in the sidebar" .
        " for the full license text</p>";
}

function plaintext ($data)
{
    if (!isset($data['li:plaintext'])) {
        return plaintext_fallback ();
    }

    $url = is_array($data['li:plaintext']) ? $data['li:plaintext'][0] : $data['li:plaintext'];

    return "<iframe class=\"plaintext\" src=\"{$url}\"></iframe>";
}

function sidebar ($data, $context, $logos)
{
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
                 render_linked_property ("li:id", $data, $context).
                 render_literal_property ("li:name", $data, $context));

    add_section ($sections,
                 render_literal_property ("dc:title", $data, $context).
                 render_literal_property ("dc:identifier", $data, $context).
                 render_literal_property ("dc:hasVersion", $data, $context).
                 render_linked_property ("dc:creator", $data, $context));

    $count = 0;
    $logodata = "";
    foreach ($logos as $url) {
        $count++;
        $logodata .= "<li><span class=\"prefix\">foaf:</span>".
            "logo: <button class=\"logo$count\">" .
            basename($url, ".png") . "</button></li>";
    };

    add_section ($sections, $logodata);

    add_section ($sections,
                 render_linked_property ("li:plaintext", $data, $context).
                 render_linked_property ("cc:legalcode", $data, $context));

    add_section ($sections, render_linked_property ("li:libre", $data, $context));

    add_section ($sections, render_linked_property ("cc:permits", $data, $context));
    add_section ($sections, render_linked_property ("cc:requires", $data, $context));
    add_section ($sections, render_linked_property ("cc:prohibits", $data, $context));

    add_section ($sections,
                 render_linked_property ("dc:isVersionOf", $data, $context).
                 render_linked_property ("dc:replaces", $data, $context).
                 render_linked_property ("dc:isReplacedBy", $data, $context));

    add_section ($sections,
                 render_linked_property ("spdx:licenseId", $data, $context));

    echo join ("<hr />", $sections);

    echo "</ul>\n";
}

function render_notice_property ($notice, $property)
{
    $checked = "";
    $bool = "false";

    if ($notice["li:$property"]["@value"])
    {
        $checked = 'checked="checked" ';
        $bool = "true";
    }

    return "<input id=\"$property\" type=\"checkbox\" $checked " .
        'disabled="disabled" /><span class="prefix">li:</span>' .
        "$property<span style=\"display: none;\" " .
        "property=\"https://licensedb.org/ns#$property\"" .
        "datatype=\"http://www.w3.org/2001/XMLSchema-datatypes#boolean\">" .
        "$bool</span>";
}

function render_notice ($notice)
{
    return '<div rel="https://licensedb.org/ns#notice">' .
        '<div class="notice-properties">' .
        render_notice_property ($notice, "canonical") .
        render_notice_property ($notice, "orlater") .
        render_notice_property ($notice, "short") .
        '</div>'.
        '<h3><span class="prefix">li:</span>notice</h3>'.
        '<pre property="https://licensedb.org/ns#text">'.
        htmlentities($notice["li:text"]).'</pre></div>';
}

function cmp_notice ($a, $b)
{
    if ($a["li:canonical"] and !$b["li:canonical"])
        return -1;

    if (!$a["li:canonical"] and $b["li:canonical"])
        return 1;

    if ($a["li:orlater"] and !$b["li:orlater"])
        return -1;

    if (!$a["li:orlater"] and $b["li:orlater"])
        return 1;

    if ($a["li:short"] and !$b["li:short"])
        return -1;

    if (!$a["li:short"] and $b["li:short"])
        return 1;

    return 0;
}

function notices ($data, $context)
{
    if (!isset ($data["li:notice"]))
        return "";

    if (isset ($data["li:notice"]) and
        isset ($data["li:notice"]["li:text"]))
    {
        return render_notice ($data["li:notice"]);
    }

    $notices = $data["li:notice"];
    usort ($notices, "cmp_notice");

    $ret = "";
    foreach ($notices as $notice)
    {
        $ret .= render_notice ($notice);
    }

    return $ret;
}

