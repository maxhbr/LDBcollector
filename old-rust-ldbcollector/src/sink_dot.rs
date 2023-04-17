use crate::model::*;
use std::error::Error;
use std::fs;
use std::fs::File;
use std::path::PathBuf;
use std::process::Command;

use graphviz_rust::dot_generator::*;
use graphviz_rust::dot_structures::*;
use graphviz_rust::{
    attributes::*,
    cmd::{CommandArg, Format, Layout},
    exec, parse,
    printer::{DotPrinter, PrinterContext},
};

pub fn write_focused_dot(
    out_file: String,
    g: &LicenseGraph,
    needle: String,
) -> Result<(), Box<dyn Error>> {
    let focused = g.focus(&needle)?;
    write_dot(out_file, &focused)
}

pub fn write_dot(out_file: String, g: &LicenseGraph) -> Result<(), Box<dyn Error>> {
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

pub fn render_dot(graph: &LicenseGraph, condensed: bool, use_fdp: bool) -> String {
    log::debug!("parse dot");
    let g = if condensed {
        parse(&format!("{}", graph.get_condensed_as_dot())).unwrap()
    } else {
        parse(&format!("{}", graph.get_as_dot())).unwrap()
    };

    log::debug!("render dot to svg");

    let mut args = vec![];
    args.extend(vec![Format::Svg.into()]);
    if use_fdp {
        args.extend(vec![Layout::Fdp.into()]);
        // -Lg         - Don't use grid
        // -LO         - Use old attractive force
        // -Ln<i>      - Set number of iterations to i
        // -LU<i>      - Set unscaled factor to i
        // -LC<v>      - Set overlap expansion factor to v
        // -LT[*]<v>   - Set temperature (temperature factor) to v
        args.extend(
            ["-Goverlap=prism", "-Lg"]
                .iter()
                .map(|arg| CommandArg::Custom(String::from(*arg)))
                .collect::<Vec<_>>(),
        );
    }
    exec(g, &mut PrinterContext::default(), args).unwrap()
}
