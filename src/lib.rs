pub mod model;

#[macro_export]
macro_rules! lic {
    ($l:tt) => {
        $crate::model::core::LicenseName::new($l)
    };
}

pub mod source_spdx {
    use super::model::graph::*;
    use crate::model::core::LicenseName;
    use spdx::identifiers::LICENSES;
    use spdx::*;

    fn licenses_satisfying_flag<'a>(flag_fn: impl Fn(LicenseId) -> bool) -> Vec<LicenseName<'a>> {
        LICENSES
            .into_iter()
            .filter(|(name, _, _)| flag_fn(spdx::license_id(name).unwrap()))
            .map(|(name, _, _)| lic!(name))
            .collect()
    }

    pub fn add_spdx(s: LicenseGraph) -> LicenseGraph {
        static ORIGIN: &'static Origin =
            &Origin::new_with_file("SPDX", "https://spdx.org/licenses/", Option::None);
        LICENSES
            .into_iter()
            .fold(s, |acc: LicenseGraph, i @ (name, full_name, _)| {
                acc.add_aliases(vec![lic!(full_name), lic!(name)], ORIGIN)
                    .add_relational_fact(
                        LicenseGraphNode::mk_json_statement(i),
                        vec![lic!(full_name), lic!(name)],
                        ORIGIN,
                    )
                // .add_relational_fact(
                //     LicenseGraphNode::mk_statement(
                //         license_id(name).unwrap().text()
                //     ),
                //     vec!(lic!(name)),
                //     ORIGIN)
            })
            .add_relational_fact(
                LicenseGraphNode::mk_statement("is_copyleft"),
                licenses_satisfying_flag(|l| l.is_copyleft()),
                ORIGIN,
            )
            .add_relational_fact(
                LicenseGraphNode::mk_statement("is_deprecated"),
                licenses_satisfying_flag(|l| l.is_deprecated()),
                ORIGIN,
            )
            .add_relational_fact(
                LicenseGraphNode::mk_statement("is_fsf_free_libre"),
                licenses_satisfying_flag(|l| l.is_fsf_free_libre()),
                ORIGIN,
            )
            .add_relational_fact(
                LicenseGraphNode::mk_statement("is_gnu"),
                licenses_satisfying_flag(|l| l.is_gnu()),
                ORIGIN,
            )
            .add_relational_fact(
                LicenseGraphNode::mk_statement("is_osi_approved"),
                licenses_satisfying_flag(|l| l.is_osi_approved()),
                ORIGIN,
            )
    }
}

pub mod source_osadl {
    use crate::model::core::LicenseName;
    use std::ffi::OsStr;
    use std::fs;
    use std::path::Path;

    use super::model::graph::*;

    fn license_from_osadl_checklist<'a>(checklist: &'a Path) -> Option<LicenseName<'a>> {
        checklist
            // .with_extension("")
            .file_name()
            .and_then(|license_name| license_name.to_str())
            .map(|license_name| lic!(license_name))
    }

    pub fn add_osadl_checklist(s: LicenseGraph) -> LicenseGraph {
        static ORIGIN: &'static Origin = &Origin::new_with_file(
            "OSADL",
            "https://www.osadl.org/Access-to-raw-data.oss-compliance-raw-data-access.0.html",
            Option::None,
        );

        fs::read_dir("./data/OSADL-checklists/")
            .unwrap()
            .filter_map(|result| {
                result
                    .ok()
                    .map(|dir_entry| dir_entry.path())
                    .filter(|path| match path.extension() {
                        Option::Some(extension) => extension == OsStr::new("osadl"),
                        _ => false,
                    })
            })
            .fold(s, |acc: LicenseGraph, checklist| {
                let contents = fs::read_to_string(&checklist)
                    .expect("Should have been able to read OSADL rule");
                if let Some(lic) = license_from_osadl_checklist(checklist.as_path()) {
                    acc.add_relational_fact(
                        LicenseGraphNode::mk_statement(&contents),
                        vec!(lic),
                        ORIGIN,
                    )
                } else {
                    acc
                }
            })
    }
}

pub mod source_scancode {}
