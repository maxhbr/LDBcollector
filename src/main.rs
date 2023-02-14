use ldbcollector::model::graph::LicenseGraph;
use ldbcollector::model::*;
use ldbcollector::*;
use std::fs;
use std::fs::File;
use std::process::Command;

fn write_focused_dot(g: graph::LicenseGraph, needle: core::LicenseName) -> () {
    let focused = g.focus(needle);
    write_dot(focused)
}

fn write_dot(g: graph::LicenseGraph) -> () {
    log::info!("... START gen dot...");
    log::info!("{:#?}", g);
    let g_dot = format!("{}", g.get_as_dot());
    log::debug!("{}", g_dot);
    fs::write("graph.dot", g_dot).expect("Unable to write file");
    log::info!("... START gen dot svg...");
    let svg = File::create("graph.svg").unwrap();
    Command::new("dot")
        .arg("-Tsvg")
        .arg("graph.dot")
        .stdout(svg)
        .spawn()
        .expect("dot call should succeed");
    log::info!("... DONE gen dot svg");
}

fn main() {
    env_logger::init();
    log::info!("    START ...");
    let sources: Vec<Box<dyn graph::Source>> = vec![
        Box::new(source_spdx::SpdxSource{}),
        Box::new(source_spdx::EmbarkSpdxSource{}),
        Box::new(source_scancode::EmbarkSpdxSource{}),
        Box::new(source_osadl::OsadlSource{}),
        Box::new(source_blueoakcouncil::CopyleftListSource{}),
        Box::new(source_blueoakcouncil::LicenseListSource{})
    ];

    log::info!("... START Collect...");
    let builder = sources
        .iter()
        .fold(graph::LicenseGraphBuilder::new(), |builder, source| builder.add_source(source));
    let serialized = serde_json::to_string(&builder).unwrap();
    fs::write("data.json", serialized).expect("Unable to write file");

    let g = builder.build();
    log::info!("... DONE Collect...");

    // log::debug!("{:#?}", g);
    // write_dot(g);

    // let needle = String::from("BSD-3-Clause");
    let needle = String::from("GPL-3.0-only");
    // let needle = String::from("MIT");
    write_focused_dot(g, lic!(needle));
    log::info!("... DONE");
}
