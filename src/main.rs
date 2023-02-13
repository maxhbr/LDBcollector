use ldbcollector::model::graph::LicenseGraph;
use ldbcollector::model::*;
use ldbcollector::*;
use std::fs;
use std::process::Command;

fn write_focused_dot(g: graph::LicenseGraph, needle: core::LicenseName) -> () {
    let focused = g.focus(needle);
    write_dot(focused)
}

fn write_dot(g: graph::LicenseGraph) -> () {
    println!("{:#?}", g);
    let g_dot = format!("{}", g.get_as_dot());
    println!("{}", g_dot);
    fs::write("graph.dot", g_dot).expect("Unable to write file");
}

fn main() {
    let sources: Vec<Box<dyn for<'a> Fn(LicenseGraph<'a>) -> LicenseGraph<'a>>> = vec![
        Box::new(source_spdx::add_spdx),
        Box::new(source_spdx::add_imprecise),
        Box::new(source_scancode::add_scancode),
        Box::new(source_osadl::add_osadl_checklist),
        Box::new(source_blueoakcouncil::add_blueoakcouncil),
    ];

    let g = sources
        .iter()
        .fold(graph::LicenseGraph::new(), |acc, f| f(acc));

    // println!("{:#?}", g);
    // write_dot(g);

    // let needle = String::from("BSD-3-Clause");
    let needle = String::from("GPL-2.0-or-later");
    write_focused_dot(g, lic!(needle));
}
