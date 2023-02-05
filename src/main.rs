use serde::{Serialize, Deserialize};
use ldbcolector::{Statement, Origin};

fn main() {
    let origin = Origin::OriginUrl{
        url: String::from("http://some.source.invalid"),
        origin: Box::new(Origin::Origin{
            name: String::from("source"),
            data_license: None
        })
    };
    let data = Statement{
        origin: Box::new(origin)
    };
    let serialized = serde_json::to_string(&data).unwrap();
    println!("serialized = {}", serialized);
}
