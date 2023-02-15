pub mod model;
pub mod server;

#[macro_export]
macro_rules! lic {
    ($l:tt) => {
        $crate::model::core::LicenseName::new(String::from($l))
    };
}

#[macro_export]
macro_rules! lic_string {
    ($l:tt) => {
        $crate::model::core::LicenseName::new($l.clone())
    };
}

// ############################################################################

pub mod source_blueoakcouncil;
pub mod source_osadl;
pub mod source_scancode;
pub mod source_spdx;

pub fn get_sources() -> Vec<Box<dyn crate::model::graph::Source>> {
    let sources: Vec<Box<dyn crate::model::graph::Source>> = vec![
        Box::new(crate::source_spdx::SpdxSource {}),
        Box::new(crate::source_spdx::EmbarkSpdxSource {}),
        Box::new(crate::source_scancode::ScancodeSource {}),
        Box::new(crate::source_osadl::OsadlSource {}),
        Box::new(crate::source_blueoakcouncil::CopyleftListSource {}),
        Box::new(crate::source_blueoakcouncil::LicenseListSource {}),
    ];
    sources
}

pub fn get_builder() -> crate::model::graph::LicenseGraphBuilder {
    get_sources().iter().fold(
        crate::model::graph::LicenseGraphBuilder::new(),
        |builder, source| builder.add_source(source),
    )
}

#[cfg(test)]
mod tests {
    use crate::get_builder;
    use crate::model::core::*;
    use crate::model::dot::*;
    use crate::model::graph::*;
    use crate::model::*;
    use std::fs;

    #[test]
    fn all_origins_test() {
        let test_output_dir = "test_output/";
        let builder = get_builder();
        let serialized = serde_json::to_string(&builder).unwrap();
        fs::write(format!("{}builder.json", &test_output_dir), serialized)
            .expect("Unable to write file");

        let graph = builder.build();
        let needle = String::from("MIT");
        write_focused_dot(
            format!("{}{}.dot", &test_output_dir, &needle),
            &graph,
            LicenseName::new(needle),
        )
        .expect("failed to generate svg");
        let needle = String::from("GPL-3.0-only");
        write_focused_dot(
            format!("{}{}.dot", &test_output_dir, &needle),
            &graph,
            LicenseName::new(needle),
        )
        .expect("failed to generate svg");
        log::info!("... DONE");
    }
}
