= How to release

== Upstream part

 * test that the package builds:
   tito build --rpm --test
 * tito tag
 * git push --follow-tags origin

== Downstream part

 * fkinit
 * tito release --no-build all
 * koji builds and bodhi updates are created automatically by Packit

== Update legal docs

 * make legal-doc
 * cp not-allowed-licenses.adoc allowed-licenses.adoc all-allowed.adoc ~/projects/fedora-legal-docs/modules/ROOT/pages/
   alter the path to your fedora-legal-docs checkout
 * cd ~/projects/fedora-legal-docs/
 * git commit -a -m 'update licenses using fedora-license-data'
 * review and create MR
