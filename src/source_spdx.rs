use crate::model::core::LicenseName;
use crate::model::graph::*;
use crate::model::*;
use spdx::identifiers::{IMPRECISE_NAMES, LICENSES};
use spdx::*;

pub struct SpdxSource {}
impl Source for SpdxSource {
    fn get_origin(&self) -> Origin {
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
    fn get_origin(&self) -> Origin {
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

#[cfg(test)]
mod tests {
    use super::*;
    use crate::model::*;

    #[test]
    fn tests_source() {
        test_helper::test_single_origin("source_spdx", &SpdxSource {})
    }
}
