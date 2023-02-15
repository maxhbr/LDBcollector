use ldbcollector::model::graph::{LicenseGraph, LicenseGraphBuilder};
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

fn gen_builder_dump() {
    log::info!("    START Collect...");
    let builder = get_builder();
    let serialized = serde_json::to_string(&builder).unwrap();
    fs::write("./assets/builder.json", serialized).expect("Unable to write file");

    log::info!("... DONE Collect");
}

fn read_builder_dump() -> Result<LicenseGraphBuilder, Box<dyn Error>> {
    let file = Asset::get("builder.json").unwrap();
    let data = file.data.as_ref();
    let reader = BufReader::new(data);

    // Read the JSON contents of the file as an instance of `User`.
    let lgb = serde_json::from_reader(reader)?;

    Ok(lgb)
}

fn querystring(str: String) -> HashMap<String, String> {
    let mut result = HashMap::new();
    let parts = str.split("&");
    for part in parts {
        let query: Vec<&str> = part.split("=").collect();
        if query.len() == 0 {
            continue;
        }
        if query.len() == 1 {
            result.insert(query[0].to_string(), "".to_string());
            continue;
        }
        result.insert(query[0].to_string(), query[1].to_string());
    }
    return result;
}

fn serve() {
    let builder = read_builder_dump().expect("builder should generated from JSON");
    let mut graph = builder.build();

    println!("Content-type: text/html");
    println!();

    let q = querystring(env::var("QUERY_STRING").unwrap());
    if q.contains_key("name") {
        let name = &q["name"];
        graph = graph.focus(crate::core::LicenseName::new(name.to_string().clone()));
    }
    println!("<body>\n<pre>\n{:?}\n</pre>\n</body>", graph);
}

fn main() {
    env_logger::init();

    let args: Vec<String> = env::args().collect();
    match args.as_slice() {
        [ref _name, ref arg] => {
            if arg == "--serve" {
                serve()
            } else {
                panic!("crash and burn");
            }
        }
        _ => gen_builder_dump(),
    }
}
