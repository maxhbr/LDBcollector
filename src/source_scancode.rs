use crate::model::graph::*;

use itertools::Itertools;
use serde_derive::{Deserialize, Serialize};
use std::error::Error;
use std::fs::File;
use std::io::BufReader;

static BASEPATH: &'static str = "./data/nexB-scancode-licensedb/docs/";

#[derive(Debug, Serialize, Deserialize, Clone)]
struct IndexEntry {
    license_key: String,
    category: String,
    spdx_license_key: Option<String>,
    other_spdx_license_keys: Vec<String>,
    is_exception: bool,
    is_deprecated: bool,
    json: String,
    yaml: String,
    html: String,
    license: String,
}
#[derive(Debug, Serialize, Deserialize, Clone)]
struct Entry {
    key: String,
    short_name: String,
    name: String,
    category: String,
    owner: String,
    homepage_url: Option<String>,
    notes: Option<String>,
    spdx_license_key: Option<String>,
    other_spdx_license_keys: Option<Vec<String>>,
    osi_license_key: Option<String>,
    text_urls: Option<Vec<String>>,
    osi_url: Option<String>,
    faq_url: Option<String>,
    other_urls: Option<Vec<String>>,
    // ignorable_copyrights: Option<Vec<String>>,
    // ignorable_holders: Option<Vec<String>>,
    // ignorable_urls: Option<Vec<String>>,
    text: Option<String>,
}
impl Entry {
    fn get_other_license_names(self) -> Vec<String> {
        let mut names = vec![];
        match self {
            Entry {
                key,
                short_name,
                name,
                category: _,
                owner: _,
                homepage_url: _,
                notes: _,
                spdx_license_key,
                other_spdx_license_keys: _,
                osi_license_key,
                text_urls: _,
                osi_url: _,
                faq_url: _,
                other_urls: _,
                text: _,
            } => {
                spdx_license_key.map(|spdx_license_key| names.push(spdx_license_key));
                names.push(short_name);
                names.push(name);

                // TODO
                // other_spdx_license_keys.map(|other_spdx_license_keys|
                //     other_spdx_license_keys
                //        .iter()
                //        .map(|other_spdx_license_key| names.push(other_spdx_license_key))
                // );
                osi_license_key.map(|osi_license_key| names.push(osi_license_key));
            }
        }
        names.into_iter().unique().collect()
    }
    fn get_urls(self) -> Vec<String> {
        let mut urls = vec![];
        match self {
            Entry {
                key: _,
                short_name: _,
                name: _,
                category: _,
                owner: _,
                homepage_url,
                notes: _,
                spdx_license_key: _,
                other_spdx_license_keys: _,
                osi_license_key: _,
                text_urls: _,
                osi_url,
                faq_url,
                other_urls: _,
                text: _,
            } => {
                homepage_url.map(|url| urls.push(url));
                osi_url.map(|url| urls.push(url));
                faq_url.map(|url| urls.push(url));
                // TODO
                // other_urls,
                // TODO
                // text_urls,
            }
        }
        urls
    }
}

fn read_index() -> Result<Vec<IndexEntry>, Box<dyn Error>> {
    let file = File::open(format!("{}index.json", BASEPATH))?;
    let reader = BufReader::new(file);
    let index = serde_json::from_reader(reader)?;
    Ok(index)
}

fn read_licenses() -> Result<Vec<(Entry, IndexEntry)>, Box<dyn Error>> {
    let index = read_index()?;
    index
        .iter()
        .map(
            |ie @ IndexEntry {
                 license_key,
                 category,
                 spdx_license_key,
                 other_spdx_license_keys,
                 is_exception,
                 is_deprecated,
                 json,
                 yaml,
                 html,
                 license,
             }| {
                log::debug!("... READ {}", json);
                let file = File::open(format!("{}{}", BASEPATH, json))?;
                let reader = BufReader::new(file);
                let entry = serde_json::from_reader(reader)?;
                Ok((entry, ie.clone()))
            },
        )
        .collect()
}

pub struct ScancodeSource {}
impl Source for ScancodeSource {
    fn get_origin(&self) -> Origin<'static> {
        Origin::new_with_file(
            "Scancode licensedb",
            "https://scancode-licensedb.aboutcode.org/",
        )
    }

    fn get_tasks(&self) -> Vec<LicenseGraphBuilderTask> {
        let licenses = read_licenses().expect("Parsing of scancode licenses should work");
        licenses
            .iter()
            .map(
                |(
                    l @ Entry {
                        key,
                        short_name,
                        name,
                        category,
                        owner,
                        homepage_url,
                        notes,
                        spdx_license_key,
                        other_spdx_license_keys,
                        osi_license_key,
                        text_urls,
                        osi_url,
                        faq_url,
                        other_urls,
                        text,
                    },
                    ie @ IndexEntry {
                        license_key: _,
                        category: _,
                        spdx_license_key: _,
                        other_spdx_license_keys: _,
                        is_exception,
                        is_deprecated,
                        json,
                        yaml,
                        html,
                        license,
                    },
                )| {
                    let category = LicenseGraphNode::mk_statement(category);
                    let mut statements = vec![category];

                    if *is_deprecated {
                        statements.push(LicenseGraphNode::mk_statement("is_deprecated"));
                    };
                    if *is_exception {
                        statements.push(LicenseGraphNode::mk_statement("is_exception"));
                    };
                    text.clone().map(|text| {
                        statements.push(LicenseGraphNode::LicenseTextNode { license_text: text })
                    });
                    osi_url.clone().map(|text| {
                        statements.push(LicenseGraphNode::mk_statement("is_osi_approved"))
                    });
                    notes
                        .clone()
                        .map(|notes| statements.push(LicenseGraphNode::Note { text: notes }));

                    let names = l.clone().get_other_license_names();
                    log::debug!("{} -> {:?}", key, names);
                    LicenseGraphBuilderTask::AddEdge {
                        lefts: statements,
                        rights: Box::new(LicenseGraphBuilderTask::mk_aliases_task(
                            key.clone(),
                            names,
                        )),
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
    use crate::model::*;

    #[test]
    fn tests_source() {
        test_helper::test_single_origin("source_scancode", &ScancodeSource {})
    }
}
