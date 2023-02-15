use ldbcollector::model::graph::{LicenseGraph, LicenseGraphBuilder};
use ldbcollector::model::*;
use ldbcollector::*;
use std::fs;
use std::fs::File;
use std::process::Command;
use std::env;
use std::io::BufReader;
use std::collections::HashMap;
use std::error::Error;

fn gen_builder_dump() {
    log::info!("    START Collect...");
    let builder = get_builder();
    let serialized = serde_json::to_string(&builder).unwrap();
    fs::write("./builder.json", serialized).expect("Unable to write file");

    log::info!("... DONE Collect");
}

fn read_builder_dump() -> Result<LicenseGraphBuilder, Box<dyn Error>> {
    let file = File::open("./builder.json")?;
    let reader = BufReader::new(file);

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
    return result
}

fn serve() {
    println!("Content-type: text/html");
    println!();

    let mut name = "unknown";
    let q = querystring(env::var("QUERY_STRING").unwrap());
    if q.contains_key("name") {
        name = &q["name"];
    }
    println!("<body><h3>Hello {}!</h3></body>", name);
}

fn main() {
    env_logger::init();

    let args: Vec<String> = env::args()
       .collect();
    match args.as_slice() {
        [ref name, ref arg] => if arg == "--serve" {
            serve()
        } else {
            panic!("crash and burn");
        },
        _ => gen_builder_dump(),
    }
}
