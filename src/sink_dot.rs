use crate::model::*;
use std::fs;
use std::fs::File;
use std::path::PathBuf;
use std::process::Command;

use graphviz_rust::dot_generator::*;
use graphviz_rust::dot_structures::*;
use graphviz_rust::{
    attributes::*,
    cmd::{CommandArg, Format},
    exec, parse,
    printer::{DotPrinter, PrinterContext},
};

pub fn write_focused_dot(
    out_file: String,
    g: &LicenseGraph,
    needle: String,
) -> Result<(), std::io::Error> {
    let focused = g.focus(needle);
    write_dot(out_file, &focused)
}

pub fn write_dot(out_file: String, g: &LicenseGraph) -> Result<(), std::io::Error> {
    let mut parent = PathBuf::from(out_file.clone());
    if parent.pop() {
        match parent.to_str() {
            Option::Some(parent_str) => fs::create_dir_all(parent_str)?,
            Option::None {} => {}
        }
    }

    log::info!("... START gen dot...");
    log::info!("{:#?}", g);
    let g_dot = format!("{}", g.get_as_dot());
    log::debug!("{}", g_dot);
    fs::write(&out_file, g_dot)?;

    let out_svg_file = format!("{}.svg", &out_file);
    log::info!("... START gen dot svg...");
    let svg = File::create(out_svg_file).unwrap();
    Command::new("dot")
        .arg("-Tsvg")
        .arg(out_file)
        .stdout(svg)
        .spawn()?;
    log::info!("... DONE gen dot svg");

    Ok(())
}

pub fn render_dot(graph: LicenseGraph) -> String {
    log::debug!("parse dot");
    let g = parse(&format!("{}", graph.get_as_dot())).unwrap();
    log::debug!("render dot to svg");
    exec(g, &mut PrinterContext::default(), vec![Format::Svg.into()]).unwrap()
}
