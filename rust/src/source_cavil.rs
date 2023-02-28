use crate::model::*;
use std::fs;
use std::io::{self, prelude::*, BufReader};

pub struct CavilSource {}
impl Source for CavilSource {
    fn get_origin(&self) -> Origin {
        Origin::new_with_url("cavil", "https://github.com/openSUSE/cavil")
    }

    fn get_tasks(&self) -> Vec<LicenseGraphBuilderTask> {
        let path = "../data/openSUSE-cavil/lib/Cavil/resources/license_changes.txt";
        log::debug!("read: {:?}", &path);
        let contents = fs::read_to_string(&path).expect("Should have been able to read YAML");
        log::debug!("parse: {:?}", &path);

        BufReader::new(contents.as_bytes())
            .lines()
            .skip(1)
            .map(|line| {
                let line = line.unwrap();
                let mut pair = line.split("\t");
                let id = pair.next().unwrap();
                let alias = pair.next().unwrap();

                LicenseGraphBuilderTask::new1(LicenseGraphNode::license_name(id)).edge(
                    LicenseGraphEdge::HintsTowards,
                    vec![LicenseGraphNode::license_name(alias)],
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
        test_helper::test_single_origin("source_cavil", &CavilSource {}, vec!["BSD-3-Clause"])
    }
}
