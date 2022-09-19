= How to release

== Upstream part

 * rpmdev-bumpspec fedora-license-data.spec
 * git add fedora-license-data.spec
 * git commit -m 'v1.4 release'
 * git tag v1.4
 * git push --tags

== Downstream part

 * packit prepare-sources
 * cp fedora-license-data.spec ~/rpmbuild/SPECS
 * cp prepare_sources_result/fedora-license-data-1.4.tar.gz ~/rpmbuild/SOURCES
 * rpmbuild -bs ~/rpmbuild/SPECS/fedora-license-data.spec

 * cd /tmp
 * fedpkg clone fedora-license-data
 * cd fedora-license-data
 * fedpkg import ~/rpmbuild/SRPMS/fedora-license-data-1.4-1.fc36.src.rpm
 * git commit -a -m 'rebase to 1.4'
 * git push && fedpkg build
 * repeat for every supported branch
 * do not forget to submit bodhi update
