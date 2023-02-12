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
    let g0 = graph::LicenseGraph::new();
    let g1 = source_spdx::add_spdx(g0);
    let g2 = source_osadl::add_osadl_checklist(g1);
    let g3 = source_blueoakcouncil::add_blueoakcouncil(g2);

    let g = g3;
    // println!("{:#?}", g);
    // write_dot(g);

    // let needle = String::from("BSD-3-Clause");
    let needle = String::from("GPL-2.0-or-later");
    write_focused_dot(g, lic!(needle));
}
