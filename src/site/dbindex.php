The License Database

      <h1>The License Database</h1>

      <p>
        If you want to add an entry to the database, or edit an
        existing entry in the database, please download the source
        code from our
        <a href="https://gitorious.org/licensedb/licensedb/">repository
        on gitorious</a>.  The file <code>EDITING.txt</code>
        in the project root contains instructions and guidelines for adding
        data to the database.
      </p>

      <p>
       If you want to use the database in an application, you can download
       the <a href="https://licensedb.org/dl/license-database.tar.gz">full database</a>.
      </p>

      <h2>Licenses currently in the database</h2>

      <div id="filter" style="display: none;">
        Showing <span id="selected">4</span> of <span id="total">10</span>
        licenses, including:<br />
        <label><input type="checkbox" class="filter nonfree" />non-free</label>
        <label><input type="checkbox" class="filter deprecated" />superseded / deprecated</label>
        <label><input type="checkbox" class="filter jurisdiction" />jurisdiction specific</label>
        <script>
          var update_filters = function (ev) {
              $('#database li').show ();
              $.each ([ "nonfree", "deprecated", "jurisdiction" ], function (key, val) {
                  if (! $('input.filter.' + val).is(':checked'))
                  {
                      $('#database li.' + val).hide ();
                  }
              });
              $('#selected').text ($('#database li:visible').length);
          };
          $(document).ready (function () {
              $('#filter').show ();
              $('#total').text ($('#database li').length);
              update_filters ();
          });
          $('input.filter').on ('change', update_filters);
        </script>
      </div>

      <ul id="database">
<?php

    function by_name ($a, $b) {
        return strcasecmp ($a['li:name'], $b['li:name']);
    };

    $licenses = array ();
    $json_sources_path = dirname (__FILE__)."/../../www/id";

    if ($dh = opendir ($json_sources_path))
    {
        while (($file = readdir($dh)) !== false)
        {
            $matches = array ();
            if (preg_match ("/(.*).json$/", $file, $matches))
            {
                array_push ($licenses, json_decode (
                                file_get_contents ("$json_sources_path/$file"), true));
            }
        }
        closedir ($dh);
    }

    usort ($licenses, "by_name");

    foreach ($licenses as $data)
    {
        $classes = array ();

        if (!array_key_exists ("li:libre", $data))
        {
            $classes["nonfree"] = true;
        }

        if (array_key_exists ("cc:jurisdiction", $data))
        {
            $classes["jurisdiction"] = true;
        }

        if (array_key_exists ("dc:isReplacedBy", $data)
            || array_key_exists ("cc:deprecatedOn", $data))
        {
            $classes["deprecated"] = true;
        }

        $id = $data["li:id"];
        $name = $data["li:name"];
        $class = join (" ", array_keys ($classes));

        echo "<li class=\"$class\"><a href=\"$id\">$name</a></li>\n";
    }

?>
      </ul>
    </div>
