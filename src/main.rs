use ldbcollector::model::*;
use ldbcollector::*;
use std::fs;
use std::process::Command;

fn write_focused_dot(g: graph::LicenseGraph, needle: core::LicenseName) -> () {
    let focused = g.focus(needle);
    println!("{:#?}", focused);
    let focused_dot = format!("{}", focused.get_as_dot());
    println!("{}", focused_dot);
    fs::write("graph.dot", focused_dot).expect("Unable to write file");
}

fn main() {
    let g0 = graph::LicenseGraph::new();
    let g1 = source_spdx::add_spdx(g0);
    let g2 = source_osadl::add_osadl_checklist(g1);
    let g3 = source_blueoakcouncil::add_blueoakcouncil(g2);

    let g = g3;
    // println!("{:#?}", g);

    // let needle = String::from("BSD-3-Clause");
    let needle = String::from("GPL-2.0-or-later");
    write_focused_dot(g, lic!(needle));
}
