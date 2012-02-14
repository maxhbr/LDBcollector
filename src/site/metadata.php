<?php

function get_logos ($data)
{
    $logos = array ();
    if (array_key_exists ("foaf:logo", $data))
    {
        $logos = (is_array ($data["foaf:logo"]) ?
                  $data["foaf:logo"] :
                  array ( $data["foaf:logo"] ));
    }

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

function render_literal_property ($name, $data, $context)
{
    if (!isset ($data[$name]))
        return;

    list ($prefix, $propname) = explode (':', $name);

    return "<li>" .
        "<span class=\"prefix\">$prefix:</span>$propname: " .
        "<span property=\"$name\">${data[$name]}</span></li>";
}

function add_section (&$sections, $data)
{
    if (empty ($data))
      return;

    array_push ($sections, $data);
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
                 render_literal_property ("li:id", $data, $context).
                 render_linked_property ("li:earlierVersion", $data, $context).
                 render_linked_property ("li:laterVersion", $data, $context));

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
            "logo: <button class=\"selected logo$count\">" .
            basename($url, ".png") . "</button></li>";
    };

    add_section ($sections, $logodata);

    add_section ($sections,
                 render_linked_property ("li:plaintext", $data, $context).
                 render_linked_property ("cc:legalcode", $data, $context));

    add_section ($sections, render_linked_property ("cc:permits", $data, $context));
    add_section ($sections, render_linked_property ("cc:requires", $data, $context));
    add_section ($sections, render_linked_property ("cc:prohibits", $data, $context));
    add_section ($sections, render_linked_property ("spdx:licenseId", $data, $context));

    echo join ("<hr />", $sections);

    echo "</ul>\n";
}

function render_notice ($notice)
{
    $orlater_checked = "";
    $orlater_bool = "false";
    $short_checked = "";
    $short_bool = "";

    if ($notice["li:orlater"])
    {
        $orlater_checked = 'checked="checked" ';
        $orlater_bool = "true";
    }

    if ($notice["li:short"])
    {
        $short_checked = 'checked="checked" ';
        $short = "true";
    }

    return '<div rel="https://licensedb.org/ns#notice">' .
        '<div class="notice-properties">' .
        '<input id="orlater" type="checkbox" ' . $orlater_checked .
        ' disabled="disabled" />'.
        '<span class="prefix">li:</span>orlater' .
        '<span style="display: none;" '.
        'property="https://licensedb.org/ns#orlater" '.
        'datatype="http://www.w3.org/2001/XMLSchema-datatypes#' .
        'boolean">' . $orlater_bool . '</span>'.
        '<input id="short" type="checkbox" ' . $short_checked .
        ' disabled="disabled" />'.
        '<span class="prefix">li:</span>short' .
        '<span style="display: none;" '.
        'property="https://licensedb.org/ns#short" '.
        'datatype="http://www.w3.org/2001/XMLSchema-datatypes#' .
        'boolean">' . $short_bool . '</span></div>'.
        '<h3><span class="prefix">li:</span>notice</h3>'.
        '<pre property="https://licensedb.org/ns#text">'.
        htmlentities($notice["li:text"]).'</pre></div>';
}

function cmp_notice ($a, $b)
{
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
    /* FIXME: sort notices. */

    $ret = "";
    if (!isset ($data["li:notice"]))
        return $ret;

    $notices = array ();
    if (!is_array ($data["li:notice"]))
    {
        $notices[0] = $data["li:notice"];
    }
    else
    {
        $notices = $data["li:notice"];
    }

    usort ($notices, "cmp_notice");

    foreach ($notices as $notice)
    {
        $ret .= render_notice ($notice);
    }

    return $ret;
}

