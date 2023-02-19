use super::model::*;
use serde_derive::{Deserialize, Serialize};
use std::ffi::OsStr;
use std::fs;

use std::fmt;

use serde::de::{self, value, Deserialize, Deserializer, SeqAccess, Visitor};

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct OslcHandbookTerm {
    r#type: String,
    description: String,
    use_case: Option<Vec<String>>,
    compliance_notes: Option<String>,
    seeAlso: Option<Vec<String>>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct OslcHandbookEntry {
    name: String,
    #[serde(deserialize_with = "string_or_vec")]
    licenseId: Vec<String>,
    notes: Option<String>,
    terms: Vec<OslcHandbookTerm>,
}

fn string_or_vec<'de, D>(deserializer: D) -> Result<Vec<String>, D::Error>
where
    D: Deserializer<'de>,
{
    struct StringOrVec;

    impl<'de> Visitor<'de> for StringOrVec {
        type Value = Vec<String>;

        fn expecting(&self, formatter: &mut fmt::Formatter) -> fmt::Result {
            formatter.write_str("string or list of strings")
        }

        fn visit_str<E>(self, s: &str) -> Result<Self::Value, E>
        where
            E: de::Error,
        {
            Ok(vec![s.to_owned()])
        }

        fn visit_seq<S>(self, seq: S) -> Result<Self::Value, S::Error>
        where
            S: SeqAccess<'de>,
        {
            Deserialize::deserialize(value::SeqAccessDeserializer::new(seq))
        }
    }

    deserializer.deserialize_any(StringOrVec)
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct OslcHandbook(Vec<OslcHandbookEntry>);

pub struct OslcHandbookSource {}
impl Source for OslcHandbookSource {
    fn get_origin(&self) -> Origin {
        Origin::new_with_url("OSLC Handbook", "https://github.com/finos/OSLC-handbook")
    }

    fn get_tasks(&self) -> Vec<LicenseGraphBuilderTask> {
        fs::read_dir("./data/finos-OSLC-handbook/src/")
            .unwrap()
            .filter_map(|result| {
                result
                    .ok()
                    .map(|dir_entry| dir_entry.path())
                    .filter(|path| match path.extension() {
                        Option::Some(extension) => extension == OsStr::new("yaml"),
                        _ => false,
                    })
            })
            .filter_map(|path| {
                log::debug!("read: {:?}", &path);
                let contents =
                    fs::read_to_string(&path).expect("Should have been able to read YAML");
                log::debug!("parse: {:?}", &path);
                serde_yaml::from_str(&contents)
                    .ok()
                    .map(|handbooks: OslcHandbook| (contents, handbooks))
            })
            .map(|(contents, OslcHandbook(handbooks))| {
                let rights = handbooks
                    .iter()
                    .map(|handbook| {
                        let licenseId = &handbook.licenseId;
                        let name = &handbook.name;
                        let notes : Vec<LicenseGraphNode> = handbook.notes
                           .iter()
                           .map(|notes| LicenseGraphNode::note(notes))
                           .collect();
                        let terms = &handbook.terms;

                        log::debug!("{}", name);

                        LicenseGraphBuilderTask::AddEdgeUnion {
                            lefts: notes,
                            rights: Box::new(LicenseGraphBuilderTask::AddEdgeLeft {
                                lefts: vec![LicenseGraphNode::license_name(name)],
                                rights: Box::new(LicenseGraphBuilderTask::AddNodes {
                                    nodes: licenseId
                                        .iter()
                                        .map(|licenseId| LicenseGraphNode::license_name(licenseId))
                                        .collect(),
                                }),
                                edge: LicenseGraphEdge::Same,
                            }),
                            edge: LicenseGraphEdge::AppliesTo,
                        }
                    })
                    .collect();
                LicenseGraphBuilderTask::AddEdge {
                    lefts: vec![LicenseGraphNode::StatementRule {
                        statement_content: contents,
                    }],
                    rights: Box::new(LicenseGraphBuilderTask::JoinTasks { tasks: rights }),
                    edge: LicenseGraphEdge::AppliesTo,
                }
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
            "source_oslc-handbook",
            &OslcHandbookSource {},
            vec!["BSD-3-Clause"],
        )
    }
}
