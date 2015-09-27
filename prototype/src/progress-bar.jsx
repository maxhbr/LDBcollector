/**
 *   This file is part of wald:find.
 *   Copyright (C) 2015  Kuno Woudt <kuno@frob.nl>
 *
 *   This program is free software: you can redistribute it and/or modify
 *   it under the terms of copyleft-next 0.3.0.  See LICENSE.txt.
 */

'use strict';

jQuery.ajaxSetup({
    xhr: function () {
        var request = new XMLHttpRequest ();

        NProgress.start ();

        var progress = function () {
            NProgress.inc ();
        };

        var complete = function () {
            NProgress.done ();
        };

        request.addEventListener ("progress", progress, false);
        request.addEventListener ("load", complete, false);
        request.addEventListener ("error", complete, false);
        request.addEventListener ("abort", complete, false);

        return request;
    }
});

// -*- mode: web -*-
// -*- engine: jsx -*-
