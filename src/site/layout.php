<!DOCTYPE html>
<html lang="en-US">
  <head>
    <meta charset="utf-8" />
    <title><?=$title ?></title>
    <link rel="stylesheet" href="<?=$wwwroot ?>licensedb.css" type="text/css">
    <?php echo $embedded_vocab; ?>

    <style type="text/css">
     article.license-details { height: 88em; }
     p.plaintext,
     iframe { float: left; width: 46em; height: 80em; margin: 0; padding: 0; border: 0; }
     .sidebar {
         width: 24em;
         float: left;
         border: 1px solid #888;
         padding: 1em;
         margin: 0 1em 1em 0;
     }
     .sidebar hr { border: 0; border-top: 1px solid #888; }
    </style>
  </head>

  <body>
    <div id="header">
      <a href="/" title="home">
        <img src="/licensedb.png" style="margin: 1em;" />
      </a>
      <div id="menu">
        <ul>
          <li><a href="/">About</a></li>
          <li><a href="/id/">Database</a></li>
          <li><a href="/ns">Vocabulary</a></li>
          <li><a href="/license">License</a></li>
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
        See <a href="/license">the license page</a> for more details.
      </p>
    </div>

  </body>
</html>
