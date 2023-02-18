use crate::model::*;

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
            LicenseGraphBuilderTask::AddEdgeLeft {
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
    fn get_origin(&self) -> Origin {
        Origin::new_with_file("Blue Oak Council", "https://blueoakcouncil.org/")
    }

    fn get_tasks(&self) -> Vec<LicenseGraphBuilderTask> {
        let CopyleftList {
            version: list_version,
            families: families_per_kind,
        } = read_blueoakcouncil_copyleft_list().expect("parsing of copyleft list should succeed");

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
                                .map(|l @ License { id, name, url: _ }| {
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
    fn get_origin(&self) -> Origin {
        Origin::new_with_file("Blue Oak Council", "https://blueoakcouncil.org/")
    }

    fn get_tasks(&self) -> Vec<LicenseGraphBuilderTask> {
        let LicenseList {
            version: list_version,
            ratings,
        } = read_blueoakcouncil_license_list().expect("parsing of copyleft list should succeed");

        let kind = LicenseGraphNode::mk_statement("Permissive");
        let from_list = ratings
            .iter()
            .map(
                |LicenseRating {
                     name,
                     notes,
                     licenses,
                 }| {
                    let from_licenses = licenses.iter().map(|l| add_license(l.clone())).collect();
                    let rating = LicenseGraphNode::mk_statement(name);
                    let rating_note = LicenseGraphNode::Note {
                        text: notes.clone(),
                    };
                    LicenseGraphBuilderTask::AddEdgeLeft {
                        lefts: vec![rating_note],
                        rights: Box::new(LicenseGraphBuilderTask::AddEdge {
                            lefts: vec![rating],
                            rights: Box::new(LicenseGraphBuilderTask::JoinTasks {
                                tasks: from_licenses,
                            }),
                            edge: LicenseGraphEdge::AppliesTo,
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

#[cfg(test)]
mod tests {
    use super::*;
    use crate::test_helper;

    #[test]
    fn tests_copyleft_source() {
        test_helper::test_single_origin(
            "source_blueoakcouncil/copyleft",
            &CopyleftListSource {},
            vec!["GPL-3.0-only"],
        )
    }

    #[test]
    fn tests_license_source() {
        test_helper::test_single_origin(
            "source_blueoakcouncil/license",
            &LicenseListSource {},
            vec!["MIT"],
        )
    }
}
