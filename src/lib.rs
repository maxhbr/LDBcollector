#![feature(core_intrinsics)]
use iri_string::types::IriStr;
use serde::{Serialize, Deserialize};
use serde_derive::{Deserialize, Serialize};
use std::intrinsics::type_name;
use std::collections::hash_map::DefaultHasher;
use std::hash::{Hash, Hasher};

#[derive(Debug, Clone, Deserialize, Serialize)] 
pub struct DataLicense {
    name: String,
    url: Option<String>
}

#[derive(Debug, Clone, Deserialize, Serialize)] 
pub enum Origin {
    Origin {
        name: String,
        data_license: Option<DataLicense>
    },
    OriginFile {
        file: String,
        origin: Box<Origin>
    },
    OriginUrl {
        url: String,
        origin: Box<Origin>
    }
}

#[derive(Debug, Clone, Deserialize, Serialize)] 
pub struct Statement {
    pub origin: Box<Origin>
}

// type StatementRef = Rc<RefCell<Statement>>;
// type StatementWRef = Weak<RefCell<Statement>>;

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn it_works() {
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
}