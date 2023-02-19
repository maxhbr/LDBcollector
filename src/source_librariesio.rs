use crate::model::*;

use serde_derive::{Deserialize, Serialize};
use std::collections::HashMap;
use std::error::Error;
use std::fs::File;
use std::io::BufReader;

#[derive(Debug, Serialize, Deserialize, Clone)]
struct LicensesJson(HashMap<String, Vec<String>>);

fn read_librariesio_compatibility_checker_licenses_json() -> Result<LicensesJson, Box<dyn Error>> {
    let file = File::open("./data/librariesio-license-compatibility/lib/license/licenses.json")?;
    let reader = BufReader::new(file);
    let cl = serde_json::from_reader(reader)?;
    Ok(cl)
}

pub struct LibrariesioSource {}
impl Source for LibrariesioSource {
    fn get_origin(&self) -> Origin {
        Origin::new_with_url(
            "librariesio License::Compatibility",
            "https://github.com/librariesio/license-compatibility",
        )
    }

    fn get_tasks(&self) -> Vec<LicenseGraphBuilderTask> {
        let LicensesJson(map) = read_librariesio_compatibility_checker_licenses_json()
            .expect("should be able to parse librariesio json");
        map.iter()
            .map(|(ty, licenses)| LicenseGraphBuilderTask::AddEdge {
                lefts: vec![LicenseGraphNode::Statement {
                    statement_content: ty.clone(),
                }],
                rights: Box::new(LicenseGraphBuilderTask::AddNodes {
                    nodes: licenses
                        .iter()
                        .map(|license| LicenseGraphNode::LicenseNameNode {
                            license_name: lic!(license),
                        })
                        .collect(),
                }),
                edge: LicenseGraphEdge::AppliesTo,
            })
            .collect()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::test_helper;

    #[test]
    fn tests_source() {
        test_helper::test_single_origin(
            "source_librariesio",
            &LibrariesioSource {},
            vec!["BSD-3-Clause"],
        )
    }
}
