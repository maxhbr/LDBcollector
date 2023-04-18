# Hermine Project
* url: 
* **example** raw data: git@gitlab.com:hermine-project/hermine.git  
  * `/examples/data/Exemple_licences.json`
  * `/examples/data/Example_generic_obligations.json`


## Example generic obligation 1
* "name": "Weak Copyleft",
* "description": "Some categories of derivative works or of works based on the Open Source Software must be distributed under the initial license or another license approved by the initial license.",
* "in_core": false,
* "metacategory": "IPManagement",
* "team": [ "Legal" ],
* "passivity": "Active"


## Example generic obligation 2

* "name": "Preserve IP mentions in Source code",
* "description": "Keep all legal notices and license texts intact, including in the headers.",
* "in_core": true,
* "metacategory": "Mentions",
* "team": [ "DevQA" ],
* "passivity": "Active"


## Example specific obligation
```json
[
    {
        "id": 15,
        "spdx_id": "AGPL-3.0-only",
        "long_name": "GNU Affero General Public License v3.0 only",
        "license_version": "3.0",
        "radical": "AGPL",
        "autoupgrade": null,
        "steward": "Free Software Foundation, Inc.",
        "inspiration_spdx": "",
        "copyleft": "Network",
        "allowed": "never",
...
        "obligation_set": [
            {
                "id": 57,
                "generic_name": "Non Tivoization",
                "name": "Non tovoization",
                "verbatim": "A \u201cUser Product\u201d is either (1) a \u201cconsumer product\u201d, which means any tangible personal property which is normally used for personal, family, or household purposes, or (2) anything designed or sold for incorporation into a dwelling. In determining whether a product is a consumer product, doubtful cases shall be resolved in favor of coverage. For a particular product received by a particular user, \u201cnormally used\u201d refers to a typical or common use of that class of product, regardless of the status of the particular user or of the way in which the particular user actually uses, or expects or is expected to use, the product. A product is a consumer product regardless of whether the product has substantial commercial, industrial or non-consumer uses, unless such uses represent the only significant mode of use of the product.\r\n\r\n\u201cInstallation Information\u201d for a User Product means any methods, procedures, authorization keys, or other information required to install and execute modified versions of a covered work in that User Product from a modified version of its Corresponding Source. The information must suffice to ensure that the continued functioning of the modified object code is in no case prevented or interfered with solely because modification has been made.\r\n\r\nIf you convey an object code work under this section in, or with, or specifically for use in, a User Product, and the conveying occurs as part of a transaction in which the right of possession and use of the User Product is transferred to the recipient in perpetuity or for a fixed term (regardless of how the transaction is characterized), the Corresponding Source conveyed under this section must be accompanied by the Installation Information. But this requirement does not apply if neither you nor any third party retains the ability to install modified object code on the User Product (for example, the work has been installed in ROM).\r\n\r\nThe requirement to provide Installation Information does not include a requirement to continue to provide support service, warranty, or updates for a work that has been modified or installed by the recipient, or for the User Product in which it has been modified or installed. Access to a network may be denied when the modification itself materially and adversely affects the operation of the network or violates the rules and protocols for communication across the network.\r\n\r\nCorresponding Source conveyed, and Installation Information provided, in accord with this section must be in a format that is publicly documented (and with an implementation available to the public in source code form), and must require no special password or key for unpacking, reading or copying.",
                "passivity": "Active",
                "trigger_expl": "DistributionSourceDistributionNonSource",
                "trigger_mdf": "Altered",
                "generic": 15
            },
            {
                "id": 1391,
                "generic_name": "Providing CSC to end user",
                "name": "Providing CSC to end user - network interaction",
                "verbatim": "13. Remote Network Interaction; Use with the GNU General Public License.\r\n\r\n  Notwithstanding any other provision of this License, if you modify the\r\nProgram, your modified version must prominently offer all users\r\ninteracting with it remotely through a computer network (if your version\r\nsupports such interaction) an opportunity to receive the Corresponding\r\nSource of your version by providing access to the Corresponding Source\r\nfrom a network server at no charge, through some standard or customary\r\nmeans of facilitating copying of software.  This Corresponding Source\r\nshall include the Corresponding Source for any work covered by version 3\r\nof the GNU General Public License that is incorporated pursuant to the\r\nfollowing paragraph.",
                "passivity": "Active",
                "trigger_expl": "NetworkAccess",
                "trigger_mdf": "Altered",
                "generic": 12
            },
            {
                "id": 56,
                "generic_name": "Providing CSC to end user",
                "name": "Providing CSC to end user - distribution",
                "verbatim": "6. Conveying Non-Source Forms.\r\n\r\nYou may convey a covered work in object code form under the terms of sections 4 and 5, provided that you also convey the machine-readable Corresponding Source under the terms of this License, in one of these ways:\r\n\r\n    a) Convey the object code in, or embodied in, a physical product (including a physical distribution medium), accompanied by the Corresponding Source fixed on a durable physical medium customarily used for software interchange.\r\n    b) Convey the object code in, or embodied in, a physical product (including a physical distribution medium), accompanied by a written offer, valid for at least three years and valid for as long as you offer spare parts or customer support for that product model, to give anyone who possesses the object code either (1) a copy of the Corresponding Source for all the software in the product that is covered by this License, on a durable physical medium customarily used for software interchange, for a price no more than your reasonable cost of physically performing this conveying of source, or (2) access to copy the Corresponding Source from a network server at no charge.\r\n    c) Convey individual copies of the object code with a copy of the written offer to provide the Corresponding Source. This alternative is allowed only occasionally and noncommercially, and only if you received the object code with such an offer, in accord with subsection 6b.\r\n    d) Convey the object code by offering access from a designated place (gratis or for a charge), and offer equivalent access to the Corresponding Source in the same way through the same place at no further charge. You need not require recipients to copy the Corresponding Source along with the object code. If the place to copy the object code is a network server, the Corresponding Source may be on a different server (operated by you or a third party) that supports equivalent copying facilities, provided you maintain clear directions next to the object code saying where to find the Corresponding Source. Regardless of what server hosts the Corresponding Source, you remain obligated to ensure that it is available for as long as needed to satisfy these requirements.\r\n    e) Convey the object code using peer-to-peer transmission, provided you inform other peers where the object code and Corresponding Source of the work are being offered to the general public at no charge under subsection 6d.",
                "passivity": "Active",
                "trigger_expl": "DistributionNonSource",
                "trigger_mdf": "AlteredUnmodified",
                "generic": 12
            },
            {
                "id": 53,
                "generic_name": "Display copyright and licence in Program",
                "name": "Display Appropriate Legal Notices in Program",
                "verbatim": "5. d) If the work has interactive user interfaces, each must display Appropriate Legal Notices; however, if the Program has interactive interfaces that do not display Appropriate Legal Notices, your work need not make them do so.",
                "passivity": "Active",
                "trigger_expl": "DistributionSourceDistributionNonSource",
                "trigger_mdf": "AlteredUnmodified",
                "generic": 18
            },
            {
                "id": 54,
                "generic_name": "SaaS : mentions",
                "name": "Mention availability of CSC in Network interactions",
                "verbatim": "13. Remote Network Interaction; Use with the GNU General Public License.\r\n\r\n  Notwithstanding any other provision of this License, if you modify the\r\nProgram, your modified version must prominently offer all users\r\ninteracting with it remotely through a computer network (if your version\r\nsupports such interaction) an opportunity to receive the Corresponding\r\nSource of your version by providing access to the Corresponding Source\r\nfrom a network server at no charge, through some standard or customary\r\nmeans of facilitating copying of software.  This Corresponding Source\r\nshall include the Corresponding Source for any work covered by version 3\r\nof the GNU General Public License that is incorporated pursuant to the\r\nfollowing paragraph.",
                "passivity": "Active",
                "trigger_expl": "DistributionSourceDistributionNonSource",
                "trigger_mdf": "AlteredUnmodified",
                "generic": 9
            },
            {
                "id": 51,
                "generic_name": "Preserve IP mentions in Source code",
                "name": "License and notices in source code",
                "verbatim": "4. Conveying Verbatim Copies.\r\n\r\nYou may convey verbatim copies of the Program's source code as you receive it, in any medium, provided that you conspicuously and appropriately publish on each copy an appropriate copyright notice; keep intact all notices stating that this License and any non-permissive terms added in accord with section 7 apply to the code; keep intact all notices of the absence of any warranty; and give all recipients a copy of this License along with the Program.\r\n\r\nYou may charge any price or no price for each copy that you convey, and you may offer support or warranty protection for a fee.",
                "passivity": "Active",
                "trigger_expl": "DistributionSourceDistributionNonSource",
                "trigger_mdf": "AlteredUnmodified",
                "generic": 3
            },
            {
                "id": 52,
                "generic_name": "Marking Modifications",
                "name": "Marking modifications",
                "verbatim": "5. a) The work must carry prominent notices stating that you modified it, and giving a relevant date.\r\nb) The work must carry prominent notices stating that it is released under this License and any conditions added under section 7. This requirement modifies the requirement in section 4 to \u201ckeep intact all notices\u201d.",
                "passivity": "Active",
                "trigger_expl": "DistributionSourceDistributionNonSource",
                "trigger_mdf": "AlteredUnmodified",
                "generic": 5
            },
            {
                "id": 55,
                "generic_name": "SaaS : network Copyleft",
                "name": "Strong network copyleft",
                "verbatim": "5. c) You must license the entire work, as a whole, under this\r\n    License to anyone who comes into possession of a copy.  This\r\n    License will therefore apply, along with any applicable section 7\r\n    additional terms, to the whole of the work, and all its parts,\r\n    regardless of how they are packaged.  This License gives no\r\n    permission to license the work in any other way, but it does not\r\n    invalidate such permission if you have separately received it.\r\n[...]\r\n  A compilation of a covered work with other separate and independent\r\nworks, which are not by their nature extensions of the covered work,\r\nand which are not combined with it such as to form a larger program,\r\nin or on a volume of a storage or distribution medium, is called an\r\n\"aggregate\" if the compilation and its resulting copyright are not\r\nused to limit the access or legal rights of the compilation's users\r\nbeyond what the individual works permit.  Inclusion of a covered work\r\nin an aggregate does not cause this License to apply to the other\r\nparts of the aggregate\r\n\r\n13 [...]\r\nNotwithstanding any other provision of this License, you have\r\npermission to link or combine any covered work with a work licensed\r\nunder version 3 of the GNU General Public License into a single\r\ncombined work, and to convey the resulting work.  The terms of this\r\nLicense will continue to apply to the part which is the covered work,\r\nbut the work with which it is combined will remain governed by version\r\n3 of the GNU General Public License.",
                "passivity": "Active",
                "trigger_expl": "DistributionSourceDistributionNonSource",
                "trigger_mdf": "AlteredUnmodified",
                "generic": 10
            },
```