use spdx::{LicenseId, LicenseItem};
use std::collections::HashMap;
use std::fmt;
use std::hash::{Hash, Hasher};

pub mod core {
    use super::*;

    //#############################################################################
    //## LicenseName
    #[derive(Debug, Clone, Copy)]
    pub struct LicenseName<'a>(&'a str);
    impl<'a> LicenseName<'a> {
        pub fn new(name: &'a str) -> Self {
            Self(name)
        }
    }
    impl<'a> core::fmt::Display for LicenseName<'a> {
        fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
            write!(f, "{}", self.0)
        }
    }
    impl<'a> PartialEq for LicenseName<'a> {
        fn eq(&self, other: &Self) -> bool {
            self.0.to_lowercase() == other.0.to_lowercase()
        }
    }
    impl<'a> Eq for LicenseName<'a> {}
    impl<'a> Hash for LicenseName<'a> {
        fn hash<H: Hasher>(&self, state: &mut H) {
            self.0.to_lowercase().hash(state);
        }
    }
    //## end LicenseName
    //#############################################################################

    // //#############################################################################
    // //## License
    // #[derive(Debug, Clone)]
    // pub enum LicenseReferenceType {
    //     SHORTNAME,
    //     FULLNAME,
    //     UNKNOWN,
    // }
    // pub enum LicenseReference {
    //     SpdxRef {
    //         spdx: LicenseItem,
    //     },
    //     NameRef {
    //         license_name: LicenseName,
    //         namespace: Option<String>,
    //         license_name_type: LicenseReferenceType,
    //     },
    //     RefList {
    //         refs: Vec<LicenseReference>
    //     }
    // }
    // pub struct License {
    //     references: Vec<LicenseReference>,
    // }
    // //## end License
    // //#############################################################################
}

pub mod graph {
    use super::core::*;
    use super::*;
    use either::{Either, Left, Right};
    use multimap::MultiMap;
    use petgraph::algo::{dijkstra, has_path_connecting, min_spanning_tree, tarjan_scc};
    use petgraph::dot::{Config, Dot};
    use petgraph::graph::{Edge, EdgeIndex, Frozen, Node, NodeIndex};
    use petgraph::stable_graph::StableGraph;
    use serde::Serialize;
    use serde_json::{Result, Value};

    //#############################################################################
    //## Origin
    #[derive(Debug, Clone)]
    pub struct Origin<'a> {
        name: &'a str,
        data_license: Option<LicenseItem>,
        file: Option<&'a str>,
        url: Option<&'a str>,
    }

    impl<'a> Origin<'a> {
        pub const fn new(name: &'a str, data_license: Option<LicenseItem>) -> Self {
            Self {
                name,
                data_license,
                file: Option::None,
                url: Option::None,
            }
        }
        pub const fn new_with_file(
            name: &'a str,
            file: &'a str,
            data_license: Option<LicenseItem>,
        ) -> Self {
            Self {
                name,
                data_license,
                file: Option::Some(file),
                url: Option::None,
            }
        }
        pub const fn new_with_url(
            name: &'a str,
            url: &'a str,
            data_license: Option<LicenseItem>,
        ) -> Self {
            Self {
                name,
                data_license,
                file: Option::None,
                url: Option::Some(url),
            }
        }
    }

    pub trait HasOrigin<'a> {
        fn get_origin(&self) -> &'a Origin;
    }
    //## end Origin
    //#############################################################################

    #[derive(Debug, Clone)]
    pub enum LicenseGraphNode<'a> {
        LicenseNameNode { license_name: LicenseName<'a> },
        Statement { statement_content: String },
        StatementJson { statement_content: Value },
    }
    impl<'a> LicenseGraphNode<'a> {
        pub fn mk_statement(i: &str) -> Self {
            Self::Statement {
                statement_content: String::from(i),
            }
        }
        pub fn mk_json_statement(i: impl Serialize) -> Self {
            Self::StatementJson {
                statement_content: serde_json::to_value(i).unwrap(),
            }
        }
    }

    #[derive(Debug, Clone, Copy)]
    pub enum LicenseGraphEdge {
        Same,
        AppliesTo,
    }

    #[derive(Clone)]
    pub struct LicenseGraph<'a> {
        pub graph: StableGraph<LicenseGraphNode<'a>, LicenseGraphEdge>,
        pub license_to_idx: HashMap<LicenseName<'a>, NodeIndex>,
        node_origins: MultiMap<NodeIndex, &'a Origin<'a>>,
        edge_origins: MultiMap<EdgeIndex, &'a Origin<'a>>,
    }
    impl<'a> LicenseGraph<'a> {
        pub fn new() -> Self {
            Self {
                graph: StableGraph::<LicenseGraphNode, LicenseGraphEdge>::new(),
                license_to_idx: HashMap::new(),
                node_origins: MultiMap::new(),
                edge_origins: MultiMap::new(),
            }
        }

        pub fn focus(self, license_name: LicenseName) -> Self {
            let mut s = self.clone();

            let root_idx = *self.license_to_idx.get(&license_name).unwrap();

            s.graph.retain_nodes(|frozen_s, idx: NodeIndex| {
                has_path_connecting(&self.graph, idx, root_idx, Option::None)
            });
            s.license_to_idx
                .retain(|_, idx| s.graph.node_weight(*idx).is_some());
            s.node_origins
                .retain(|idx, _| s.graph.node_weight(*idx).is_some());
            s.edge_origins
                .retain(|idx, _| s.graph.edge_weight(*idx).is_some());

            s
        }

        fn add_node(&mut self, node: LicenseGraphNode<'a>) -> NodeIndex {
            match node {
                LicenseGraphNode::LicenseNameNode { license_name } => {
                    match self.license_to_idx.get(&license_name) {
                        Some(idx) => *idx,
                        None => {
                            let idx = self.graph.add_node(node);
                            self.license_to_idx.insert(license_name, idx);
                            idx
                        }
                    }
                }
                _ => self.graph.add_node(node),
            }
        }
        fn add_edges(
            &mut self,
            left: LicenseGraphNode<'a>,
            rights: Vec<LicenseGraphNode<'a>>,
            edge: LicenseGraphEdge,
        ) -> Vec<EdgeIndex> {
            let left_idx = self.add_node(left);
            rights
                .into_iter()
                .map(|right| {
                    let right_idx = self.add_node(right);
                    self.graph.add_edge(left_idx, right_idx, edge)
                })
                .collect()
        }

        fn add_node_with_origin(
            &mut self,
            node: LicenseGraphNode<'a>,
            origin: &'a Origin,
        ) -> NodeIndex {
            let idx = self.add_node(node);
            self.node_origins.insert(idx, origin);
            idx
        }
        fn add_edges_with_origin(
            &mut self,
            left: LicenseGraphNode<'a>,
            rights: Vec<LicenseGraphNode<'a>>,
            edge: LicenseGraphEdge,
            origin: &'a Origin,
        ) -> Vec<EdgeIndex> {
            self.add_edges(left, rights, edge)
                .into_iter()
                .map(|idx| {
                    self.edge_origins.insert(idx, origin);
                    idx
                })
                .collect()
        }

        pub fn add_license(mut self, lic: LicenseName<'a>, origin: &'a Origin) -> Self {
            self.add_node_with_origin(
                LicenseGraphNode::LicenseNameNode { license_name: lic },
                origin,
            );
            self
        }
        pub fn add_aliases(mut self, names: Vec<LicenseName<'a>>, origin: &'a Origin) -> Self {
            match names.as_slice() {
                [] => {}
                [name] => {
                    self.add_node_with_origin(
                        LicenseGraphNode::LicenseNameNode {
                            license_name: *name,
                        },
                        origin,
                    );
                }
                [best, others @ ..] => {
                    self.add_edges_with_origin(
                        LicenseGraphNode::LicenseNameNode {
                            license_name: *best,
                        },
                        others
                            .into_iter()
                            .map(|o| LicenseGraphNode::LicenseNameNode { license_name: *o })
                            .collect(),
                        LicenseGraphEdge::Same,
                        origin,
                    );
                }
            };
            self
        }
        pub fn add_relational_fact(
            mut self,
            left: LicenseGraphNode<'a>,
            rights: Vec<LicenseName<'a>>,
            origin: &'a Origin,
        ) -> Self {
            self.add_edges_with_origin(
                left,
                rights
                    .into_iter()
                    .map(|o| LicenseGraphNode::LicenseNameNode { license_name: o })
                    .collect(),
                LicenseGraphEdge::AppliesTo,
                origin,
            );
            self
        }
        pub fn get_as_dot(&self) -> String {
            let dot = Dot::with_config(&self.graph, &[]);
            format!("{:?}", dot)
        }
    }
    impl<'a> fmt::Debug for LicenseGraph<'a> {
        fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
            f.debug_struct("State").field("graph", &self.graph).finish()
        }
    }
}

// #[derive(Debug, Clone)]
// pub enum LicenseReference {
//     SpdxRef {
//         spdx: LicenseItem,
//     },
//     NameRef {
//         license_name: LicenseName,
//         namespace: Option<String>,
//         license_name_type: LicenseReferenceType,
//     },
//     RefList {
//         refs: Vec<LicenseReference>
//     }
// }

// pub mod origin {
//     use serde_derive::{Deserialize, Serialize};

//     #[derive(Debug, Clone, Deserialize, Serialize)]
//     pub enum DataLicense {
//         DataLicense { name: String, url: Option<String> },
//         Noassertion {},
//     }

//     #[derive(Debug, Clone, Deserialize, Serialize)]
//     pub enum Origin {
//         Origin {
//             name: String,
//             data_license: DataLicense,
//         },
//         OriginFile {
//             file: String,
//             origin: Box<Origin>,
//         },
//         OriginUrl {
//             url: String,
//             origin: Box<Origin>,
//         },
//     }

//     impl Origin {
//         pub fn new(name: &str, data_license: DataLicense) -> Self {
//             Self::Origin {
//                 name: String::from(name),
//                 data_license: data_license,
//             }
//         }
//         pub fn new_with_file(name: &str, file: &str, data_license: DataLicense) -> Self {
//             Self::OriginFile {
//                 file: String::from(file),
//                 origin: Box::new(Self::new(name, data_license)),
//             }
//         }
//         pub fn new_with_url(name: &str, url: &str, data_license: DataLicense) -> Self {
//             Self::OriginUrl {
//                 url: String::from(url),
//                 origin: Box::new(Self::new(name, data_license)),
//             }
//         }
//     }

//     pub trait HasOrigin {
//         fn get_origin(&self) -> &Box<Origin>;
//     }
// }

// pub mod statement {
//     use super::*;

//     pub trait Projection<T> {
//         fn apply(self) -> Vec<T>;
//     }

//     pub trait Statement<T>: origin::HasOrigin + Clone + std::fmt::Debug {
//         fn apply(self) -> Vec<T>;
//     }
// }

// pub mod state {
//     use super::core::*;
//     use super::*;
//     use petgraph::algo::{dijkstra, min_spanning_tree, tarjan_scc};
//     use petgraph::dot::{Config, Dot};
//     use petgraph::graph::{EdgeIndex, NodeIndex};
//     use petgraph::stable_graph::StableGraph;
//     use serde_derive::{Deserialize, Serialize};
//     use std::cmp::Ordering;
//     use std::cmp::PartialOrd;
//     use std::collections::hash_set::HashSet;
//     use std::fmt;

//     #[derive(Debug, Clone, Deserialize, Serialize)]
//     pub enum LicenseRelation {
//         Same,
//     }

//     pub struct State {
//         pub graph: StableGraph<LicenseName, LicenseRelation>,
//         pub license_to_idx: HashMap<LicenseName, NodeIndex>,
//         pub license_statements: HashMap<NodeIndex, ()>,
//         pub license_relation_statements: HashMap<NodeIndex, ()>,
//     }
//     impl State {
//         pub fn new() -> Self {
//             Self {
//                 graph: StableGraph::<LicenseName, LicenseRelation>::new(),
//                 license_to_idx: HashMap::new(),
//                 license_statements: HashMap::new(),
//                 license_relation_statements: HashMap::new(),
//             }
//         }
//         pub fn consistency_check(&self) -> () {
//             let map_and_graph_length_matches = self.license_to_idx.len() == self.graph.edge_count();
//             assert!(map_and_graph_length_matches);
//             let maps_are_consistent = self.license_to_idx.clone().into_iter().all(|(lic, idx)| {
//                 match self.graph.node_weight(idx) {
//                     None => false,
//                     Some(&ref rev_lic) => lic == *rev_lic,
//                 }
//             });
//             assert!(maps_are_consistent);
//         }
//         pub fn add_license_(&mut self, lic: LicenseName) -> NodeIndex {
//             match self.license_to_idx.get(&lic) {
//                 Some(idx) => *idx,
//                 None => {
//                     let idx = self.graph.add_node(lic.clone());
//                     self.license_to_idx.insert(lic.clone(), idx);
//                     idx
//                 }
//             }
//         }
//         pub fn add_license(mut self, lic: LicenseName) -> Self {
//             self.add_license_(lic);
//             self
//         }
//         pub fn add_alias_(
//             &mut self,
//             left: LicenseName,
//             right: LicenseName,
//             relation: LicenseRelation,
//         ) -> EdgeIndex {
//             let left_idx = self.add_license_(left);
//             let right_idx = self.add_license_(right);
//             let e1 = self.graph.add_edge(left_idx, right_idx, relation);
//             e1
//         }
//         pub fn add_alias(
//             mut self,
//             left: LicenseName,
//             right: LicenseName,
//             relation: LicenseRelation,
//         ) -> Self {
//             self.add_alias_(left, right, relation);
//             self
//         }
//         pub fn get_component(self) -> Vec<Vec<LicenseName>> {
//             let idx_components = tarjan_scc(&self.graph);
//             idx_components
//                 .into_iter()
//                 // TODO: sorting within strongly connected components is not doing anything
//                 // .map(|mut idxs| {
//                 //     idxs.sort_by(|a, b| {
//                 //         match self.graph.find_edge(*a, *b) {
//                 //             Some(_) => Some(Ordering::Greater),
//                 //             None => None
//                 //         }.unwrap()
//                 //     });
//                 //     idxs
//                 // })
//                 // TODO: add all weekly connected nodes first
//                 .map(|idxs| {
//                     idxs.iter()
//                         .filter_map(|idx| self.graph.node_weight(*idx))
//                         .map(|license_name| license_name.clone())
//                         .collect()
//                 })
//                 .collect()
//         }
//         pub fn get_licenses_dot(&self) -> String {
//             let dot = Dot::with_config(&self.graph, &[]);
//             format!("{:?}", dot)
//         }
//     }
//     impl fmt::Debug for State {
//         fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
//             f.debug_struct("State")
//                 .field("graph", &self.graph)
//                 .field("license_statements", &self.license_statements)
//                 .field(
//                     "license_relation_statements",
//                     &self.license_relation_statements,
//                 )
//                 .finish()
//         }
//     }
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

pub fn demo<'a>() -> graph::LicenseGraph<'a> {
    static ORIGIN: &'static graph::Origin = &graph::Origin::new_with_file(
        "Origin_name",
        "https://domain.invalid/license.txt",
        Option::None,
    );
    graph::LicenseGraph::new()
        .add_aliases(
            vec![
                core::LicenseName::new("MIT License"),
                core::LicenseName::new("MIT"),
            ],
            &ORIGIN,
        )
        .add_aliases(
            vec![
                core::LicenseName::new("The MIT"),
                core::LicenseName::new("mit"),
            ],
            &ORIGIN,
        )
}

#[cfg(test)]
mod tests {
    use super::core::*;
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
        // s.consistency_check();
        println!("{s:#?}");
    }
}
