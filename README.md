# ldbcollector

This is a framework to collect, parse, normalize and join metadata about open source and other software licenses.


## History:
This is a rewrite of the old ldbcollector, which is found in ./old-ldbcollector or in the branch v1.

This rewrite is not yet stable and for stable use the old version is prefered.

# Sources and Outputs

```mermaid
graph LR;
    BlueOak["Blue Oak Council\nPermissive license list\nCopyleft license list"]--->LDBcollector;
    Cavil[Cavil\ngithub.com/openSUSE/cavil]---->LDBcollector;
    ChooseALicense[choosalicense.com]--->LDBcollector;
    EclipseOrgLegal[eclipse.org/legal/license.json]---->LDBcollector;
    Fedora[gitlab.com/fedora/legal/fedora-license-data]--->LDBcollector;
    FOSSLight---->LDBcollector;
    Fossology--->LDBcollector;
    FSF[gnu.org/licenses/license-list.html]---->LDBcollector;
    GoogleLicensePolicy[opensource.google/documentation/reference/thirdparty/licenses]--->LDBcollector;
    HitachiOpenLicense[github.com/Hitachi/open-license]---->LDBcollector;
    Ifross[ifross.github.io/ifrOSS/Lizenzcenter]--->LDBcollector;
    Metaeffekt[metaeffekt.com/#universe]---->LDBcollector;
    OKFN[opendefinition.org/licenses/]--->LDBcollector;
    OSADL[OSADL Open Source License Checklists]---->LDBcollector;
    OSI[opensource.org/licenses]--->LDBcollector;
    OSLC[github.com/finos/OSLC-handbook]---->LDBcollector;
    Scancode[scancode-licensedb.aboutcode.org]--->LDBcollector;
    SPDX[spdx.org/licenses]---->LDBcollector;
    Warpr[github.com/warpr/licensedb]--->LDBcollector;

    Curation["Manual Curations"]-->LDBcollector;

    LDBcollector-->GraphViz;
    LDBcollector-->JSON;
    LDBcollector-->Metrics;
    LDBcollector--->Server[Interactive Server\nto browse and analyze\nserved on localhost:3000];
    GraphViz --> Server;
    JSON --> Server;
    LDBcollector--> Wiki;
    LDBcollector--->Policy[Open Source Policy];
    Wiki-->Policy;
```