use crate::model::*;

use serde_derive::{Deserialize, Serialize};
use std::collections::HashMap;
use std::error::Error;
use std::fs::File;
use std::io::BufReader;

#[derive(Debug, Serialize, Deserialize, Clone)]
struct License {
    id: String,
    #[serde(default)]
    identifiers: HashMap<String, Vec<String>>,
    name: String,
    #[serde(default)]
    tags: Vec<String>,
    #[serde(default)]
    uris: Vec<String>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
struct LicensesJson {
    licenses: HashMap<String, License>,
}

fn read_fsf_compatibility_checker_licenses_json() -> Result<LicensesJson, Box<dyn Error>> {
    let file = File::open("../data/wking-fsf-api/licenses-full.json")?;
    let reader = BufReader::new(file);
    let cl = serde_json::from_reader(reader)?;
    Ok(cl)
}

pub struct FsfSource {}
impl Source for FsfSource {
    fn get_origin(&self) -> Origin {
        Origin::new_with_url("FSF License Metadata", "https://github.com/wking/fsf-api")
    }

    fn get_tasks(&self) -> Vec<LicenseGraphBuilderTask> {
        let LicensesJson { licenses } = read_fsf_compatibility_checker_licenses_json()
            .expect("should be able to parse fsf json");
        licenses
            .iter()
            .map(
                |(
                    _,
                    license @ License {
                        id,
                        identifiers,
                        name,
                        tags,
                        uris,
                    },
                )| {
                    LicenseGraphBuilderTask::new1(LicenseGraphNode::license_name(id))
                        .edge(
                            LicenseGraphEdge::Same,
                            vec![
                                LicenseGraphNode::namespaced_license_name("fsf", id),
                                LicenseGraphNode::license_name(name),
                            ],
                        )
                        .edge1(
                            LicenseGraphEdge::AppliesTo,
                            LicenseGraphNode::Raw(format!("{:#?}", license)),
                        )
                        .edge(
                            LicenseGraphEdge::Same,
                            identifiers
                                .iter()
                                .flat_map(|(namespace, identifiers)| {
                                    identifiers
                                        .iter()
                                        .flat_map(|identifier| {
                                            vec![
                                                LicenseGraphNode::license_name(identifier),
                                                LicenseGraphNode::namespaced_license_name(
                                                    namespace, identifier,
                                                ),
                                            ]
                                        })
                                        .collect::<Vec<_>>()
                                })
                                .collect::<Vec<_>>(),
                        )
                        .edge_add(
                            LicenseGraphEdge::AppliesTo,
                            tags.iter()
                                .map(|tag| LicenseGraphNode::license_flag(tag))
                                .collect(),
                        )
                        .edge_add(
                            LicenseGraphEdge::AppliesTo,
                            LicenseGraphNode::vec(
                                uris.iter().map(|uri| LicenseGraphNode::url(uri)).collect(),
                            ),
                        )
                },
            )
            .collect()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::test_helper;

    #[test]
    fn tests_source() {
        test_helper::test_single_origin("source_fsf", &FsfSource {}, vec!["BSD-3-Clause"])
    }
}
