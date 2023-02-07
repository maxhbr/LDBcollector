use std::collections::HashMap;

mod license {
    use serde_derive::{Deserialize, Serialize};
    use std::fmt;
    use std::hash::{Hash, Hasher};

    #[derive(Debug, Clone, Deserialize, Serialize)]
    pub struct LicenseName(String);
    impl LicenseName {
        pub fn new(name: &str) -> Self {
            Self(String::from(name))
        }
    }
    impl core::fmt::Display for LicenseName {
        fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
            write!(f, "{}", self.0)
        }
    }
    impl PartialEq for LicenseName {
        fn eq(&self, other: &Self) -> bool {
            self.0.to_lowercase() == other.0.to_lowercase()
        }
    }
    impl Eq for LicenseName {}
    impl Hash for LicenseName {
        fn hash<H: Hasher>(&self, state: &mut H) {
            self.0.to_lowercase().hash(state);
        }
    }
}

mod origin {
    use serde_derive::{Deserialize, Serialize};

    #[derive(Debug, Clone, Deserialize, Serialize)]
    pub enum DataLicense {
        DataLicense { name: String, url: Option<String> },
        Noassertion {},
    }

    #[derive(Debug, Clone, Deserialize, Serialize)]
    pub enum Origin {
        Origin {
            name: String,
            data_license: DataLicense,
        },
        OriginFile {
            file: String,
            origin: Box<Origin>,
        },
        OriginUrl {
            url: String,
            origin: Box<Origin>,
        },
    }

    impl Origin {
        pub fn new(name: &str, data_license: DataLicense) -> Self {
            Self::Origin {
                name: String::from(name),
                data_license: data_license,
            }
        }
        pub fn new_with_file(name: &str, file: &str, data_license: DataLicense) -> Self {
            Self::OriginFile {
                file: String::from(file),
                origin: Box::new(Self::new(name, data_license)),
            }
        }
        pub fn new_with_url(name: &str, url: &str, data_license: DataLicense) -> Self {
            Self::OriginUrl {
                url: String::from(url),
                origin: Box::new(Self::new(name, data_license)),
            }
        }
    }

    pub trait HasOrigin {
        fn get_origin(&self) -> &Box<Origin>;
    }
}

mod statement {
    use super::*;

    pub trait Projection<T> {
        fn apply(self) -> Vec<T>;
    }

    pub trait Statement<T>: origin::HasOrigin + Clone + std::fmt::Debug {
        fn apply(self) -> Vec<T>;
    }
}

mod state {
    use super::license::*;
    use super::*;
    use petgraph::algo::{dijkstra, min_spanning_tree};
    use petgraph::dot::{Config, Dot};
    use petgraph::graph::{EdgeIndex, NodeIndex};
    use petgraph::stable_graph::StableGraph;
    use serde_derive::{Deserialize, Serialize};
    use std::fmt;

    #[derive(Debug, Clone, Deserialize, Serialize)]
    pub enum LicenseRelation {
        Same,
    }

    pub struct State {
        pub graph: StableGraph<LicenseName, LicenseRelation>,
        pub lic_to_idx: HashMap<LicenseName, NodeIndex>,
    }
    impl State {
        pub fn new() -> Self {
            Self {
                graph: StableGraph::<LicenseName, LicenseRelation>::new(),
                lic_to_idx: HashMap::new(),
            }
        }
        pub fn consistency_check(&self) -> () {
            let map_and_graph_length_matches = self.lic_to_idx.len() == self.graph.edge_count();
            assert!(map_and_graph_length_matches);
            let maps_are_consistent = self.lic_to_idx.clone().into_iter().all(|(lic, idx)| {
                match self.graph.node_weight(idx) {
                    None => false,
                    Some(&ref rev_lic) => lic == *rev_lic,
                }
            });
            assert!(maps_are_consistent);
        }
        pub fn add_license_(&mut self, lic: LicenseName) -> NodeIndex {
            match self.lic_to_idx.get(&lic) {
                Some(idx) => *idx,
                None => {
                    let idx = self.graph.add_node(lic.clone());
                    self.lic_to_idx.insert(lic.clone(), idx);
                    idx
                }
            }
        }
        pub fn add_license(mut self, lic: LicenseName) -> Self {
            self.add_license_(lic);
            self
        }
        pub fn add_alias_(
            &mut self,
            left: LicenseName,
            right: LicenseName,
            relation: LicenseRelation,
        ) -> EdgeIndex {
            let left_idx = self.add_license_(left);
            let right_idx = self.add_license_(right);
            let e1 = self.graph.add_edge(left_idx, right_idx, relation);
            e1
        }
        pub fn add_alias(
            mut self,
            left: LicenseName,
            right: LicenseName,
            relation: LicenseRelation,
        ) -> Self {
            self.add_alias_(left, right, relation);
            self
        }
        pub fn get_licenses_dot(&self) -> String {
            let dot = Dot::with_config(&self.graph, &[]);
            format!("{:?}", dot)
        }
    }
    impl fmt::Debug for State {
        fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
            f.debug_struct("State").field("graph", &self.graph).finish()
        }
    }
}

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

pub fn demo() -> state::State {
    state::State::new()
        .add_alias(
            license::LicenseName::new("MIT"),
            license::LicenseName::new("MIT License"),
            state::LicenseRelation::Same,
        )
        .add_alias(
            license::LicenseName::new("mit"),
            license::LicenseName::new("The MIT"),
            state::LicenseRelation::Same,
        )
}

#[cfg(test)]
mod tests {
    use super::license::*;
    use super::*;

    #[test]
    fn license_name_tests() {
        assert_eq!(LicenseName::new("MIT"), LicenseName::new("MIT"));
        assert_eq!(LicenseName::new("MIT"), LicenseName::new("mit"));
        assert_eq!(LicenseName::new("MIT"), LicenseName::new("mIt"));
    }

    #[test]
    fn demo_should_run() {
        let s = demo();
        s.consistency_check();
        println!("{s:#?}");
    }
}
