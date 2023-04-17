pub mod model;
pub mod server;

#[macro_export]
macro_rules! lic {
    ($l:tt) => {
        $crate::model::LicenseName::new(String::from($l))
    };
}

#[macro_export]
macro_rules! lic_string {
    ($l:tt) => {
        $crate::model::LicenseName::new($l.clone())
    };
}

// ############################################################################

pub mod sink_dot;
pub mod sink_force_graph;
pub mod sink_html;

// ############################################################################

pub mod test_helper {
    use super::sink_dot::*;
    use crate::model::*;
    use std::fs;

    pub fn test_graph(source_name: &str, graph: LicenseGraph, licenses: Vec<&str>) {
        let test_output_dir = format!("test_output/{}/", source_name);
        fs::create_dir_all(test_output_dir.clone()).expect("Unable to create dir");

        licenses.iter().for_each(|license| {
            let needle = String::from(*license);
            write_focused_dot(
                format!("{}{}.dot", &test_output_dir, &needle),
                &graph,
                needle,
            )
            .expect("failed to generate svg");
        });
    }

    pub fn test_builder(source_name: &str, builder: LicenseGraphBuilder, licenses: Vec<&str>) {
        let test_output_dir = format!("test_output/{}/", source_name);
        fs::create_dir_all(test_output_dir.clone()).expect("Unable to create dir");

        let serialized = serde_json::to_string(&builder).unwrap();
        fs::write(format!("{}builder.json", &test_output_dir), serialized)
            .expect("Unable to write file");

        let graph = builder.build();

        test_graph(source_name, graph, licenses)
    }

    pub fn test_single_origin(source_name: &str, source: &dyn Source, licenses: Vec<&str>) {
        let builder = LicenseGraphBuilder::new().add_unboxed_source(source);
        test_builder(source_name, builder, licenses)
    }
}

// ############################################################################

pub mod source_blueoakcouncil;
pub mod source_cavil;
pub mod source_fedora_license_data;
pub mod source_fsf;
pub mod source_hanshammel;
pub mod source_librariesio;
pub mod source_metaeffekt_universe;
pub mod source_okfn;
pub mod source_osadl;
pub mod source_oslc_handbook;
pub mod source_scancode;
pub mod source_spdx;

pub fn get_sources() -> Vec<Box<dyn crate::model::Source>> {
    let sources: Vec<Box<dyn crate::model::Source>> = vec![
        Box::new(crate::source_spdx::SpdxSource {}),
        Box::new(crate::source_spdx::EmbarkSpdxSource {}),
        Box::new(crate::source_scancode::ScancodeSource {}),
        Box::new(crate::source_osadl::OsadlSource {}),
        Box::new(crate::source_blueoakcouncil::CopyleftListSource {}),
        Box::new(crate::source_blueoakcouncil::LicenseListSource {}),
        Box::new(crate::source_oslc_handbook::OslcHandbookSource {}),
        Box::new(crate::source_hanshammel::HansHammelSource {}),
        Box::new(crate::source_librariesio::LibrariesioSource {}),
        Box::new(crate::source_okfn::OkfnSource {}),
        Box::new(crate::source_cavil::CavilSource {}),
        Box::new(crate::source_metaeffekt_universe::MetaeffektUniverseSource {}),
        Box::new(crate::source_fedora_license_data::FedoraLicenseDataSource {}),
        Box::new(crate::source_fsf::FsfSource {}),
    ];
    sources
}

pub fn get_builder() -> crate::model::LicenseGraphBuilder {
    get_sources().iter().fold(
        crate::model::LicenseGraphBuilder::new(),
        |builder, source| builder.add_source(source),
    )
}

#[cfg(test)]
mod tests {
    use crate::get_builder;
    use crate::test_helper;

    #[test]
    fn all_origins_test() {
        let builder = get_builder();

        test_helper::test_builder(
            "all",
            builder,
            vec!["MIT", "BSD-3-Clause", "GPL-3.0-or-later"],
        )
    }
}
