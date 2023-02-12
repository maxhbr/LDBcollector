pub mod model;

#[macro_export]
macro_rules! lic {
    ($l:tt) => {
        $crate::model::core::LicenseName::new(String::from($l))
    };
}

#[macro_export]
macro_rules! lic_string {
    ($l:tt) => {
        $crate::model::core::LicenseName::new($l.clone())
    };
}

pub mod source_spdx {
    use super::model::graph::*;
    use crate::model::core::LicenseName;
    use spdx::identifiers::LICENSES;
    use spdx::*;

    static ORIGIN: &'static Origin =
        &Origin::new_with_file("SPDX", "https://spdx.org/licenses/", Option::None);

    fn licenses_satisfying_flag(flag_fn: impl Fn(LicenseId) -> bool) -> Vec<LicenseName> {
        LICENSES
            .into_iter()
            .filter(|(name, _, _)| flag_fn(spdx::license_id(name).unwrap()))
            .map(|(name, _, _)| {
                let name = String::from(*name);
                lic!(name)
            })
            .collect()
    }

    pub fn add_spdx(s: LicenseGraph) -> LicenseGraph {
        LICENSES
            .into_iter()
            .fold(s, |acc: LicenseGraph, i @ (name, full_name, _)| {
                let name = String::from(*name);
                let full_name = String::from(*full_name);
                acc.add_aliases(
                    vec![
                        LicenseName::new(name.clone()),
                        LicenseName::new(full_name.clone()),
                    ],
                    ORIGIN,
                )
                .add_relational_fact(
                    LicenseGraphNode::mk_json_statement(i),
                    vec![lic!(full_name), lic!(name)],
                    ORIGIN,
                )
                // .add_relational_fact(
                //     LicenseGraphNode::mk_statement(
                //         license_id(name).unwrap().text()
                //     ),
                //     vec!(lic!(name)),
                //     ORIGIN)
            })
            .add_relational_fact(
                LicenseGraphNode::mk_statement("is_copyleft"),
                licenses_satisfying_flag(|l| l.is_copyleft()),
                ORIGIN,
            )
            .add_relational_fact(
                LicenseGraphNode::mk_statement("is_deprecated"),
                licenses_satisfying_flag(|l| l.is_deprecated()),
                ORIGIN,
            )
            .add_relational_fact(
                LicenseGraphNode::mk_statement("is_fsf_free_libre"),
                licenses_satisfying_flag(|l| l.is_fsf_free_libre()),
                ORIGIN,
            )
            .add_relational_fact(
                LicenseGraphNode::mk_statement("is_gnu"),
                licenses_satisfying_flag(|l| l.is_gnu()),
                ORIGIN,
            )
            .add_relational_fact(
                LicenseGraphNode::mk_statement("is_osi_approved"),
                licenses_satisfying_flag(|l| l.is_osi_approved()),
                ORIGIN,
            )
    }
}

pub mod source_osadl {
    use crate::model::core::LicenseName;
    use std::ffi::OsStr;
    use std::fs;
    use std::path::Path;

    use super::model::graph::*;

    static ORIGIN: &'static Origin = &Origin::new_with_file(
        "OSADL",
        "https://www.osadl.org/Access-to-raw-data.oss-compliance-raw-data-access.0.html",
        Option::None,
    );

    pub fn add_osadl_checklist(s: LicenseGraph) -> LicenseGraph {
        fs::read_dir("./data/OSADL-checklists/")
            .unwrap()
            .filter_map(|result| {
                result
                    .ok()
                    .map(|dir_entry| dir_entry.path())
                    .filter(|path| match path.extension() {
                        Option::Some(extension) => extension == OsStr::new("osadl"),
                        _ => false,
                    })
            })
            .fold(s, |acc: LicenseGraph, checklist| {
                let contents = fs::read_to_string(&checklist)
                    .expect("Should have been able to read OSADL rule");
                if let Some(lic_str) = checklist
                    .with_extension("")
                    .file_name()
                    .and_then(|license_name| license_name.to_str())
                {
                    acc.add_relational_fact(
                        LicenseGraphNode::mk_statement(&contents),
                        vec![lic!(lic_str)],
                        ORIGIN,
                    )
                } else {
                    acc
                }
            })
    }
}

pub mod source_scancode {}

pub mod source_blueoakcouncil {
    use super::model::graph::*;
    use crate::model::core::LicenseName;

    use serde_derive::{Deserialize, Serialize};
    use std::collections::HashMap;
    use std::error::Error;
    use std::fs::File;
    use std::io::BufReader;
    use std::path::Path;

    static ORIGIN: &'static Origin = &Origin::new_with_file(
        "Blue Oak Council",
        "https://blueoakcouncil.org/",
        Option::None,
    );

    #[derive(Debug, Serialize, Deserialize, Clone)]
    struct CopyleftFamilyVersion {
        id: String,
        name: String,
        url: String,
    }

    #[derive(Debug, Serialize, Deserialize, Clone)]
    struct CopyleftFamily {
        name: String,
        versions: Vec<CopyleftFamilyVersion>,
    }

    #[derive(Debug, Serialize, Deserialize, Clone)]
    struct CopyleftList {
        version: String,
        families: HashMap<String, Vec<CopyleftFamily>>,
    }

    fn read_blueoakcouncil_copyleft_list() -> Result<CopyleftList, Box<dyn Error>> {
        let file = File::open("./data/blueoakcouncil/blue-oak-council-copyleft-list.json")?;
        let reader = BufReader::new(file);
        let cl = serde_json::from_reader(reader)?;
        Ok(cl)
    }

    pub fn add_blueoakcouncil_copyleft_list(s: LicenseGraph) -> LicenseGraph {
        let CopyleftList {
            version: list_version,
            families: families_per_kind,
        } = read_blueoakcouncil_copyleft_list().expect("parsing of copyleft list should succeed");

        families_per_kind.iter().fold(s, |ss, (kind, families)| {
            let kind = LicenseGraphNode::mk_statement(kind);
            let (ss, ids) = families.iter().fold(
                (ss, vec![]),
                |(sss, mut idss): (_, Vec<LicenseName>),
                 CopyleftFamily {
                     name: family_name,
                     versions,
                 }| {
                    let family_name = lic!(family_name);
                    let (sss, mut ids) = versions.iter().fold(
                        (sss, vec![]),
                        |(ssss, mut ids): (_, Vec<LicenseName>),
                         CopyleftFamilyVersion { id, name, url }| {
                            println!("{:?} -> {} -> {} , {}", kind, family_name, id, name);
                            let url = LicenseGraphNode::mk_statement(url);
                            let id = lic_string!(id);
                            let ssss = ssss
                                .add_aliases(vec![id.clone(), lic_string!(name)], ORIGIN)
                                .add_relational_fact(url, vec![id.clone()], ORIGIN);
                            ids.push(id);
                            (ssss, ids)
                        },
                    );
                    let sss = sss.add_relation(
                        family_name.clone(),
                        ids.clone(),
                        LicenseGraphEdge::Better,
                        ORIGIN,
                    );
                    idss.append(&mut ids);
                    idss.push(family_name);
                    (sss, idss)
                },
            );
            ss.add_relational_fact(kind, ids, ORIGIN)
        })
    }

    pub fn add_blueoakcouncil_license_list(s: LicenseGraph) -> LicenseGraph {
        s
    }

    pub fn add_blueoakcouncil(s: LicenseGraph) -> LicenseGraph {
        add_blueoakcouncil_license_list(add_blueoakcouncil_copyleft_list(s))
    }
}
