<!DOCTYPE html>
<html lang="en-US">
  <head>
    <meta charset="utf-8" />
    <title><?=$title ?></title>
    <link rel="stylesheet" href="<?=$wwwroot ?>licensedb.css" type="text/css">
    <link href="<?=$wwwroot ?>nprogress.css" rel="stylesheet" />
    <style>
     #nprogress .bar { background: #fff; }
     #nprogress .peg { box-shadow: 0 0 10px #fff, 0 0 5px #fff; }
     #nprogress .spinner-icon { border-top-color: #fff; border-left-color: #fff; }
    </style>
    <?php echo $embedded_vocab; ?>
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
        <?php echo $content ?>
    </div>

    <?php if ($footer): ?>
        <div id="footer">
            <p class="copyright">
                &copy; 2015 <a href="https://frob.nl">Kuno Woudt</a>, software licensed under
                <a rel="license" href="http://www.apache.org/licenses/LICENSE-2.0.html">Apache
                2.0</a>, database available under <a rel="license"
                href="http://creativecommons.org/publicdomain/zero/1.0/">CC0</a>.
                See <a href="/license">the license page</a> for more details.
            </p>
        </div>
    <?php endif ?>

    <?php echo $scripts ?>

  </body>
</html>
