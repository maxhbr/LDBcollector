pub mod model;
mod utils;

use wasm_bindgen::prelude::*;

// When the `wee_alloc` feature is enabled, use `wee_alloc` as the global
// allocator.
#[cfg(feature = "wee_alloc")]
#[global_allocator]
static ALLOC: wee_alloc::WeeAlloc = wee_alloc::WeeAlloc::INIT;

#[macro_export]
macro_rules! lic {
    ($l:tt) => {
        $crate::model::core::LicenseName::new(String::from($l))
    };
}


#[wasm_bindgen]
extern {
    fn alert(s: &str);
}

#[wasm_bindgen]
pub fn greet() {
    alert("Hello, ldbcollector-rust!");
}

// ############################################################################

#[macro_export]
macro_rules! lic_string {
    ($l:tt) => {
        $crate::model::core::LicenseName::new($l.clone())
    };
}

pub mod source_spdx {
    use super::model::graph::*;
    use crate::model::core::LicenseName;
    use spdx::identifiers::{IMPRECISE_NAMES, LICENSES};
    use spdx::*;

    static ORIGIN: &'static Origin = &Origin::new_with_file("SPDX", "https://spdx.org/licenses/");

    // fn task_for_licenses_satisfying_flag(flag_name: &str, flag_fn: impl Fn(LicenseId) -> bool) -> LicenseGraphBuilderTask {
    //     let affected = LICENSES
    //         .into_iter()
    //         .filter(|(name, _, _)| flag_fn(spdx::license_id(name).unwrap()))
    //         .map(|(name, _, _)| {
    //             let name = String::from(*name);
    //             lic!(name)
    //         })
    //         .map(|name| LicenseGraphNode::LicenseNameNode { license_name: name })
    //         .collect();

    //      LicenseGraphBuilderTask::AddEdge {
    //          lefts: vec!(LicenseGraphNode::mk_statement(flag_name)),
    //          rights: Box::new(
    //              LicenseGraphBuilderTask::AddNodes {
    //                  nodes: affected
    //              }
    //          ),
    //          edge: LicenseGraphEdge::AppliesTo
    //      }
    // }

    fn task_for_license_satisfying_flag(
        node: LicenseGraphNode,
        name: &str,
        flag_name: &str,
        flag_fn: impl Fn(LicenseId) -> bool,
    ) -> Vec<LicenseGraphNode> {
        if flag_fn(spdx::license_id(name).unwrap()) {
            vec![LicenseGraphNode::mk_statement(flag_name)]
        } else {
            vec![]
        }
    }

    pub struct SpdxSource {}
    impl Source for SpdxSource {
        fn get_origin(&self) -> Origin<'static> {
            Origin::new_with_file("SPDX", "https://spdx.org/licenses/")
        }

        fn get_tasks(&self) -> Vec<LicenseGraphBuilderTask> {
            LICENSES
                .into_iter()
                .flat_map(|i @ (name, full_name, _)| {
                    let license_name = String::from(*name);
                    let full_name = String::from(*full_name);
                    let node = LicenseGraphNode::LicenseNameNode {
                        license_name: lic!(license_name),
                    };
                    let add_json_task = LicenseGraphBuilderTask::AddEdge {
                        lefts: vec![LicenseGraphNode::mk_json_statement(i)],
                        rights: Box::new(LicenseGraphBuilderTask::AddNodes {
                            nodes: vec![node.clone()],
                        }),
                        edge: LicenseGraphEdge::AppliesTo,
                    };
                    vec![
                        LicenseGraphBuilderTask::AddEdge {
                            lefts: vec![LicenseGraphNode::LicenseNameNode {
                                license_name: lic!(full_name),
                            }],
                            rights: Box::new(LicenseGraphBuilderTask::AddNodes {
                                nodes: vec![node.clone()],
                            }),
                            edge: LicenseGraphEdge::Same,
                        },
                        add_json_task.clone(),
                        LicenseGraphBuilderTask::AddEdge {
                            lefts: {
                                let spdx_license = spdx::license_id(name).unwrap();
                                let flags: Vec<(&str, bool)> = vec![
                                    ("is_deprecated", spdx_license.is_deprecated()),
                                    ("is_fsf_free_libre", spdx_license.is_fsf_free_libre()),
                                    ("is_gnu", spdx_license.is_gnu()),
                                    ("is_osi_approved", spdx_license.is_osi_approved()),
                                    ("Copyleft", spdx_license.is_copyleft()),
                                ];
                                flags
                                    .iter()
                                    .filter_map(|(flag, flag_bool)| {
                                        if *flag_bool {
                                            Option::Some(LicenseGraphNode::mk_statement(flag))
                                        } else {
                                            Option::None
                                        }
                                    })
                                    .collect()
                            },
                            rights: Box::new(add_json_task),
                            edge: LicenseGraphEdge::AppliesTo,
                        },
                    ]
                })
                .collect()
        }
    }

    pub struct EmbarkSpdxSource {}
    impl Source for EmbarkSpdxSource {
        fn get_origin(&self) -> Origin<'static> {
            Origin::new_with_file("Embark SPDX lib", "https://github.com/EmbarkStudios/spdx")
        }

        fn get_tasks(&self) -> Vec<LicenseGraphBuilderTask> {
            IMPRECISE_NAMES
                .into_iter()
                .map(|i @ (imprecise, better)| {
                    let imprecise = String::from(*imprecise);
                    let better = String::from(*better);
                    LicenseGraphBuilderTask::AddEdge {
                        lefts: vec![LicenseGraphNode::LicenseNameNode {
                            license_name: lic_string!(imprecise),
                        }],
                        rights: Box::new(LicenseGraphBuilderTask::AddNodes {
                            nodes: vec![LicenseGraphNode::LicenseNameNode {
                                license_name: lic_string!(better),
                            }],
                        }),
                        edge: LicenseGraphEdge::HintsTowards,
                    }
                })
                .collect()
        }
    }
}

pub mod source_osadl {
    use std::ffi::OsStr;
    use std::fs;

    use super::model::graph::*;

    pub struct OsadlSource {}
    impl Source for OsadlSource {
        fn get_origin(&self) -> Origin<'static> {
            Origin::new_with_file(
                "OSADL",
                "https://www.osadl.org/Access-to-raw-data.oss-compliance-raw-data-access.0.html",
            )
        }

        fn get_tasks(&self) -> Vec<LicenseGraphBuilderTask> {
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
                .map(|checklist| {
                    let contents = fs::read_to_string(&checklist)
                        .expect("Should have been able to read OSADL rule");
                    if let Some(lic_str) = checklist
                        .with_extension("")
                        .file_name()
                        .and_then(|license_name| license_name.to_str())
                    {
                        log::debug!("{}", lic_str);
                        LicenseGraphBuilderTask::AddEdge {
                            lefts: vec![LicenseGraphNode::StatementRule {
                                statement_content: contents,
                            }],
                            rights: Box::new(LicenseGraphBuilderTask::AddNodes {
                                nodes: vec![LicenseGraphNode::LicenseNameNode {
                                    license_name: lic!(lic_str),
                                }],
                            }),
                            edge: LicenseGraphEdge::AppliesTo,
                        }
                    } else {
                        LicenseGraphBuilderTask::Noop {}
                    }
                })
                .collect()
        }
    }
}

pub mod source_scancode {
    use super::model::graph::*;

    use itertools::Itertools;
    use serde_derive::{Deserialize, Serialize};
    use std::error::Error;
    use std::fs::File;
    use std::io::BufReader;

    static BASEPATH: &'static str = "./data/nexB-scancode-licensedb/docs/";

    #[derive(Debug, Serialize, Deserialize, Clone)]
    struct IndexEntry {
        license_key: String,
        category: String,
        spdx_license_key: Option<String>,
        other_spdx_license_keys: Vec<String>,
        is_exception: bool,
        is_deprecated: bool,
        json: String,
        yaml: String,
        html: String,
        license: String,
    }
    #[derive(Debug, Serialize, Deserialize, Clone)]
    struct Entry {
        key: String,
        short_name: String,
        name: String,
        category: String,
        owner: String,
        homepage_url: Option<String>,
        notes: Option<String>,
        spdx_license_key: Option<String>,
        other_spdx_license_keys: Option<Vec<String>>,
        osi_license_key: Option<String>,
        text_urls: Option<Vec<String>>,
        osi_url: Option<String>,
        faq_url: Option<String>,
        other_urls: Option<Vec<String>>,
        // ignorable_copyrights: Option<Vec<String>>,
        // ignorable_holders: Option<Vec<String>>,
        // ignorable_urls: Option<Vec<String>>,
        text: Option<String>,
    }
    impl Entry {
        fn get_other_license_names(self) -> Vec<String> {
            let mut names = vec![];
            match self {
                Entry {
                    key,
                    short_name,
                    name,
                    category: _,
                    owner: _,
                    homepage_url: _,
                    notes: _,
                    spdx_license_key,
                    other_spdx_license_keys: _,
                    osi_license_key,
                    text_urls: _,
                    osi_url: _,
                    faq_url: _,
                    other_urls: _,
                    text: _,
                } => {
                    spdx_license_key.map(|spdx_license_key| names.push(spdx_license_key));
                    names.push(short_name);
                    names.push(name);

                    // TODO
                    // other_spdx_license_keys.map(|other_spdx_license_keys|
                    //     other_spdx_license_keys
                    //        .iter()
                    //        .map(|other_spdx_license_key| names.push(other_spdx_license_key))
                    // );
                    osi_license_key.map(|osi_license_key| names.push(osi_license_key));
                }
            }
            names.into_iter().unique().collect()
        }
        fn get_urls(self) -> Vec<String> {
            let mut urls = vec![];
            match self {
                Entry {
                    key: _,
                    short_name: _,
                    name: _,
                    category: _,
                    owner: _,
                    homepage_url,
                    notes: _,
                    spdx_license_key: _,
                    other_spdx_license_keys: _,
                    osi_license_key: _,
                    text_urls: _,
                    osi_url,
                    faq_url,
                    other_urls: _,
                    text: _,
                } => {
                    homepage_url.map(|url| urls.push(url));
                    osi_url.map(|url| urls.push(url));
                    faq_url.map(|url| urls.push(url));
                    // TODO
                    // other_urls,
                    // TODO
                    // text_urls,
                }
            }
            urls
        }
    }

    fn read_index() -> Result<Vec<IndexEntry>, Box<dyn Error>> {
        let file = File::open(format!("{}index.json", BASEPATH))?;
        let reader = BufReader::new(file);
        let index = serde_json::from_reader(reader)?;
        Ok(index)
    }

    fn read_licenses() -> Result<Vec<(Entry, IndexEntry)>, Box<dyn Error>> {
        let index = read_index()?;
        index
            .iter()
            .map(
                |ie @ IndexEntry {
                     license_key,
                     category,
                     spdx_license_key,
                     other_spdx_license_keys,
                     is_exception,
                     is_deprecated,
                     json,
                     yaml,
                     html,
                     license,
                 }| {
                    log::debug!("... READ {}", json);
                    let file = File::open(format!("{}{}", BASEPATH, json))?;
                    let reader = BufReader::new(file);
                    let entry = serde_json::from_reader(reader)?;
                    Ok((entry, ie.clone()))
                },
            )
            .collect()
    }

    pub struct EmbarkSpdxSource {}
    impl Source for EmbarkSpdxSource {
        fn get_origin(&self) -> Origin<'static> {
            Origin::new_with_file(
                "Scancode licensedb",
                "https://scancode-licensedb.aboutcode.org/",
            )
        }

        fn get_tasks(&self) -> Vec<LicenseGraphBuilderTask> {
            let licenses = read_licenses().expect("Parsing of scancode licenses should work");
            licenses
                .iter()
                .map(
                    |(
                        l @ Entry {
                            key,
                            short_name,
                            name,
                            category,
                            owner,
                            homepage_url,
                            notes,
                            spdx_license_key,
                            other_spdx_license_keys,
                            osi_license_key,
                            text_urls,
                            osi_url,
                            faq_url,
                            other_urls,
                            text,
                        },
                        ie @ IndexEntry {
                            license_key: _,
                            category: _,
                            spdx_license_key: _,
                            other_spdx_license_keys: _,
                            is_exception,
                            is_deprecated,
                            json,
                            yaml,
                            html,
                            license,
                        },
                    )| {
                        let category = LicenseGraphNode::mk_statement(category);
                        let mut statements = vec![category];

                        if *is_deprecated {
                            statements.push(LicenseGraphNode::mk_statement("is_deprecated"));
                        };
                        if *is_exception {
                            statements.push(LicenseGraphNode::mk_statement("is_exception"));
                        };
                        text.clone().map(|text| {
                            statements
                                .push(LicenseGraphNode::LicenseTextNode { license_text: text })
                        });
                        osi_url.clone().map(|text| {
                            statements.push(LicenseGraphNode::mk_statement("is_osi_approved"))
                        });
                        notes
                            .clone()
                            .map(|notes| statements.push(LicenseGraphNode::Note { text: notes }));

                        let names = l.clone().get_other_license_names();
                        log::debug!("{} -> {:?}", key, names);
                        LicenseGraphBuilderTask::AddEdge {
                            lefts: statements,
                            rights: Box::new(LicenseGraphBuilderTask::mk_aliases_task(
                                key.clone(),
                                names,
                            )),
                            edge: LicenseGraphEdge::AppliesTo,
                        }
                    },
                )
                .collect()
        }
    }
}

pub mod source_blueoakcouncil {
    use super::model::graph::*;
    use crate::model::core::LicenseName;

    use serde_derive::{Deserialize, Serialize};
    use std::collections::HashMap;
    use std::error::Error;
    use std::fs::File;
    use std::io::BufReader;

    #[derive(Debug, Serialize, Deserialize, Clone)]
    struct License {
        id: String,
        name: String,
        url: String,
    }

    fn add_license(lic: License) -> LicenseGraphBuilderTask {
        match lic {
            License { id, name, url } => {
                let url = LicenseGraphNode::mk_statement(&url);
                LicenseGraphBuilderTask::AddEdge {
                    lefts: vec![url],
                    rights: Box::new(LicenseGraphBuilderTask::mk_aliases_task(id, vec![name])),
                    edge: LicenseGraphEdge::AppliesTo,
                }
            }
        }
    }

    #[derive(Debug, Serialize, Deserialize, Clone)]
    struct CopyleftFamily {
        name: String,
        versions: Vec<License>,
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

    pub struct CopyleftListSource {}
    impl Source for CopyleftListSource {
        fn get_origin(&self) -> Origin<'static> {
            Origin::new_with_file("Blue Oak Council", "https://blueoakcouncil.org/")
        }

        fn get_tasks(&self) -> Vec<LicenseGraphBuilderTask> {
            let CopyleftList {
                version: list_version,
                families: families_per_kind,
            } = read_blueoakcouncil_copyleft_list()
                .expect("parsing of copyleft list should succeed");

            let from_families_per_kind = families_per_kind
                .iter()
                .map(|(kind, families)| {
                    let from_families = families
                        .iter()
                        .map(
                            |CopyleftFamily {
                                 name: family_name,
                                 versions,
                             }| {
                                let family_name = lic!(family_name);
                                let from_versions = versions
                                    .iter()
                                    .map(|l @ License { id, name, url }| {
                                        log::debug!(
                                            "{:?} -> {} -> {} , {}",
                                            kind,
                                            family_name,
                                            id,
                                            name
                                        );
                                        add_license(l.clone())
                                    })
                                    .collect();
                                LicenseGraphBuilderTask::AddEdge {
                                    lefts: vec![LicenseGraphNode::LicenseNameNode {
                                        license_name: family_name,
                                    }],
                                    rights: Box::new(LicenseGraphBuilderTask::JoinTasks {
                                        tasks: from_versions,
                                    }),
                                    edge: LicenseGraphEdge::Better,
                                }
                            },
                        )
                        .collect();
                    let kind = LicenseGraphNode::mk_statement(kind);
                    LicenseGraphBuilderTask::AddEdge {
                        lefts: vec![kind],
                        rights: Box::new(LicenseGraphBuilderTask::JoinTasks {
                            tasks: from_families,
                        }),
                        edge: LicenseGraphEdge::AppliesTo,
                    }
                })
                .collect();

            vec![LicenseGraphBuilderTask::AddEdge {
                lefts: vec![LicenseGraphNode::mk_statement("Copyleft")],
                rights: Box::new(LicenseGraphBuilderTask::JoinTasks {
                    tasks: from_families_per_kind,
                }),
                edge: LicenseGraphEdge::AppliesTo,
            }]
        }
    }

    #[derive(Debug, Serialize, Deserialize, Clone)]
    struct LicenseRating {
        name: String,
        notes: String,
        licenses: Vec<License>,
    }

    #[derive(Debug, Serialize, Deserialize, Clone)]
    struct LicenseList {
        version: String,
        ratings: Vec<LicenseRating>,
    }

    fn read_blueoakcouncil_license_list() -> Result<LicenseList, Box<dyn Error>> {
        let file = File::open("./data/blueoakcouncil/blue-oak-council-license-list.json")?;
        let reader = BufReader::new(file);
        let ll = serde_json::from_reader(reader)?;
        Ok(ll)
    }

    pub struct LicenseListSource {}
    impl Source for LicenseListSource {
        fn get_origin(&self) -> Origin<'static> {
            Origin::new_with_file("Blue Oak Council", "https://blueoakcouncil.org/")
        }

        fn get_tasks(&self) -> Vec<LicenseGraphBuilderTask> {
            let LicenseList {
                version: list_version,
                ratings,
            } = read_blueoakcouncil_license_list()
                .expect("parsing of copyleft list should succeed");

            let kind = LicenseGraphNode::mk_statement("Permissive");
            let from_list = ratings
                .iter()
                .map(
                    |LicenseRating {
                         name,
                         notes,
                         licenses,
                     }| {
                        let from_licenses =
                            licenses.iter().map(|l| add_license(l.clone())).collect();
                        let rating =
                            LicenseGraphNode::mk_statement(&format!("{}\n{}", name, notes));
                        LicenseGraphBuilderTask::AddEdge {
                            lefts: vec![rating],
                            rights: Box::new(LicenseGraphBuilderTask::JoinTasks {
                                tasks: from_licenses,
                            }),
                            edge: LicenseGraphEdge::AppliesTo,
                        }
                    },
                )
                .collect();
            vec![LicenseGraphBuilderTask::AddEdge {
                lefts: vec![kind],
                rights: Box::new(LicenseGraphBuilderTask::JoinTasks { tasks: from_list }),
                edge: LicenseGraphEdge::AppliesTo,
            }]
        }
    }
}
