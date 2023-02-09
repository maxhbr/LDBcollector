use ldbcollector::*;
use ldbcollector::model::*;
use std::fs;
use std::process::Command;

fn write_focused_dot(g: graph::LicenseGraph, needle: core::LicenseName) -> () {
    let focused = g.focus(needle);
    println!("{:#?}", focused);
    fs::write("graph.dot", format!("{}",focused.get_as_dot())).expect("Unable to write file");
}

fn main() {
    let g0 = graph::LicenseGraph::new();
    let g1 = source_spdx::add_spdx(g0);

    let g = g1;
    println!("{:#?}", g);

    write_focused_dot(g, lic!("BSD-3-Clause"));
}
