use super::model::*;
use std::ffi::OsStr;
use std::fs;

pub struct OsadlSource {}
impl Source for OsadlSource {
    fn get_origin(&self) -> Origin {
        Origin::new_with_url(
            "OSADL",
            "https://www.osadl.org/Access-to-raw-data.oss-compliance-raw-data-access.0.html",
        )
    }

    fn get_tasks(&self) -> Vec<LicenseGraphBuilderTask> {
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
            .map(|checklist| {
                let contents = fs::read_to_string(&checklist)
                    .expect("Should have been able to read OSADL rule");
                if let Some(lic_str) = checklist
                    .with_extension("")
                    .file_name()
                    .and_then(|license_name| license_name.to_str())
                {
                    log::debug!("{}", lic_str);
                    LicenseGraphBuilderTask::new1(LicenseGraphNode::license_name(lic_str)).edge(
                        LicenseGraphEdge::AppliesTo,
                        vec![LicenseGraphNode::StatementRule {
                            statement_content: contents,
                        }],
                    )
                } else {
                    LicenseGraphBuilderTask::Noop {}
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
        test_helper::test_single_origin("source_osadl", &OsadlSource {}, vec!["BSD-3-Clause"])
    }
}
