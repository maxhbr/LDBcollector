use crate::model::*;
use spdx::identifiers::{IMPRECISE_NAMES, LICENSES};

pub struct SpdxSource {}
impl Source for SpdxSource {
    fn get_origin(&self) -> Origin {
        Origin::new_with_url("SPDX", "https://spdx.org/licenses/")
    }

    fn get_tasks(&self) -> Vec<LicenseGraphBuilderTask> {
        LICENSES
            .into_iter()
            .map(|i @ (name, full_name, _)| {
                LicenseGraphBuilderTask::new1(LicenseGraphNode::namespaced_license_name("spdx", name))
                    .edge1(LicenseGraphEdge::Better, LicenseGraphNode::license_name(name))
                    .edge(
                        LicenseGraphEdge::AppliesTo,
                        vec![LicenseGraphNode::Raw(format!("{:#?}", i))],
                    )
                    .edge(
                        LicenseGraphEdge::Same,
                        vec![LicenseGraphNode::license_name(full_name)],
                    )
                    .edge_add(LicenseGraphEdge::AppliesTo, {
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
                            .filter_map(|(flag, flag_bool)|
                                if *flag_bool {
                                    if *flag == "Copyleft" {
                                        Option::Some(LicenseGraphNode::license_type(flag))
                                    } else {
                                        Option::Some(LicenseGraphNode::license_flag(flag))
                                    }
                                } else {
                                    Option::None
                                })
                            .collect()
                    })
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
                LicenseGraphBuilderTask::new1(LicenseGraphNode::license_name(&better)).edge(
                    LicenseGraphEdge::HintsTowards,
                    vec![LicenseGraphNode::license_name(&imprecise)],
                )
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
        test_helper::test_single_origin("source_spdx", &SpdxSource {}, vec!["MIT", "GPL-3.0-only"])
    }
}
