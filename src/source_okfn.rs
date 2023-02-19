use super::model::*;
use serde_derive::{Deserialize, Serialize};
use std::ffi::OsStr;
use std::fs;

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct OkfnLicense {
    domain_content: bool,
    domain_data: bool,
    domain_software: bool,
    family: Option<String>,
    id: String,
    legacy_ids: Option<Vec<String>>,
    od_conformance: String,
    osd_conformance: String,
    maintainer: Option<String>,
    status: String,
    title: String,
    url: String,
}

pub struct OkfnSource {}
impl Source for OkfnSource {
    fn get_origin(&self) -> Origin {
        Origin::new_with_url("okfn licenses", "https://github.com/okfn/")
    }

    fn get_tasks(&self) -> Vec<LicenseGraphBuilderTask> {
        fs::read_dir("./data/okfn-licenses/licenses/")
            .unwrap()
            .filter_map(|result| {
                result
                    .ok()
                    .map(|dir_entry| dir_entry.path())
                    .filter(|path| match path.extension() {
                        Option::Some(extension) => extension == OsStr::new("json"),
                        _ => false,
                    })
            })
            .map(|path| {
                log::debug!("read: {:?}", &path);
                let contents =
                    fs::read_to_string(&path).expect("Should have been able to read JSON");
                log::debug!("parse: {:?}", &path);
                let license: OkfnLicense =
                    serde_yaml::from_str(&contents).expect("Should have been able to parse JSON");
                license
            })
            .map(
                |OkfnLicense {
                     domain_content,
                     domain_data,
                     domain_software,
                     family,
                     id,
                     legacy_ids,
                     od_conformance,
                     osd_conformance,
                     maintainer,
                     status,
                     title,
                     url,
                 }| {
                    let legacy_ids = legacy_ids.unwrap_or(vec![]);
                    LicenseGraphBuilderTask::AddEdge {
                        lefts: legacy_ids
                            .iter()
                            .map(|id| LicenseGraphNode::license_name(id))
                            .collect(),
                        rights: Box::new(LicenseGraphBuilderTask::AddEdgeLeft {
                            lefts: vec![LicenseGraphNode::url(&url)],
                            rights: Box::new(LicenseGraphBuilderTask::AddNodes {
                                nodes: vec![id, title]
                                    .iter()
                                    .map(|license_name| LicenseGraphNode::license_name(license_name))
                                    .collect(),
                            }),
                            edge: LicenseGraphEdge::AppliesTo,
                        }),
                        edge: LicenseGraphEdge::HintsTowards,
                    }
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
        test_helper::test_single_origin(
            "source_oslc-handbook",
            &OkfnSource {},
            vec!["BSD-3-Clause"],
        )
    }
}
