// #![feature(core_intrinsics)]
// use serde::{Serialize, Deserialize};
use serde_derive::{Serialize, Deserialize};
use std::fmt;
// use std::intrinsics::type_name;
// use std::collections::hash_map::DefaultHasher;
// use std::hash::{Hash, Hasher};
use petgraph::graph::{NodeIndex, EdgeIndex, Graph};
use petgraph::algo::{dijkstra, min_spanning_tree};
use petgraph::data::FromElements;
use petgraph::dot::{Dot, Config};
use std::collections::{HashMap};


#[derive(Debug, Clone, Deserialize, Serialize)] 
pub enum DataLicense {
    DataLicense {
        name: String,
        url: Option<String>
    },
    Noassertion {}
}

#[derive(Debug, Clone, Deserialize, Serialize)] 
pub enum Origin {
    Origin {
        name: String,
        data_license: DataLicense
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

impl Origin {
    fn new(name: &str, data_license: DataLicense) -> Self {
        Self::Origin { 
            name: String::from(name),
            data_license: data_license
        }
    }
    fn new_with_file(name: &str, file: &str, data_license: DataLicense) -> Self {
        Self::OriginFile { 
            file: String::from(file),
            origin: Box::new(Self::new(name, data_license))
        }
    }
    fn new_with_url(name: &str, url: &str, data_license: DataLicense) -> Self {
        Self::OriginUrl { 
            url: String::from(url),
            origin: Box::new(Self::new(name, data_license))
        }
    }
}

pub trait HasOrigin {
    fn get_origin(&self) -> &Box<Origin>;
}

pub trait Projection<T> {
    fn apply(self) -> Vec<T>;
}

pub trait Statement<T> : HasOrigin + Clone + std::fmt::Debug {
    fn apply(self) -> Vec<T>;
}

// https://doc.rust-lang.org/book/ch19-03-advanced-traits.html#using-the-newtype-pattern-to-implement-external-traits-on-external-types
#[derive(Debug, Clone, Deserialize, Serialize)] 
pub struct LicenseName(String);
impl LicenseName {
    fn new(name: &str) -> Self {
        Self(String::from(name))
    }
}
impl PartialEq for LicenseName {
    fn eq(&self, other: &Self) -> bool {
        self.0.to_lowercase() == other.0.to_lowercase()
    }
}
impl Eq for LicenseName {}
// impl IntoNodeReferences for LicenseName {
//     fn node_references(self) -> Self::NodeReferences {

//     }
// }
pub struct State {
    graph: Graph<LicenseName, ()>,
    idx_to_node: HashMap<NodeIndex, LicenseName>,
    node_to_idx: HashMap<LicenseName,NodeIndex>
}
impl State {
    fn new() -> Self {
        Self {
            graph: Graph::<LicenseName, ()>::new(),
            idx_to_node: HashMap::new(),
            node_to_idx: HashMap::new()
        }
    }
    fn add_license(&mut self, lic: LicenseName) -> NodeIndex {
        self.graph.add_node(lic)
    }
    fn add_alias(&mut self, left: LicenseName, right: LicenseName) -> EdgeIndex {
        let left_idx = self.add_license(left);
        let right_idx = self.add_license(right);
        self.graph.add_edge(left_idx, right_idx, ())
    }
}

// struct LicenseAlias {
//     left: LicenseName,
//     rights: Vec<LicenseName>
// }





// // #[derive(Debug, Clone, Deserialize, Serialize)] 
// pub struct Statement<T> 
// where
//   T: Clone + std::fmt::Debug
// {
//     pub origin: Box<Origin>,
//     content: T
// }

// impl<T: Clone + std::fmt::Debug> HasOrigin for Statement<T> {
//     fn get_origin(&self) -> &Box<Origin> {
//         &self.origin
//     }
// }

// impl<T: Clone + std::fmt::Debug> Statement<T> {
//     fn new(origin: Origin, content: T) -> Self {
//         Self { 
//             origin: Box::new(origin), 
//             content: content
//         }
//     }
// }
// impl<T: Clone + std::fmt::Debug> fmt::Debug for Statement<T> {
//     fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
//         write!(f, "[[{:?}][{:?}]]", self.content, self.origin)
//     }
// }

pub fn demo() -> State {
    let mut s = State::new();
    s.add_alias(LicenseName::new("MIT"), LicenseName::new("MIT License"));
    s.add_alias(LicenseName::new("mit"), LicenseName::new("The MIT"));
    println!("{:?}", Dot::with_config(&s.graph, &[Config::EdgeNoLabel]));
    s
}

#[cfg(test)]
mod tests {
    use super::*;

    // fn gen_example() -> dyn Statement<String> {
    //     let origin = Origin::new_with_url(
    //         "source",
    //         "http://some.source.invalid",
    //         DataLicense::Noassertion{}
    //     );
    //     println!("The origin is: {:?}", origin);
    //     let data = Statement::new(origin, String::from("bla"));
    //     println!("The data is: {:#?}", data);

    //     return data;
    // }

    // #[test]
    // fn it_works() {
    //     let _data = gen_example();

    //     // let serialized = serde_json::to_string(&data).unwrap();
    //     // println!("serialized = {}", serialized);
    // }

    #[test]
    fn license_name_tests() {
        assert_eq!(LicenseName::new("MIT"), LicenseName::new("MIT"));
        assert_eq!(LicenseName::new("MIT"), LicenseName::new("mit"));
        assert_eq!(LicenseName::new("MIT"), LicenseName::new("mIt"));
    }

    #[test]
    fn basic_graph() {
        let mut s = demo();

        // let serialized = serde_json::to_string(&data).unwrap();
        // println!("serialized = {}", serialized);
    }
}