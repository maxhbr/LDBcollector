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

      <h2>Licenses currently in the database</h2>

      <ul>
<?php

    $licenses = array ();

    if ($dh = opendir (dirname (__FILE__)."/../../data/"))
    {
        while (($file = readdir($dh)) !== false)
        {
            $matches = array ();
            if (preg_match ("/(.*).turtle$/", $file, $matches))
            {
                array_push ($licenses, $matches[1]);
            }
        }
        closedir ($dh);
    }

    sort ($licenses);
    foreach ($licenses as $id)
    {
        echo "<li><a href=\"$id\">$id</a></li>\n";
    }

?>
      </ul>
    </div>
