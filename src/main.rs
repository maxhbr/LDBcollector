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
    let sources: Vec<Box<dyn Fn(LicenseGraph) -> LicenseGraph>> = vec![
        // Box::new(source_spdx::add_spdx),
        // Box::new(source_spdx::add_imprecise),
        // // Box::new(source_scancode::add_scancode),
        // Box::new(source_osadl::add_osadl_checklist),
        // Box::new(source_blueoakcouncil::add_blueoakcouncil),
    ];

    log::info!("... START Collect...");
    let g = sources
        .iter()
        .fold(graph::LicenseGraph::new(), |acc, f| f(acc));
    log::info!("... DONE Collect...");

    // log::debug!("{:#?}", g);
    // write_dot(g);

    let needle = String::from("BSD-3-Clause");
    // let needle = String::from("GPL-2.0-or-later");
    write_focused_dot(g, lic!(needle));
    log::info!("... DONE");
}
