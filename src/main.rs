use ldbcollector::model::*;
use ldbcollector::*;
use rust_embed::RustEmbed;
use std::collections::HashMap;
use std::env;
use std::error::Error;
use std::fs;
use std::fs::File;
use std::io::BufReader;
use std::process::Command;

#[derive(RustEmbed)]
#[folder = "./assets/"]
struct Asset;

fn gen_builder_dump() -> LicenseGraphBuilder {
    log::info!("    START Collect...");
    let builder = get_builder();
    let serialized = serde_json::to_string(&builder).unwrap();
    fs::write("./assets/builder.json", serialized).expect("Unable to write file");

    log::info!("... DONE Collect");

    builder
}

fn read_builder_dump() -> Result<LicenseGraphBuilder, Box<dyn Error>> {
    let file = Asset::get("builder.json").unwrap();
    let data = file.data.as_ref();
    let reader = BufReader::new(data);

    // Read the JSON contents of the file as an instance of `User`.
    let lgb = serde_json::from_reader(reader)?;

    Ok(lgb)
}

fn main() {
    pretty_env_logger::init();

    let args: Vec<String> = env::args().collect();
    let builder = match args.as_slice() {
        [ref _name, ref arg] => {
            if arg == "--load" {
                read_builder_dump().expect("builder should generated from JSON")
            } else {
                gen_builder_dump()
            }
        },
        _ => gen_builder_dump(),
    };
    log::info!("... finished creating builder");
    let graph = builder.build();
    log::info!("... finished building");
    server::sync_serve(Box::new(graph))
}