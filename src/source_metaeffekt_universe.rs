use super::model::*;
use glob::glob;
use serde_derive::{Deserialize, Serialize};
use std::fs;

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct MetaeffektLicense {
    canonicalName: String,
    category: String,
    shortName: String,
    spdxIdentifier: String,
    openCoDEStatus: String,
    alternativeNames: Vec<String>,
    otherIds: Vec<String>,
}

pub struct MetaeffektUniverseSource {}
impl Source for MetaeffektUniverseSource {
    fn get_origin(&self) -> Origin {
        Origin::new_with_url("okfn licenses", "https://github.com/okfn/")
    }

    fn get_tasks(&self) -> Vec<LicenseGraphBuilderTask> {
        let yamls = glob(
            "./data/org-metaeffekt-metaeffekt-universe/src/main/resources/ae-universe/**/*.yaml",
        )
        .expect("should be able to glob the metaeffekt universe");
        yamls
            .filter_map(|entry| {
                if let Ok(json) = entry {
                    log::debug!("read: {:?}", &json);
                    let contents =
                        fs::read_to_string(&json).expect("Should have been able to read YAML");
                    log::debug!("parse: {:?}", &json);
                    serde_yaml::from_str(&contents).ok()
                } else {
                    Option::None {}
                }
            })
            .map(
                |MetaeffektLicense {
                     canonicalName,
                     category,
                     shortName,
                     spdxIdentifier,
                     openCoDEStatus,
                     alternativeNames,
                     otherIds,
                 }| {
                    let nodes_from_otherIds: Vec<_> = otherIds
                        .iter()
                        .map(|otherId| LicenseGraphNode::license_name(otherId))
                        .collect();
                    let nodes_from_alternativeNames: Vec<_> = alternativeNames
                        .iter()
                        .map(|alternativeName| LicenseGraphNode::license_name(alternativeName))
                        .collect();
                    LicenseGraphBuilderTask::AddEdge {
                        lefts: [
                            vec![
                                LicenseGraphNode::license_name(&shortName),
                                LicenseGraphNode::license_name(&spdxIdentifier),
                            ],
                            nodes_from_alternativeNames,
                            nodes_from_otherIds,
                        ]
                        .concat(),
                        rights: Box::new(LicenseGraphBuilderTask::AddNodes {
                            nodes: vec![LicenseGraphNode::license_name(&canonicalName)],
                        }),
                        edge: LicenseGraphEdge::Same,
                    }
                },
            )
            .collect()
    }
}
