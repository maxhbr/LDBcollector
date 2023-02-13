use serde_derive::{Deserialize, Serialize};
use spdx::LicenseItem;
use std::fmt;
use std::hash::{Hash, Hasher};

pub mod core {
    use super::*;

    //#############################################################################
    //## LicenseName
    #[derive(Debug, Clone, Serialize, Deserialize)]
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
    use petgraph::algo::has_path_connecting;
    use petgraph::dot::{Config, Dot};
    use petgraph::graph::{Edge, EdgeIndex, Frozen, Node, NodeIndex};
    use petgraph::stable_graph::StableGraph;
    use serde::Serialize;
    use serde_json::{Result, Value};

    //#############################################################################
    //## Origin
    #[derive(Debug, Clone, Serialize, Deserialize)]
    pub struct Origin<'a> {
        name: &'a str,
        // data_license: Option<LicenseItem>, // TODO
        file: Option<&'a str>,
        url: Option<&'a str>,
    }

    impl<'a> Origin<'a> {
        pub const fn new(name: &'a str) -> Self {
            Self {
                name,
                file: Option::None,
                url: Option::None,
            }
        }
        pub const fn new_with_file(name: &'a str, file: &'a str) -> Self {
            Self {
                name,
                file: Option::Some(file),
                url: Option::None,
            }
        }
        pub const fn new_with_url(name: &'a str, url: &'a str) -> Self {
            Self {
                name,
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

    #[derive(Clone, Eq, PartialEq, Serialize, Deserialize)]
    pub enum LicenseGraphNode {
        LicenseNameNode { license_name: LicenseName },
        LicenseTextNode { license_text: String },
        Statement { statement_content: String },
        StatementRule { statement_content: String },
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
                Self::StatementRule {
                    statement_content: _,
                } => {
                    write!(f, "$RULE")
                }
                Self::StatementJson { statement_content } => {
                    write!(f, "{:#?}", statement_content)
                }
            }
        }
    }

    #[derive(Debug, Clone, Serialize, Deserialize)]
    pub enum LicenseGraphEdge {
        Same,
        Better,
        HintsTowards,
        AppliesTo,
    }

    #[derive(Debug, Clone, Serialize, Deserialize)]
    pub enum LicenseGraphBuilderTask {
        AddNodes {
            nodes: Vec<LicenseGraphNode>,
        },
        AddEdge {
            lefts: Vec<LicenseGraphNode>,
            rights: Box<LicenseGraphBuilderTask>,
            edge: LicenseGraphEdge,
        },
    }

    #[derive(Clone)]
    pub struct LicenseGraph {
        pub graph: StableGraph<LicenseGraphNode, LicenseGraphEdge>,
        node_origins: MultiMap<NodeIndex, &'static Origin<'static>>,
        edge_origins: MultiMap<EdgeIndex, &'static Origin<'static>>,
    }
    impl LicenseGraph {
        pub fn new() -> Self {
            Self {
                graph: StableGraph::<LicenseGraphNode, LicenseGraphEdge>::new(),
                node_origins: MultiMap::new(),
                edge_origins: MultiMap::new(),
            }
        }

        fn get_idx_of_node(&self, node: &LicenseGraphNode) -> Option<NodeIndex> {
            self.graph
                .node_indices()
                .filter_map(|idx| {
                    self.graph
                        .node_weight(idx)
                        .map(|weight| (idx, weight.clone()))
                })
                .filter(|(_, weight)| *node == *weight)
                .map(|(idx, _)| idx.clone())
                .next()
        }

        fn get_idx_of_license(&self, license_name: LicenseName) -> Option<NodeIndex> {
            let node = LicenseGraphNode::LicenseNameNode {
                license_name: license_name,
            };
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

        fn add_node(&mut self, node: &LicenseGraphNode) -> NodeIndex {
            match self.get_idx_of_node(&node) {
                Some(idx) => idx,
                None => {
                    let idx = self.graph.add_node(node.clone());
                    idx
                }
            }
        }
        fn add_edges(
            &mut self,
            left: NodeIndex,
            rights: Vec<NodeIndex>,
            edge: LicenseGraphEdge,
        ) -> Vec<EdgeIndex> {
            rights
                .into_iter()
                .map(|right| self.graph.add_edge(left, right, edge.clone()))
                .collect()
        }

        fn add_node_with_origin(
            &mut self,
            node: &LicenseGraphNode,
            origin: &'static Origin,
        ) -> NodeIndex {
            let idx = self.add_node(node);
            self.node_origins.insert(idx, origin);
            idx
        }
        fn add_edges_with_origin(
            &mut self,
            left: NodeIndex,
            rights: Vec<NodeIndex>,
            edge: LicenseGraphEdge,
            origin: &'static Origin,
        ) -> Vec<EdgeIndex> {
            self.add_edges(left, rights, edge)
                .into_iter()
                .map(|idx| {
                    self.edge_origins.insert(idx, origin);
                    idx
                })
                .collect()
        }

        pub fn apply_task(
            &mut self,
            task: &LicenseGraphBuilderTask,
            origin: &'static Origin,
        ) -> Vec<NodeIndex> {
            match task {
                LicenseGraphBuilderTask::AddNodes { nodes } => nodes
                    .iter()
                    .map(|node| self.add_node_with_origin(node, origin))
                    .collect(),
                LicenseGraphBuilderTask::AddEdge {
                    lefts,
                    rights,
                    edge,
                } => lefts
                    .iter()
                    .map(|left| {
                        let left_idx = self.add_node_with_origin(left, origin);
                        let right_idxs = self.apply_task(rights, origin);
                        self.add_edges_with_origin(left_idx, right_idxs, edge.clone(), origin);
                        left_idx
                    })
                    .collect(),
            }
        }

        // pub fn add_license(mut self, lic: LicenseName, origin: &'static Origin) -> Self {
        //     self.add_node_with_origin(
        //         LicenseGraphNode::LicenseNameNode { license_name: lic },
        //         origin,
        //     );
        //     self
        // }
        // pub fn add_relation(
        //     mut self,
        //     left: LicenseName,
        //     rights: Vec<LicenseName>,
        //     edge: LicenseGraphEdge,
        //     origin: &'static Origin,
        // ) -> Self {
        //     self.add_edges_with_origin(
        //         LicenseGraphNode::LicenseNameNode { license_name: left },
        //         rights
        //             .into_iter()
        //             .map(|o| LicenseGraphNode::LicenseNameNode {
        //                 license_name: o.clone(),
        //             })
        //             .collect(),
        //         edge,
        //         origin,
        //     );
        //     self
        // }
        // pub fn add_aliases(mut self, names: Vec<LicenseName>, origin: &'static Origin) -> Self {
        //     match names.as_slice() {
        //         [] => self,
        //         [name] => {
        //             self.add_node_with_origin(
        //                 LicenseGraphNode::LicenseNameNode {
        //                     license_name: name.clone(),
        //                 },
        //                 origin,
        //             );
        //             self
        //         }
        //         [best, others @ ..] => others.iter().fold(self, |acc, other| {
        //             acc.add_relation(
        //                 other.clone(),
        //                 vec![best.clone()],
        //                 LicenseGraphEdge::Same,
        //                 origin,
        //             )
        //         }),
        //     }
        // }
        // pub fn add_relational_fact(
        //     mut self,
        //     left: LicenseGraphNode,
        //     rights: Vec<LicenseName>,
        //     origin: &'static Origin,
        // ) -> Self {
        //     self.add_edges_with_origin(
        //         left,
        //         rights
        //             .into_iter()
        //             .map(|o| LicenseGraphNode::LicenseNameNode { license_name: o })
        //             .collect(),
        //         LicenseGraphEdge::AppliesTo,
        //         origin,
        //     );
        //     self
        // }
        pub fn get_as_dot(&self) -> String {
            let dot = Dot::with_config(&self.graph, &[]);
            format!("{:?}", dot)
        }
    }
    impl fmt::Debug for LicenseGraph {
        fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
            f.debug_struct("State").field("graph", &self.graph).finish()
        }
    }

    trait Source {
        fn get_origin(&self) -> Origin<'static>;
        fn get_tasks(&self) -> Vec<LicenseGraphBuilderTask>;
    }

    #[derive(Debug, Clone, Serialize, Deserialize)]
    #[serde(bound(deserialize = "'de: 'static"))]
    pub enum LicenseGraphBuilder {
        Init,
        Add {
            prev: Box<LicenseGraphBuilder>,
            origin: Box<Origin<'static>>,
            tasks: Vec<LicenseGraphBuilderTask>,
        },
    }
    impl LicenseGraphBuilder {
        pub fn new() -> Self {
            Self::Init
        }
        pub fn add_tasks(
            self,
            tasks: Vec<LicenseGraphBuilderTask>,
            origin: Box<Origin<'static>>,
        ) -> Self {
            Self::Add {
                prev: Box::new(self),
                origin: origin,
                tasks: tasks,
            }
        }

        pub fn add_source(self, source: &dyn Source) -> Self {
            self.add_tasks(source.get_tasks(), Box::new(source.get_origin().clone()))
        }

        pub fn build(self) -> LicenseGraph {
            match self {
                Self::Init => LicenseGraph::new(),
                Self::Add {
                    prev,
                    origin,
                    tasks,
                } => {
                    let prev_graph = prev.build();
                    tasks
                        .iter()
                        .fold(prev_graph, |mut prev_graph, task| {
                            prev_graph.apply_task(task, Box::leak(origin.clone()));
                            prev_graph
                        })
                }
            }
        }
    }
}

pub fn demo() -> graph::LicenseGraph {
    static ORIGIN: &'static graph::Origin =
        &graph::Origin::new_with_file("Origin_name", "https://domain.invalid/license.txt");

    let add_nodes_task = 
            graph::LicenseGraphBuilderTask::AddNodes {
                nodes: vec!(
                graph::LicenseGraphNode::LicenseNameNode{ license_name: core::LicenseName::new(String::from("MIT")) },
            )};
    let add_alias_task = graph::LicenseGraphBuilderTask::AddEdge {
        lefts: vec!(
            graph::LicenseGraphNode::LicenseNameNode{ license_name: core::LicenseName::new(String::from("MIT License")) }
        ),
        rights: Box::new(add_nodes_task),
        edge: graph::LicenseGraphEdge::Same
     };

    graph::LicenseGraphBuilder::new()
        .add_tasks(vec!(
            add_alias_task
        ), Box::new(ORIGIN.clone()))
        .build()
    // graph::LicenseGraph::new()
    //     .add_aliases(
    //         vec![
    //             core::LicenseName::new(String::from("MIT License")),
    //             core::LicenseName::new(String::from("MIT")),
    //         ],
    //         &ORIGIN,
    //     )
    //     .add_aliases(
    //         vec![
    //             core::LicenseName::new(String::from("The MIT")),
    //             core::LicenseName::new(String::from("mit")),
    //         ],
    //         &ORIGIN,
    //     )
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
            LicenseGraphNode::LicenseNameNode {
                license_name: LicenseName::new(String::from("MIT"))
            },
            LicenseGraphNode::LicenseNameNode {
                license_name: LicenseName::new(String::from("mIt"))
            }
        );
    }

    #[test]
    fn demo_should_run() {
        let s = demo();
        // s.consistency_check();
        println!("{s:#?}");
    }
}
