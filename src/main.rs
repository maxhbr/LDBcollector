use ldbcollector::model::*;
use ldbcollector::*;
use std::fs;
use std::process::Command;

fn write_focused_dot(g: graph::LicenseGraph, needle: core::LicenseName) -> () {
    let focused = g.focus(needle);
    println!("{:#?}", focused);
    fs::write("graph.dot", format!("{}", focused.get_as_dot())).expect("Unable to write file");
}

fn main() {
    let g0 = graph::LicenseGraph::new();
    let g1 = source_spdx::add_spdx(g0);
    let g2 = source_osadl::add_osadl_checklist(g1);
    let g3 = source_blueoakcouncil::add_blueoakcouncil(g2);

    let g = g3;
    // println!("{:#?}", g);

    // write_focused_dot(g, lic!("BSD-3-Clause"));
}
