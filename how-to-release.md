= How to release

== Upstream part

 * test that the package builds:
   tito build --rpm --test
 * tito tag
 * git push --follow-tags origin

== Downstream part

 * fkinit
 * tito release all
 * do not forget to submit bodhi update
