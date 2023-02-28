use crate::model::*;

use itertools::join;
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
            let url = LicenseGraphNode::url(&url);
            LicenseGraphBuilderTask::new1(LicenseGraphNode::license_name(&id))
                .edge_left(
                    LicenseGraphEdge::Same,
                    vec![LicenseGraphNode::license_name(&name)],
                )
                .edge_left(LicenseGraphEdge::AppliesTo, vec![url])
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
    let file = File::open("../data/blueoakcouncil/blue-oak-council-copyleft-list.json")?;
    let reader = BufReader::new(file);
    let cl = serde_json::from_reader(reader)?;
    Ok(cl)
}

pub struct CopyleftListSource {}
impl Source for CopyleftListSource {
    fn get_origin(&self) -> Origin {
        Origin::new_with_url("Blue Oak Council", "https://blueoakcouncil.org/")
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
                            LicenseGraphBuilderTask::join(from_versions).edge(
                                LicenseGraphEdge::Better,
                                vec![LicenseGraphNode::license_name(&family_name)],
                            )
                        },
                    )
                    .collect();
                let kind = LicenseGraphNode::license_type(kind);
                LicenseGraphBuilderTask::join(from_families)
                    .edge(LicenseGraphEdge::AppliesTo, vec![kind])
            })
            .collect();

        vec![LicenseGraphBuilderTask::join(from_families_per_kind).edge(
            LicenseGraphEdge::AppliesTo,
            vec![LicenseGraphNode::license_type("Copyleft")],
        )]
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
    let file = File::open("../data/blueoakcouncil/blue-oak-council-license-list.json")?;
    let reader = BufReader::new(file);
    let ll = serde_json::from_reader(reader)?;
    Ok(ll)
}

pub struct LicenseListSource {}
impl Source for LicenseListSource {
    fn get_origin(&self) -> Origin {
        Origin::new_with_url("Blue Oak Council", "https://blueoakcouncil.org/")
    }

    fn get_tasks(&self) -> Vec<LicenseGraphBuilderTask> {
        let LicenseList {
            version: list_version,
            ratings,
        } = read_blueoakcouncil_license_list().expect("parsing of copyleft list should succeed");

        let kind = LicenseGraphNode::license_type("Permissive");
        let task = LicenseGraphBuilderTask::join(
            ratings
                .iter()
                .map(
                    |LicenseRating {
                         name,
                         notes,
                         licenses,
                     }| {
                        let from_licenses = LicenseGraphBuilderTask::join(
                            licenses.iter().map(|l| add_license(l.clone())).collect(),
                        );
                        let rating = LicenseGraphNode::Data(LicenseData::LicenseType(
                            LicenseType::Permissive(Option::Some(name.clone())),
                        ));
                        let rating_note = LicenseGraphNode::note(notes);

                        from_licenses
                            .edge(LicenseGraphEdge::AppliesTo, vec![rating])
                            .edge_left(LicenseGraphEdge::AppliesTo, vec![rating_note])
                    },
                )
                .collect(),
        )
        .edge(LicenseGraphEdge::AppliesTo, vec![kind]);
        vec![task]
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
