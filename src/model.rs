use spdx::{LicenseItem};
use std::fmt;
use std::hash::{Hash, Hasher};

pub mod core {
    use super::*;

    //#############################################################################
    //## LicenseName
    #[derive(Debug, Clone)]
    pub struct LicenseName(String);
    impl<'a> LicenseName {
        pub fn new(name: String) -> Self {
            Self(name)
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
    //## end LicenseName
    //#############################################################################
}

pub mod graph {
    use super::core::*;
    use super::*;
    use either::{Either, Left, Right};
    use multimap::MultiMap;
    use petgraph::algo::{has_path_connecting};
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

    #[derive(Clone,Eq, PartialEq)]
    pub enum LicenseGraphNode {
        LicenseNameNode { license_name: LicenseName },
        LicenseTextNode { license_text: String },
        Statement { statement_content: String },
        StatementJson { statement_content: Value },
    }
    impl<'a> LicenseGraphNode {
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
    impl fmt::Debug for LicenseGraphNode {
        fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
            match self {
                Self::LicenseNameNode { license_name } => {
                    write!(f, "{}", license_name)
                }
                Self::LicenseTextNode { license_text: _ } => {
                    write!(f, "$TEXT")
                }
                Self::Statement { statement_content } => {
                    write!(f, "{}", statement_content)
                }
                Self::StatementJson { statement_content } => {
                    write!(f, "{:#?}", statement_content)
                }
            }
        }
    }

    #[derive(Debug, Clone)]
    pub enum LicenseGraphEdge {
        Same,
        Better,
        HintsTowards,
        AppliesTo,
    }

    #[derive(Clone)]
    pub struct LicenseGraph<'a> {
        pub graph: StableGraph<LicenseGraphNode, LicenseGraphEdge>,
        node_origins: MultiMap<NodeIndex, &'a Origin<'a>>,
        edge_origins: MultiMap<EdgeIndex, &'a Origin<'a>>,
    }
    impl<'a> LicenseGraph<'a> {
        pub fn new() -> Self {
            Self {
                graph: StableGraph::<LicenseGraphNode, LicenseGraphEdge>::new(),
                node_origins: MultiMap::new(),
                edge_origins: MultiMap::new(),
            }
        }

        fn get_idx_of_node(&self, node: &LicenseGraphNode) -> Option<NodeIndex> {
            self.graph.node_indices()
                .filter_map(|idx| {
                    self.graph.node_weight(idx)
                        .map(|weight| (idx,weight.clone()))
                })
                .filter(|(_,weight)| *node == *weight)
                .map(|(idx,_)| idx.clone())
                .next()
        }

        fn get_idx_of_license(&self, license_name: LicenseName) -> Option<NodeIndex> {
            let node = LicenseGraphNode::LicenseNameNode { license_name: license_name };
            self.get_idx_of_node(&node)
        }

        pub fn focus(self, license_name: LicenseName) -> Self {
            let mut s = self.clone();

            let root_idx = self.get_idx_of_license(license_name).unwrap();

            s.graph.retain_nodes(|frozen_s, idx: NodeIndex| {
                let incomming = has_path_connecting(&self.graph, idx, root_idx, Option::None);
                let outgoing = has_path_connecting(&self.graph, root_idx, idx, Option::None);
                incomming || outgoing
            });
            s.node_origins
                .retain(|idx, _| s.graph.node_weight(*idx).is_some());
            s.edge_origins
                .retain(|idx, _| s.graph.edge_weight(*idx).is_some());
            s
        }

        fn add_node(&mut self, node: LicenseGraphNode) -> NodeIndex {
            match self.get_idx_of_node(&node) {
                Some(idx) => idx,
                None => {
                    let idx = self.graph.add_node(node);
                    idx
                }
            }
        }
        fn add_edges(
            &mut self,
            left: LicenseGraphNode,
            rights: Vec<LicenseGraphNode>,
            edge: LicenseGraphEdge,
        ) -> Vec<EdgeIndex> {
            let left_idx = self.add_node(left);
            rights
                .into_iter()
                .map(|right| {
                    let right_idx = self.add_node(right);

                    // (&(self.graph)).edges_connecting(left_idx, right_idx)
                    //     .collect();

                    let idx = self.graph.add_edge(left_idx, right_idx, edge.clone());
                    idx
                })
                .collect()
        }

        fn add_node_with_origin(
            &mut self,
            node: LicenseGraphNode,
            origin: &'a Origin,
        ) -> NodeIndex {
            let idx = self.add_node(node);
            self.node_origins.insert(idx, origin);
            idx
        }
        fn add_edges_with_origin(
            &mut self,
            left: LicenseGraphNode,
            rights: Vec<LicenseGraphNode>,
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

        pub fn add_license(mut self, lic: LicenseName, origin: &'a Origin) -> Self {
            self.add_node_with_origin(
                LicenseGraphNode::LicenseNameNode { license_name: lic },
                origin,
            );
            self
        }
        pub fn add_relation(
            mut self,
            left: LicenseName,
            rights: Vec<LicenseName>,
            edge: LicenseGraphEdge,
            origin: &'a Origin,
        ) -> Self {
            self.add_edges_with_origin(
                LicenseGraphNode::LicenseNameNode { license_name: left },
                rights
                    .into_iter()
                    .map(|o| LicenseGraphNode::LicenseNameNode {
                        license_name: o.clone(),
                    })
                    .collect(),
                edge,
                origin,
            );
            self
        }
        pub fn add_aliases(mut self, names: Vec<LicenseName>, origin: &'a Origin) -> Self {
            match names.as_slice() {
                [] => self,
                [name] => {
                    self.add_node_with_origin(
                        LicenseGraphNode::LicenseNameNode {
                            license_name: name.clone(),
                        },
                        origin,
                    );
                    self
                }
                [best, others @ ..] => others.iter().fold(self, |acc, other| {
                    acc.add_relation(
                        other.clone(),
                        vec![best.clone()],
                        LicenseGraphEdge::Same,
                        origin,
                    )
                }),
            }
        }
        pub fn add_relational_fact(
            mut self,
            left: LicenseGraphNode,
            rights: Vec<LicenseName>,
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

pub fn demo<'a>() -> graph::LicenseGraph<'a> {
    static ORIGIN: &'static graph::Origin = &graph::Origin::new_with_file(
        "Origin_name",
        "https://domain.invalid/license.txt",
        Option::None,
    );
    graph::LicenseGraph::new()
        .add_aliases(
            vec![
                core::LicenseName::new(String::from("MIT License")),
                core::LicenseName::new(String::from("MIT")),
            ],
            &ORIGIN,
        )
        .add_aliases(
            vec![
                core::LicenseName::new(String::from("The MIT")),
                core::LicenseName::new(String::from("mit")),
            ],
            &ORIGIN,
        )
}

#[cfg(test)]
mod tests {
    use super::core::*;
    use super::graph::*;
    use super::*;

    #[test]
    fn license_name_tests() {
        assert_eq!(
            LicenseName::new(String::from("MIT")),
            LicenseName::new(String::from("MIT"))
        );
        assert_eq!(
            LicenseName::new(String::from("MIT")),
            LicenseName::new(String::from("mit"))
        );
        assert_eq!(
            LicenseName::new(String::from("MIT")),
            LicenseName::new(String::from("mIt"))
        );
    }

    #[test]
    fn license_name_statement_tests() {
        assert_eq!(
            LicenseGraphNode::LicenseNameNode{ license_name: LicenseName::new(String::from("MIT")) },
            LicenseGraphNode::LicenseNameNode{ license_name: LicenseName::new(String::from("mIt")) }
        );
    }

    #[test]
    fn demo_should_run() {
        let s = demo();
        // s.consistency_check();
        println!("{s:#?}");
    }
}
