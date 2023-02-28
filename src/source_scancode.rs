use crate::model::*;

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
                other_urls,
                text: _,
            } => {
                homepage_url.map(|url| urls.push(url));
                osi_url.map(|url| urls.push(url));
                faq_url.map(|url| urls.push(url));
                other_urls
                    .unwrap_or(vec![])
                    .iter()
                    .for_each(|other_url| urls.push(other_url.clone()));
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
                 license_key: _,
                 category: _,
                 spdx_license_key: _,
                 other_spdx_license_keys: _,
                 is_exception: _,
                 is_deprecated: _,
                 json,
                 yaml: _,
                 html: _,
                 license: _,
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
    fn get_origin(&self) -> Origin {
        Origin::new_with_url(
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
                        short_name: _,
                        name: _,
                        category,
                        owner: _,
                        homepage_url: _,
                        notes,
                        spdx_license_key: _,
                        other_spdx_license_keys: _,
                        osi_license_key: _,
                        text_urls: _,
                        osi_url,
                        faq_url: _,
                        other_urls: _,
                        text,
                    },
                    ie @ IndexEntry {
                        license_key: _,
                        category: _,
                        spdx_license_key: _,
                        other_spdx_license_keys: _,
                        is_exception,
                        is_deprecated,
                        json: _,
                        yaml: _,
                        html: _,
                        license: _,
                    },
                )| {
                    let mut task =
                        LicenseGraphBuilderTask::new1(LicenseGraphNode::license_name(key))
                            .edge_left(
                                LicenseGraphEdge::Same,
                                l.clone()
                                    .get_other_license_names()
                                    .iter()
                                    .map(|other_name| LicenseGraphNode::license_name(other_name))
                                    .collect(),
                            )
                            .edge1(
                                LicenseGraphEdge::AppliesTo,
                                LicenseGraphNode::Raw(format!("{:#?}", l)),
                            )
                            .edge1(
                                LicenseGraphEdge::AppliesTo,
                                LicenseGraphNode::license_type(category),
                            )
                            .edge_add(LicenseGraphEdge::AppliesTo, {
                                let urls = l.clone().get_urls();
                                LicenseGraphNode::vec(
                                    urls.iter().map(|url| LicenseGraphNode::url(url)).collect(),
                                )
                            })
                            .edge_add(
                                LicenseGraphEdge::AppliesTo,
                                [
                                    if *is_deprecated {
                                        vec![LicenseGraphNode::license_flag("is_deprecated")]
                                    } else {
                                        vec![]
                                    },
                                    if *is_exception {
                                        vec![LicenseGraphNode::license_flag("is_exception")]
                                    } else {
                                        vec![]
                                    },
                                    match osi_url {
                                        Some(_) => {
                                            vec![LicenseGraphNode::license_flag("is_osi_approved")]
                                        }
                                        None => vec![],
                                    },
                                ]
                                .concat(),
                            )
                            .edge_add(
                                LicenseGraphEdge::AppliesTo,
                                match text {
                                    Some(text) => vec![LicenseGraphNode::license_text(&text)],
                                    None => vec![],
                                },
                            )
                            .edge_add(
                                LicenseGraphEdge::AppliesTo,
                                match notes {
                                    Some(notes) => vec![LicenseGraphNode::note(notes)],
                                    None => vec![],
                                },
                            );

                    log::debug!("{}", key);
                    task
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
            "source_scancode",
            &ScancodeSource {},
            vec!["MIT", "GPL-3.0-only"],
        )
    }
}
