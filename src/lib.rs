pub mod model;


#[macro_export]
macro_rules! lic {
    ($l:tt) => {
        $crate::model::core::LicenseName::new($l)
    };
}

pub mod source_spdx {
    use spdx::*;
    use spdx::identifiers::LICENSES;
    use crate::model::core::LicenseName;

    use super::model::graph::*;

    fn licenses_satisfying_flag(flag_fn: impl Fn(LicenseId) -> bool) -> Vec<LicenseName> {
        LICENSES
            .into_iter()
            .filter(|(name, _, _)| {
                flag_fn(spdx::license_id(name).unwrap())
            })
            .map(|(name, _, _)| {
                lic!(name)
            })
            .collect()
    }

    pub fn add_spdx(s: LicenseGraph) -> LicenseGraph {
        static ORIGIN: &'static Origin = &Origin::new_with_file("SPDX", "https://spdx.org/licenses/", Option::None);
        LICENSES
            .into_iter()
            .fold(s, |acc: LicenseGraph, i@(name, full_name, _)| {
                acc.add_aliases(vec!(lic!(full_name), lic!(name)), ORIGIN)
                    .add_relational_fact(
                        LicenseGraphNode::mk_json_statement(i),
                        vec!(lic!(full_name), lic!(name)),
                        ORIGIN)
                    // .add_relational_fact(
                    //     LicenseGraphNode::mk_statement(
                    //         license_id(name).unwrap().text()
                    //     ),
                    //     vec!(lic!(name)),
                    //     ORIGIN)
            })
            .add_relational_fact( LicenseGraphNode::mk_statement("is_copyleft"), licenses_satisfying_flag(|l| l.is_copyleft()), ORIGIN)
            .add_relational_fact( LicenseGraphNode::mk_statement("is_deprecated"), licenses_satisfying_flag(|l| l.is_deprecated()), ORIGIN)
            .add_relational_fact( LicenseGraphNode::mk_statement("is_fsf_free_libre"), licenses_satisfying_flag(|l| l.is_fsf_free_libre()), ORIGIN)
            .add_relational_fact( LicenseGraphNode::mk_statement("is_gnu"), licenses_satisfying_flag(|l| l.is_gnu()), ORIGIN)
            .add_relational_fact( LicenseGraphNode::mk_statement("is_osi_approved"), licenses_satisfying_flag(|l| l.is_osi_approved()), ORIGIN)
    }
}

pub mod scancode {
}