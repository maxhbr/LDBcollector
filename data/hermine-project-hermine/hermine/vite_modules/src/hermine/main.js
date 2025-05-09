/*
 * SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
 *
 * SPDX-License-Identifier: AGPL-3.0-only
 */

"use strict";

import "@fortawesome/fontawesome-free/css/all.min.css";

import "./fonts/nunito.css";
import "./theme/main.scss";



/* Aside: submenus toggle */
Array.from(document.getElementsByClassName('menu is-menu-main')).forEach(function (el) {
  Array.from(el.getElementsByClassName('has-dropdown-icon')).forEach(function (elA) {
    elA.addEventListener('click', function (e) {
      var dropdownIcon = e.currentTarget.getElementsByClassName('dropdown-icon')[0].getElementsByClassName('fas')[0];
      e.currentTarget.parentNode.classList.toggle('is-active');
      dropdownIcon.classList.toggle('fa-caret-right');
      dropdownIcon.classList.toggle('fa-caret-down');
    });
  });
});
/* Aside Mobile toggle */

Array.from(document.getElementsByClassName('jb-aside-mobile-toggle')).forEach(function (el) {
  el.addEventListener('click', function (e) {
    var dropdownIcon = e.currentTarget.getElementsByClassName('icon')[0].getElementsByClassName('mdi')[0];
    document.documentElement.classList.toggle('has-aside-mobile-expanded');
    dropdownIcon.classList.toggle('mdi-forwardburger');
    dropdownIcon.classList.toggle('mdi-backburger');
  });
});
/* NavBar menu mobile toggle */

Array.from(document.getElementsByClassName('jb-navbar-menu-toggle')).forEach(function (el) {
  el.addEventListener('click', function (e) {
    var dropdownIcon = e.currentTarget.getElementsByClassName('icon')[0].getElementsByClassName('mdi')[0];
    document.getElementById(e.currentTarget.getAttribute('data-target')).classList.toggle('is-active');
    dropdownIcon.classList.toggle('mdi-dots-vertical');
    dropdownIcon.classList.toggle('mdi-close');
  });
});



