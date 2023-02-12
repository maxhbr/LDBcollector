pub mod model;

#[macro_export]
macro_rules! lic {
    ($l:tt) => {
        $crate::model::core::LicenseName::new($l)
    };
}

pub mod source_spdx {
    use super::model::graph::*;
    use crate::model::core::LicenseName;
    use spdx::identifiers::LICENSES;
    use spdx::*;

    static ORIGIN: &'static Origin =
        &Origin::new_with_file("SPDX", "https://spdx.org/licenses/", Option::None);

    fn licenses_satisfying_flag<'a>(flag_fn: impl Fn(LicenseId) -> bool) -> Vec<LicenseName<'a>> {
        LICENSES
            .into_iter()
            .filter(|(name, _, _)| flag_fn(spdx::license_id(name).unwrap()))
            .map(|(name, _, _)| lic!(name))
            .collect()
    }

    pub fn add_spdx(s: LicenseGraph) -> LicenseGraph {
        LICENSES
            .into_iter()
            .fold(s, |acc: LicenseGraph, i @ (name, full_name, _)| {
                acc.add_aliases(vec![lic!(full_name), lic!(name)], ORIGIN)
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

    // fn license_from_osadl_checklist<'a>(checklist: &Path) -> Option<LicenseName<'a>> {
    //     checklist
    //         .with_extension("")
    //         .file_name()
    //         .and_then(|license_name| license_name.to_str())
    //         .map(|license_name| lic!(license_name))
    // }

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
                        vec![], //vec!(LicenseName::new(lic_str)),
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
    impl CopyleftFamilyVersion {
        fn get_id(&self) -> &str {
            &self.id
        }
    }

    #[derive(Debug, Serialize, Deserialize, Clone)]
    struct CopyleftFamily {
        name: String,
        versions: Vec<CopyleftFamilyVersion>,
    }
    impl CopyleftFamily {
        fn get_family_name(&self) -> &str {
            &self.name
        }
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

    fn read_blueoakcouncil_copyleft_list_vec(
    ) -> Result<Vec<(String, String, String, String, String)>, Box<dyn Error>> {
        let CopyleftList {
            version: list_version,
            families: families_per_kind,
        } = read_blueoakcouncil_copyleft_list()?;

        println!("copyleft_list version: {}", list_version);
        Ok(families_per_kind
            .iter()
            .flat_map(|(kind, families)| families.iter().map(move |family| (kind, family)))
            .flat_map(
                |(
                    kind,
                    CopyleftFamily {
                        name: family_name,
                        versions,
                    },
                )| {
                    versions
                        .iter()
                        .map(move |version| (kind, family_name, version))
                },
            )
            .map(
                |(kind, family_name, CopyleftFamilyVersion { id, name, url })| {
                    (
                        kind.clone(),
                        family_name.clone(),
                        id.clone(),
                        name.clone(),
                        url.clone(),
                    )
                },
            )
            .collect())
    }

    pub fn add_blueoakcouncil_copyleft_list(s: LicenseGraph) -> LicenseGraph {
        let vec = read_blueoakcouncil_copyleft_list_vec().expect("...");
        s
        // vec.iter()
        //     .fold(s,|acc,(kind,_,_,_,_)| {
        //         acc.add_license(lic!(kind), ORIGIN)
        //     })
    }

    pub fn add_blueoakcouncil_license_list(s: LicenseGraph) -> LicenseGraph {
        s
    }

    pub fn add_blueoakcouncil(s: LicenseGraph) -> LicenseGraph {
        add_blueoakcouncil_license_list(
            add_blueoakcouncil_copyleft_list(s)
        )
    }
}
