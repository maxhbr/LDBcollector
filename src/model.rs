use multimap::MultiMap;
use petgraph::algo::has_path_connecting;
use petgraph::dot::{Config, Dot};
use petgraph::graph::{Edge, EdgeIndex, Frozen, Node, NodeIndex};
use petgraph::stable_graph::StableGraph;
use serde::Serialize;
use serde_derive::{Deserialize, Serialize};
use serde_json::{Result, Value};
use std::collections::hash_map::DefaultHasher;
use std::collections::HashMap;
use std::fmt;
use std::hash::{Hash, Hasher};

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
//## Origin
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct Origin {
    pub name: String,
    // data_license: Option<LicenseItem>, // TODO
    pub file: Option<String>,
    pub url: Option<String>,
}

impl Origin {
    pub fn new(name: &str) -> Self {
        Self {
            name: String::from(name),
            file: Option::None,
            url: Option::None,
        }
    }
    pub fn new_with_file(name: &str, file: &str) -> Self {
        Self {
            name: String::from(name),
            file: Option::Some(String::from(file)),
            url: Option::None,
        }
    }
    pub fn new_with_url(name: &str, url: &str) -> Self {
        Self {
            name: String::from(name),
            file: Option::None,
            url: Option::Some(String::from(url)),
        }
    }
}

pub trait HasOrigin<'a> {
    fn get_origin(&self) -> &'a Origin;
}
//## end Origin
//#############################################################################

//#############################################################################
//## start License Data
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub enum LicenseIdentifier {
    LicenseName(LicenseName)
}
impl LicenseIdentifier {
    pub fn new(name: &str) -> Self {
        Self::LicenseName(LicenseName::new(String::from(name)))
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub enum LicenseType {
    PublicDomain (Option<String>),
    Permissive (Option<String>),
    Copyleft (Option<String>),
    WeaklyProtective (Option<String>),
    StronglyProtective (Option<String>),
    NetworkProtective (Option<String>),
    Unknown (Option<String>),
    Unlicensed (Option<String>),
}
impl LicenseType{
    fn get_names_for_type(&self) -> Vec<&str> {
        match self {
            LicenseType::PublicDomain(_) => vec!( "PublicDomain", "Public Domain" ),
            LicenseType::Permissive(_) => vec!( "Permissive" ),
            LicenseType::Copyleft(_) => vec!("Copyleft"),
            LicenseType::WeaklyProtective(_) => vec!( "WeaklyProtective", "Weakly Protective", "weak"),
            LicenseType::StronglyProtective(_) => vec!( "StronglyProtective", "Strongly Protective", "strong"),
            LicenseType::NetworkProtective(_) => vec!( "NetworkProtective", "Network Protective", "network"),
            LicenseType::Unlicensed(_) => vec!( "Unlicensed"),
            LicenseType::Unknown(_) => vec!( "Unknown"),
        }
    }

    fn type_matches_type(self, needle: &str) -> Option<Self> {
        let needle_lower = needle.to_lowercase();
        let matches = self.get_names_for_type()
            .iter()
            .map(|s| s.to_lowercase())
            .any(|s| s == needle_lower);
        if matches {
            Option::Some(self)
        } else {
            Option::None
        }
    }

    pub fn new(ty: &str) -> Self {
        if let Option::Some(new) = Self::PublicDomain(Option::None).type_matches_type(ty) {
            new
        } else if let Option::Some(new) = Self::Permissive(Option::None).type_matches_type(ty) {
            new
        } else if let Option::Some(new) = Self::Copyleft(Option::None).type_matches_type(ty) {
            new
        } else if let Option::Some(new) = Self::WeaklyProtective(Option::None).type_matches_type(ty) {
            new
        } else if let Option::Some(new) = Self::StronglyProtective(Option::None).type_matches_type(ty) {
            new
        } else if let Option::Some(new) = Self::NetworkProtective(Option::None).type_matches_type(ty) {
            new
        } else if let Option::Some(new) = Self::Unlicensed(Option::None).type_matches_type(ty) {
            new
        } else {
            let ty_str = String::from(ty);
            Self::Unknown(Option::Some(ty_str))
        }
    }
}
impl core::fmt::Display for LicenseType {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "{}", self.get_names_for_type()[0])
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub enum LicenseData {
    LicenseIdentifier(LicenseIdentifier),
    LicenseType(LicenseType),
    LicenseText(String),
    LicenseFlag(String),
}
impl LicenseData {
    pub fn license_name(name: &str) -> Self {
        LicenseData::LicenseIdentifier(LicenseIdentifier::new(name))
    }
    pub fn license_type(ty: &str) -> Self {
        LicenseData::LicenseType(LicenseType::new(ty))
    }
    pub fn license_text(text: &str) -> Self {
        LicenseData::LicenseText(String::from(text))
    }
    pub fn license_flag(flag: &str) -> Self {
        LicenseData::LicenseFlag(String::from(flag))
    }
}
//## end License Data
//#############################################################################

#[derive(Clone, Eq, PartialEq, Serialize, Deserialize)]
pub enum LicenseGraphNode {
    Data(LicenseData),
    Note(String),
    URL(String),
    Statement { statement_content: String },
    StatementRule { statement_content: String },
    StatementJson { statement_content: Value },
}
impl LicenseGraphNode {
    pub fn license_name(name: &str) -> Self {
        Self::Data(LicenseData::license_name(name))
    }
    pub fn license_type(ty: &str) -> Self {
        Self::Data(LicenseData::license_type(ty))
    }
    pub fn license_text(text: &str) -> Self {
        Self::Data(LicenseData::license_text(text))
    }
    pub fn license_flag(text: &str) -> Self {
        Self::Data(LicenseData::license_flag(text))
    }
    pub fn note(note: &str) -> Self {
        Self::Note(String::from(note))
    }
    pub fn url(url: &str) -> Self {
        Self::URL(String::from(url))
    }



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
            Self::Data(d) => {
                write!(f, "$DATA")
            }
            Self::Note (_) => {
                write!(f, "$NOTE")
            }
            Self::URL (url) => {
                write!(f, "{}", url)
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
                write!(f, "$JSON")
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
    Noop {},
    AddNodes {
        nodes: Vec<LicenseGraphNode>,
    },
    AddEdge {
        lefts: Vec<LicenseGraphNode>,
        rights: Box<LicenseGraphBuilderTask>,
        edge: LicenseGraphEdge,
    },
    AddEdgeLeft {
        lefts: Vec<LicenseGraphNode>,
        rights: Box<LicenseGraphBuilderTask>,
        edge: LicenseGraphEdge,
    },
    AddEdgeUnion {
        lefts: Vec<LicenseGraphNode>,
        rights: Box<LicenseGraphBuilderTask>,
        edge: LicenseGraphEdge,
    },
    JoinTasks {
        tasks: Vec<LicenseGraphBuilderTask>,
    },
}
impl LicenseGraphBuilderTask {
    pub fn mk_aliases_task(best: String, other_names: Vec<String>) -> Self {
        LicenseGraphBuilderTask::AddEdge {
            lefts: vec![LicenseGraphNode::license_name(&best)],
            rights: Box::new(LicenseGraphBuilderTask::AddNodes {
                nodes: other_names
                    .iter()
                    .map(|other_name| LicenseGraphNode::license_name(other_name))
                    .collect(),
            }),
            edge: LicenseGraphEdge::Same,
        }
    }
}
impl Hash for LicenseGraphBuilderTask {
    fn hash<H: Hasher>(&self, state: &mut H) {
        format!("{:?}", self).hash(state)
    }
}

#[derive(Clone)]
pub struct LicenseGraph {
    pub graph: StableGraph<LicenseGraphNode, LicenseGraphEdge>,
    pub node_origins: MultiMap<NodeIndex, Origin>,
    pub edge_origins: MultiMap<EdgeIndex, Origin>,
    accomplished_tasks: HashMap<u64, Vec<NodeIndex>>,
}
impl LicenseGraph {
    pub fn new() -> Self {
        Self {
            graph: StableGraph::<LicenseGraphNode, LicenseGraphEdge>::new(),
            node_origins: MultiMap::new(),
            edge_origins: MultiMap::new(),
            accomplished_tasks: HashMap::new(),
        }
    }

    pub fn get_internal_graph(&self) -> &StableGraph<LicenseGraphNode, LicenseGraphEdge> {
        &self.graph
    }

    fn get_idxs_of_node(&self, node: &LicenseGraphNode) -> Vec<NodeIndex> {
        self.graph
            .node_indices()
            .filter_map(|idx|
                self.graph.node_weight(idx)
                    .filter(|weight| *weight == node)
                    .map(|_| idx))
            .collect()
    }

    pub fn get_idxs_of_license(&self, license_name: String) -> Vec<NodeIndex> {
        let node = LicenseGraphNode::license_name(&license_name);
        self.get_idxs_of_node(&node)
    }

    pub fn focus(&self, license_name: String) -> Self {
        let mut s = self.clone();

        let root_idxs = self.get_idxs_of_license(license_name);

        s.graph.retain_nodes(|frozen_s, idx: NodeIndex| {
            root_idxs.iter()
                .any(|root_idx| {
                    let incomming = has_path_connecting(&self.graph, idx, *root_idx, Option::None);
                    let outgoing = has_path_connecting(&self.graph, *root_idx, idx, Option::None);
                    incomming || outgoing
                })
        });
        s.node_origins
            .retain(|idx, _| s.graph.node_weight(*idx).is_some());
        s.edge_origins
            .retain(|idx, _| s.graph.edge_weight(*idx).is_some());
        s
    }

    fn add_node(&mut self, node: &LicenseGraphNode) -> NodeIndex {
        let idxs = self.get_idxs_of_node(&node);
        if idxs.len() > 0 {
            *idxs.iter().next().unwrap()
        } else {
            let idx = self.graph.add_node(node.clone());
            idx
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
        match self.node_origins.get_vec(&idx) {
            Option::Some(vec) => {
                if !vec.contains(origin) {
                    self.node_origins.insert(idx, origin.clone())
                }
            }
            Option::None {} => self.node_origins.insert(idx, origin.clone()),
        };
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
                self.edge_origins.insert(idx, origin.clone());
                idx
            })
            .collect()
    }

    pub fn apply_task(
        &mut self,
        task: &LicenseGraphBuilderTask,
        origin: &'static Origin,
    ) -> Vec<NodeIndex> {
        let mut hasher = DefaultHasher::new();
        task.hash(&mut hasher);
        let hash = hasher.finish();

        match self.accomplished_tasks.get(&hash) {
            Option::Some(idxs) => idxs.clone(),
            Option::None {} => {
                let idxs = match task {
                    LicenseGraphBuilderTask::Noop {} => vec![],
                    LicenseGraphBuilderTask::AddNodes { nodes } => nodes
                        .iter()
                        .map(|node| self.add_node_with_origin(node, origin))
                        .collect(),
                    LicenseGraphBuilderTask::AddEdge {
                        lefts,
                        rights,
                        edge,
                    } => {
                        let right_idxs = self.apply_task(rights, origin);
                        lefts
                            .iter()
                            .map(|left| {
                                let left_idx = self.add_node_with_origin(left, origin);
                                self.add_edges_with_origin(
                                    left_idx,
                                    right_idxs.clone(),
                                    edge.clone(),
                                    origin,
                                );
                                left_idx
                            })
                            .collect()
                    }
                    LicenseGraphBuilderTask::AddEdgeLeft {
                        lefts,
                        rights,
                        edge,
                    } => {
                        let right_idxs = self.apply_task(rights, origin);
                        lefts.iter().for_each(|left| {
                            let left_idx = self.add_node_with_origin(left, origin);
                            self.add_edges_with_origin(
                                left_idx,
                                right_idxs.clone(),
                                edge.clone(),
                                origin,
                            );
                        });
                        right_idxs
                    }
                    LicenseGraphBuilderTask::AddEdgeUnion {
                        lefts,
                        rights,
                        edge,
                    } => {
                        let right_idxs = self.apply_task(rights, origin);
                        let left_idxs = lefts
                            .iter()
                            .map(|left| {
                                let left_idx = self.add_node_with_origin(left, origin);
                                self.add_edges_with_origin(
                                    left_idx,
                                    right_idxs.clone(),
                                    edge.clone(),
                                    origin,
                                );
                                left_idx
                            })
                            .collect();
                        [right_idxs, left_idxs].concat()
                    }
                    LicenseGraphBuilderTask::JoinTasks { tasks } => tasks
                        .iter()
                        .flat_map(|task| self.apply_task(task, origin))
                        .collect(),
                };
                self.accomplished_tasks.insert(hash, idxs.clone());
                idxs
            }
        }
    }

    pub fn get_license_names(&self) -> Vec<&LicenseName> {
        self.graph
            .node_weights()
            .filter_map(|w| match w {
                LicenseGraphNode::Data(data) => {
                    match data {
                        LicenseData::LicenseIdentifier(license_identifier) => {
                            match license_identifier {
                                LicenseIdentifier::LicenseName(license_name) => Option::Some(license_name),
                            }
                        },
                        LicenseData::LicenseType(_) => Option::None {},
                        LicenseData::LicenseText(_) => Option::None {},
                        LicenseData::LicenseFlag(_) => Option::None {},
                    }
                }
                _ => Option::None {},
            })
            .collect()
    }

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

pub trait Source {
    fn get_origin(&self) -> Origin;
    fn get_tasks(&self) -> Vec<LicenseGraphBuilderTask>;
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum LicenseGraphBuilder {
    Init,
    Add {
        prev: Box<LicenseGraphBuilder>,
        origin: Box<Origin>,
        tasks: Vec<LicenseGraphBuilderTask>,
    },
}
impl LicenseGraphBuilder {
    pub fn new() -> Self {
        Self::Init
    }
    pub fn add_tasks(self, tasks: Vec<LicenseGraphBuilderTask>, origin: Box<Origin>) -> Self {
        Self::Add {
            prev: Box::new(self),
            origin,
            tasks,
        }
    }

    pub fn add_unboxed_source(self, source: &dyn Source) -> Self {
        self.add_tasks(source.get_tasks(), Box::new(source.get_origin().clone()))
    }

    pub fn add_source(self, source: &Box<dyn Source>) -> Self {
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
                log::debug!("apply from origin {}", origin.name);
                tasks.iter().fold(prev_graph, |mut prev_graph, task| {
                    prev_graph.apply_task(task, Box::leak(origin.clone()));
                    prev_graph
                })
            }
        }
    }
}

pub fn demo() -> LicenseGraph {
    let origin: &Origin =
        &Origin::new_with_file("Origin_name", "https://domain.invalid/license.txt");

    let add_nodes_task = LicenseGraphBuilderTask::AddNodes {
        nodes: vec![LicenseGraphNode::license_name("MIT")],
    };
    let add_alias_task = LicenseGraphBuilderTask::AddEdge {
        lefts: vec![LicenseGraphNode::license_name("MIT License")],
        rights: Box::new(add_nodes_task),
        edge: LicenseGraphEdge::Same,
    };

    LicenseGraphBuilder::new()
        .add_tasks(vec![add_alias_task], Box::new(origin.clone()))
        .build()
}

#[cfg(test)]
mod tests {
    use crate::model::*;

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
            LicenseGraphNode::license_name("MIT")
            ,
            LicenseGraphNode::license_name("mIt")
        );
    }

    #[test]
    fn demo_should_run() {
        let s = demo();
        // s.consistency_check();
        println!("{s:#?}");
    }
}
