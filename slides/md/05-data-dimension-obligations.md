# License Obligations and Rules


## Some obligations are implied by classification
e.g. Copyleft implies usually some expected obligations


## permissions / conditions / limitations
* [choosealicense.com](https://choosealicense.com/) defines
  * permissions / conditions / limitations
* tl;drLegal uses
  * Can / Cannot / Must


<!-- .slide: data-background-iframe="https://choosealicense.com/licenses/mit/" data-background-interactive="true" data-preload="false" -->


<!-- .slide: data-background-iframe="https://www.tldrlegal.com/license/mit-license" data-background-interactive="true" data-preload="false" -->


## Rule based description of obligations
* OSADL writes [License Checklists](https://www.osadl.org/OSADL-Open-Source-License-Checklists.oss-compliance-lists.0.html)
* FINOS [Open Source License Compliance Handbook](https://github.com/finos/OSLC-handbook)
* Hitachi [OSS License Open Data](https://github.com/Hitachi/open-license)
* Hermine
* ...


## OSADL
### Example: BSD-3-Clause
```txt
USE CASE Source code delivery
	YOU MUST Forward Copyright notices
	YOU MUST Forward License text
	YOU MUST Forward Warranty disclaimer
	YOU MUST NOT Promote
USE CASE Binary delivery
	YOU MUST Provide Copyright notices In Documentation OR Distribution material
	YOU MUST Provide License text In Documentation OR Distribution material
	YOU MUST Provide Warranty disclaimer In Documentation OR Distribution material
	YOU MUST NOT Promote
```


## FINOS [Open Source License Compliance Handbook](https://github.com/finos/OSLC-handbook)
The OSLC-handbook defines tables with conditions per usecase:
# GNU Affero General Public License 3.0
<table>
<colgroup>
<col style="width: 30%" />
<col style="width: 4%" />
<col style="width: 4%" />
<col style="width: 4%" />
<col style="width: 4%" />
<col style="width: 50%" />
</colgroup>
<thead>
<tr class="header">
<th>Description</th>
<th>UB</th>
<th>MB</th>
<th>US</th>
<th>MS</th>
<th>Compliance Notes</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td><p>Provide copy of license</p></td>
<td><p>X</p></td>
<td><p>X</p></td>
<td><p>X</p></td>
<td><p>X</p></td>
<td><p>It must be an actual copy of the license not a website link</p></td>
</tr>
<tr class="even">
<td><p>Retain notices on all files</p></td>
<td><p>X</p></td>
<td><p>X</p></td>
<td><p>X</p></td>
<td><p>X</p></td>
<td><p>Source files usually have a standard license header that includes a copyright notice and disclaimer of warranty. This is also where you determine if the license is “or later” or the specific version only</p></td>
</tr>
<tr class="odd">
<td><p>Notice of modifications</p></td>
<td></td>
<td><p>X</p></td>
<td></td>
<td><p>X</p></td>
<td><p>Modified files must have “prominent notices that you changed the files” and a date</p></td>
</tr>
<tr class="even">
<td><p>Modifications or derivative work must be licensed under same license</p></td>
<td></td>
<td><p>X</p></td>
<td></td>
<td><p>X</p></td>
<td><p>Strong copyleft or reciprocal, project-based license meaning that derivative works must also be under AGPL-3.0. For more information about AGPL-3.0 compliance and this condition in particular (which is the same as for GPL-3.0), see the references provided or consult with your open source legal counsel.</p></td>
</tr>
<tr class="odd">
<td><p>Provide corresponding source code</p></td>
<td><p>X</p></td>
<td><p>X</p></td>
<td></td>
<td></td>
<td><p>Corresponding Source = all the source code needed to generate, install, and (for an executable work) run the object code and to modify the work, including scripts to control those activities. Options for providing source = with binary, written offer, or via a network server. See section 6 for more details. For more information about AGPL-3.0 compliance and this condition in particular, see the references provided or consult your open source legal counsel.</p></td>
</tr>
<tr class="even">
<td><p>No additional restrictions</p></td>
<td><p>X</p></td>
<td><p>X</p></td>
<td><p>X</p></td>
<td><p>X</p></td>
<td><p>You may not impose any further restrictions on the exercise of the rights granted under this license.</p></td>
</tr>
</tbody>
</table>


## Hitachi [OSS License Open Data](https://github.com/Hitachi/open-license)
### Example BSD-3-Clause (translated via DeepL)
* **Action:** Use the obtained source code without modification:
  Use the fetched code as it is.
* **Action:** Modify the obtained source code.
* **Action:** Using Modified Source Code
* **Action:** Distribute the obtained source code without modification
  * **Obligation:** Include a copyright notice, list of terms and conditions, and disclaimer included in the license
* **Action:** Distribution of Modified Source Code
  * **Obligation:** Include a copyright notice, list of terms and conditions, and disclaimer included in the license
* **Action:** Use the name of the owner or contributor to promote or sell the derived product:
  * **Requisite:** Get special permission in writing.
* ...

## Hermine
