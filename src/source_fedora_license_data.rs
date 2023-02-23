use super::model::*;
use serde_derive::{Deserialize, Serialize};
use std::ffi::OsStr;
use std::fs;

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct LicenseInfo {
    expression: String,
    status: Vec<String>,
    usage: Option<String>,
    url: Option<String>,
    text: Option<String>,
    #[serde(alias = "scancode-key")]
    scancode_key: Option<String>,
}
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
pub struct FedoraInfo {
    #[serde(alias = "legacy-name")]
    legacy_name: Option<Vec<String>>,
    #[serde(alias = "legacy-abbreviation")]
    legacy_abbreviation: Option<Vec<String>>,
    notes: Option<String>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct FedoraLicenseData {
    license: LicenseInfo,
    fedora: Option<FedoraInfo>,
}

pub struct FedoraLicenseDataSource {}
impl Source for FedoraLicenseDataSource {
    fn get_origin(&self) -> Origin {
        Origin::new_with_url(
            "Fedora License Data Project",
            "https://gitlab.com/fedora/legal/fedora-license-data",
        )
    }

    fn get_tasks(&self) -> Vec<LicenseGraphBuilderTask> {
        fs::read_dir("./data/fedora-legal-fedora-license-data/data")
            .unwrap()
            .filter_map(|result| {
                result
                    .ok()
                    .map(|dir_entry| dir_entry.path())
                    .filter(|path| match path.extension() {
                        Option::Some(extension) => extension == OsStr::new("toml"),
                        _ => false,
                    })
            })
            .filter_map(|file| {
                let contents =
                    fs::read_to_string(&file).expect("Should have been able to read TOML");
                if let Some(lic_str) = &file
                    .with_extension("")
                    .file_name()
                    .and_then(|license_name| license_name.to_str())
                {
                    Some((String::from(*lic_str), contents))
                } else {
                    log::error!("failed to find lic_str from path {:?}", file);
                    None
                }
            })
            .map(|(lic_str, contents)| {
                let parsed: FedoraLicenseData = toml::from_str(&contents).unwrap();
                (lic_str, contents, parsed)
            })
            .map(
                |(
                    lic_str,
                    contents,
                    FedoraLicenseData {
                        license:
                            LicenseInfo {
                                expression,
                                status,
                                usage,
                                url,
                                text,
                                scancode_key,
                            },
                        fedora,
                    },
                )| {
                    log::debug!("{}", lic_str);

                    let FedoraInfo {
                        legacy_name,
                        legacy_abbreviation,
                        notes,
                    } = fedora.unwrap_or_default();
                    let lic_str_nodes = vec![LicenseGraphNode::license_name(&lic_str)];
                    let legacy_name_nodes: Vec<_> = [
                        legacy_name.unwrap_or_default(),
                        legacy_abbreviation.unwrap_or_default(),
                    ]
                    .concat()
                    .iter()
                    .map(|legacy_name| LicenseGraphNode::license_name(legacy_name))
                    .collect();
                    let lic_str_task = Box::new(LicenseGraphBuilderTask::AddEdgeLeft {
                        lefts: legacy_name_nodes,
                        rights: Box::new(if expression != lic_str {
                            LicenseGraphBuilderTask::AddEdge {
                                lefts: lic_str_nodes,
                                rights: Box::new(LicenseGraphBuilderTask::AddNodes {
                                    nodes: vec![LicenseGraphNode::license_name(&expression)],
                                }),
                                edge: LicenseGraphEdge::Better,
                            }
                        } else {
                            LicenseGraphBuilderTask::AddNodes {
                                nodes: lic_str_nodes,
                            }
                        }),
                        edge: LicenseGraphEdge::Better,
                    });

                    let text_nodes: Vec<_> = text
                        .iter()
                        .map(|text| LicenseGraphNode::license_text(text))
                        .collect();

                    let url_nodes: Vec<_> = url
                        .iter()
                        .flat_map(|text| text.lines().map(|url| LicenseGraphNode::url(url)))
                        .collect();

                    let usage_nodes: Vec<_> = usage
                        .iter()
                        .map(|usage| LicenseGraphNode::Note(format!("Fedora usage: {}", usage)))
                        .collect();

                    let notes_nodes: Vec<_> = notes
                        .iter()
                        .map(|notes| LicenseGraphNode::Note(format!("Fedora notes: {}", notes)))
                        .collect();

                    LicenseGraphBuilderTask::AddEdge {
                        lefts: [
                            vec![
                                LicenseGraphNode::StatementRule {
                                    statement_content: contents,
                                },
                                LicenseGraphNode::license_rating(&format!(
                                    "Fedora Rating: {:?}",
                                    status
                                )),
                            ],
                            text_nodes,
                            url_nodes,
                            usage_nodes,
                            notes_nodes,
                        ]
                        .concat(),
                        rights: lic_str_task,
                        edge: LicenseGraphEdge::AppliesTo,
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
            "source_fedora_license_data",
            &FedoraLicenseDataSource {},
            vec!["BSD-3-Clause"],
        )
    }
}
