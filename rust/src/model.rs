use multimap::MultiMap;
use petgraph::algo::has_path_connecting;
use petgraph::dot::{Config, Dot};
use petgraph::graph::{Edge, EdgeIndex, Frozen, Graph, Node, NodeIndex};
use petgraph::stable_graph::StableGraph;
use petgraph::visit::EdgeRef;
use serde_derive::{Deserialize, Serialize};
use std::collections::hash_map::DefaultHasher;
use std::collections::HashMap;
use std::error::Error;
use std::fmt;
use std::hash::{Hash, Hasher};

#[derive(thiserror::Error, Debug)]
pub enum MyError {
    #[error("Source contains no data")]
    Err(String),
    #[error("Read error")]
    ReadError { source: std::io::Error },
    #[error(transparent)]
    IOError(#[from] std::io::Error),
}

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
#[derive(Clone, Serialize, Deserialize)]
pub enum LicenseIdentifier {
    Name(String),
    Namespaced {
        namespace: String,
        name: Box<LicenseIdentifier>,
    },
}
impl LicenseIdentifier {
    pub fn new(full_name: &str) -> Self {
        match full_name.split(':').collect::<Vec<_>>().as_slice() {
            [] => Self::Name(String::from(full_name)),
            [start @ .., name] => {
                start
                    .iter()
                    .rev()
                    .fold(Self::Name(String::from(*name)), |acc, namespace| {
                        Self::Namespaced {
                            namespace: String::from(*namespace),
                            name: Box::new(acc),
                        }
                    })
            }
        }
    }
    pub fn new_namespaced(namespace: &str, name: &str) -> Self {
        Self::Namespaced {
            namespace: String::from(namespace),
            name: Box::new(Self::new(name)),
        }
    }
}
impl core::fmt::Display for LicenseIdentifier {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            LicenseIdentifier::Name(license_name) => write!(f, "{}", license_name),
            LicenseIdentifier::Namespaced { namespace, name } => {
                write!(f, "{}:{}", namespace, name)
            }
        }
    }
}
impl core::fmt::Debug for LicenseIdentifier {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            LicenseIdentifier::Name(license_name) => write!(f, "{}", license_name),
            LicenseIdentifier::Namespaced { namespace, name } => {
                write!(f, "{}:{}", namespace, name)
            }
        }
    }
}
impl PartialEq for LicenseIdentifier {
    fn eq(&self, other: &Self) -> bool {
        format!("{}", self).to_lowercase() == format!("{}", other).to_lowercase()
    }
}
impl Eq for LicenseIdentifier {}
impl Hash for LicenseIdentifier {
    fn hash<H: Hasher>(&self, state: &mut H) {
        format!("{}", self).to_lowercase().hash(state);
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq, Hash)]
pub enum LicenseType {
    PublicDomain(Option<String>),
    Permissive(Option<String>),
    Copyleft(Option<String>),
    WeaklyProtective(Option<String>),
    StronglyProtective(Option<String>),
    NetworkProtective(Option<String>),
    Unknown(Option<String>),
    Unlicensed(Option<String>),
}
impl LicenseType {
    fn get_names_for_type(&self) -> Vec<&str> {
        match self {
            LicenseType::PublicDomain(_) => vec!["PublicDomain", "Public Domain"],
            LicenseType::Permissive(_) => vec!["Permissive"],
            LicenseType::Copyleft(_) => vec!["Copyleft"],
            LicenseType::WeaklyProtective(_) => {
                vec!["WeaklyProtective", "Weakly Protective", "weak"]
            }
            LicenseType::StronglyProtective(_) => {
                vec!["StronglyProtective", "Strongly Protective", "strong"]
            }
            LicenseType::NetworkProtective(_) => {
                vec![
                    "NetworkProtective",
                    "Network Protective",
                    "network_copyleft",
                    "network",
                ]
            }
            LicenseType::Unlicensed(_) => vec!["Unlicensed"],
            LicenseType::Unknown(_) => vec!["Unknown"],
        }
    }

    fn type_matches_type(self, needle: &str) -> Option<Self> {
        let needle_lower = needle.to_lowercase();
        let matches = self
            .get_names_for_type()
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
        } else if let Option::Some(new) = Self::WeaklyProtective(Option::None).type_matches_type(ty)
        {
            new
        } else if let Option::Some(new) =
            Self::StronglyProtective(Option::None).type_matches_type(ty)
        {
            new
        } else if let Option::Some(new) =
            Self::NetworkProtective(Option::None).type_matches_type(ty)
        {
            new
        } else if let Option::Some(new) = Self::Unlicensed(Option::None).type_matches_type(ty) {
            new
        } else {
            let ty_str = String::from(ty);
            Self::Unknown(Option::Some(ty_str))
        }
    }
    pub fn get_optional(&self) -> &Option<String> {
        match self {
            LicenseType::PublicDomain(o) => o,
            LicenseType::Permissive(o) => o,
            LicenseType::Copyleft(o) => o,
            LicenseType::WeaklyProtective(o) => o,
            LicenseType::StronglyProtective(o) => o,
            LicenseType::NetworkProtective(o) => o,
            LicenseType::Unknown(o) => o,
            LicenseType::Unlicensed(o) => o,
        }
    }
}
impl core::fmt::Display for LicenseType {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        let main_name = self.get_names_for_type()[0];
        if let Option::Some(o) = self.get_optional() {
            write!(f, "{} ({})", main_name, o)
        } else {
            write!(f, "{}", main_name)
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq, Hash)]
pub enum LicenseData {
    LicenseIdentifier(LicenseIdentifier),
    LicenseType(LicenseType),
    LicenseText(String),
    LicenseFlag(String),
    LicenseRating(String),
}
impl LicenseData {
    pub fn license_name(name: &str) -> Self {
        LicenseData::LicenseIdentifier(LicenseIdentifier::new(name))
    }
    pub fn namespaced_license_name(namespace: &str, name: &str) -> Self {
        LicenseData::LicenseIdentifier(LicenseIdentifier::new_namespaced(namespace, name))
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
    pub fn license_rating(rating: &str) -> Self {
        LicenseData::LicenseRating(String::from(rating))
    }
}
//## end License Data
//#############################################################################

#[derive(Clone, Eq, PartialEq, Serialize, Deserialize, Hash)]
pub enum LicenseGraphNode {
    Data(LicenseData),
    Note(String),
    URL(String),
    Vec(Vec<LicenseGraphNode>),
    Raw(String),
    Statement { statement_content: String },
    StatementRule { statement_content: String },
}
impl LicenseGraphNode {
    pub fn license_name(name: &str) -> Self {
        Self::Data(LicenseData::license_name(name))
    }
    pub fn namespaced_license_name(namespace: &str, name: &str) -> Self {
        Self::Data(LicenseData::namespaced_license_name(namespace, name))
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
    pub fn license_rating(rating: &str) -> Self {
        Self::Data(LicenseData::license_rating(rating))
    }
    pub fn note(note: &str) -> Self {
        Self::Note(String::from(note))
    }
    pub fn url(url: &str) -> Self {
        Self::URL(String::from(url))
    }
    pub fn vec(vec: Vec<LicenseGraphNode>) -> Vec<LicenseGraphNode> {
        let len = vec.len();
        if len <= 1 {
            vec
        } else {
            vec![Self::Vec(vec)]
        }
    }
}
impl fmt::Debug for LicenseGraphNode {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            Self::Data(d) => match d {
                LicenseData::LicenseIdentifier(license_name) => write!(f, "{:?}", license_name),
                LicenseData::LicenseType(ty) => write!(f, "{}", ty),
                LicenseData::LicenseText(_) => write!(f, "$DATA:license_text"),
                LicenseData::LicenseFlag(flag) => write!(f, "$DATA:license_flag:{}", flag),
                LicenseData::LicenseRating(rating) => write!(f, "{}", rating),
            },
            Self::Note(_) => {
                write!(f, "$NOTE")
            }
            Self::URL(url) => {
                write!(f, "{}", url)
            }
            Self::Vec(vec) => {
                write!(f, "{:?}", vec)
            }
            Self::Raw(raw) => {
                write!(f, "$Raw")
            }
            Self::Statement { statement_content } => {
                write!(f, "{}", statement_content)
            }
            Self::StatementRule {
                statement_content: _,
            } => {
                write!(f, "$RULE")
            }
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
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
        left_pairs: Vec<(LicenseGraphEdge, Vec<LicenseGraphNode>)>,
        rights: Box<LicenseGraphBuilderTask>,
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
    pub fn new(nodes: Vec<LicenseGraphNode>) -> Self {
        Self::AddNodes { nodes }
    }
    pub fn new1(node: LicenseGraphNode) -> Self {
        Self::AddNodes { nodes: vec![node] }
    }
    pub fn edge(self, edge: LicenseGraphEdge, lefts: Vec<LicenseGraphNode>) -> Self {
        Self::AddEdge {
            left_pairs: vec![(edge, lefts)],
            rights: Box::new(self),
        }
    }
    pub fn edge1(self, edge: LicenseGraphEdge, lefts: LicenseGraphNode) -> Self {
        Self::AddEdge {
            left_pairs: vec![(edge, vec![lefts])],
            rights: Box::new(self),
        }
    }
    pub fn edge_add(self, edge: LicenseGraphEdge, lefts: Vec<LicenseGraphNode>) -> Self {
        match self {
            Self::AddEdge {
                mut left_pairs,
                rights,
            } => {
                left_pairs.push((edge, lefts));
                Self::AddEdge { left_pairs, rights }
            }
            _ => self.edge(edge, lefts),
        }
    }
    pub fn edge_add1(self, edge: LicenseGraphEdge, lefts: LicenseGraphNode) -> Self {
        match self {
            Self::AddEdge {
                mut left_pairs,
                rights,
            } => {
                left_pairs.push((edge, vec![lefts]));
                Self::AddEdge { left_pairs, rights }
            }
            _ => self.edge1(edge, lefts),
        }
    }
    pub fn edge_left(self, edge: LicenseGraphEdge, lefts: Vec<LicenseGraphNode>) -> Self {
        Self::AddEdgeLeft {
            lefts,
            rights: Box::new(self),
            edge,
        }
    }
    pub fn edge_union(self, edge: LicenseGraphEdge, lefts: Vec<LicenseGraphNode>) -> Self {
        Self::AddEdgeUnion {
            lefts,
            rights: Box::new(self),
            edge,
        }
    }
    pub fn join(tasks: Vec<LicenseGraphBuilderTask>) -> Self {
        Self::JoinTasks { tasks }
    }

    pub fn mk_aliases_task(best: String, other_names: Vec<String>) -> Self {
        LicenseGraphBuilderTask::AddEdgeLeft {
            lefts: other_names
                .iter()
                .map(|other_name| LicenseGraphNode::license_name(other_name))
                .collect(),
            rights: Box::new(LicenseGraphBuilderTask::AddNodes {
                nodes: vec![LicenseGraphNode::license_name(&best)],
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
    pub node_indexes: HashMap<LicenseGraphNode, NodeIndex>,
    pub node_origins: MultiMap<NodeIndex, Origin>,
    pub edge_origins: MultiMap<EdgeIndex, Origin>,
    accomplished_tasks: HashMap<u64, Vec<NodeIndex>>,
}
impl LicenseGraph {
    pub fn new() -> Self {
        Self {
            graph: StableGraph::<LicenseGraphNode, LicenseGraphEdge>::new(),
            node_indexes: HashMap::new(),
            node_origins: MultiMap::new(),
            edge_origins: MultiMap::new(),
            accomplished_tasks: HashMap::new(),
        }
    }

    pub fn get_internal_graph(&self) -> &StableGraph<LicenseGraphNode, LicenseGraphEdge> {
        &self.graph
    }

    fn get_idx_of_node(&self, node: &LicenseGraphNode) -> Option<NodeIndex> {
        self.node_indexes.get(node).copied()
    }

    pub fn get_idx_of_license(&self, license_name: &str) -> Option<NodeIndex> {
        let node = LicenseGraphNode::license_name(license_name);
        self.get_idx_of_node(&node)
    }

    pub fn focus_many(&self, license_names: Vec<&str>) -> Result<Self, Box<dyn Error>> {
        let mut s = self.clone();

        let root_idxs: Vec<NodeIndex> = license_names
            .iter()
            .filter_map(|license_name| self.get_idx_of_license(license_name))
            .collect();

        s.graph.retain_nodes(|_frozen_s, idx: NodeIndex| {
            root_idxs.iter().any(|root_idx| {
                let incoming = has_path_connecting(&self.graph, idx, *root_idx, Option::None);
                let outgoing = has_path_connecting(&self.graph, *root_idx, idx, Option::None);
                incoming || outgoing
            })
        });
        s.node_origins
            .retain(|idx, _| s.graph.node_weight(*idx).is_some());
        s.edge_origins
            .retain(|idx, _| s.graph.edge_weight(*idx).is_some());
        Ok(s)
    }

    pub fn focus(&self, license_name: &str) -> Result<Self, Box<dyn Error>> {
        self.focus_many(vec![license_name])
    }

    fn add_node(&mut self, node: &LicenseGraphNode) -> NodeIndex {
        if let Option::Some(idx) = self.get_idx_of_node(&node) {
            idx
        } else {
            let idx = self.graph.add_node(node.clone());
            self.node_indexes.insert(node.clone(), idx);
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
            .map(|right| {
                match self
                    .graph
                    .edges_connecting(left, right)
                    .filter(|e| *e.weight() == edge)
                    .map(|e| e.id())
                    .next()
                {
                    Some(idx) => idx,
                    None => self.graph.add_edge(left, right, edge.clone()),
                }

                // let idx = self.graph.add_edge(left, right, edge.clone());
                // // if edge == LicenseGraphEdge::Same {
                // //     // TODO: realy add inverses of Same edges?
                // //     self.graph.add_edge(right, left, edge.clone());
                // // }
                // idx
            })
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
                    LicenseGraphBuilderTask::AddEdge { left_pairs, rights } => {
                        let right_idxs = self.apply_task(rights, origin);
                        left_pairs
                            .iter()
                            .flat_map(|(edge, nodes)| nodes.iter().map(move |node| (edge, node)))
                            .map(|(edge, left)| {
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

    pub fn get_license_names(&self) -> Vec<&LicenseIdentifier> {
        self.graph
            .node_weights()
            .filter_map(|w| match w {
                LicenseGraphNode::Data(data) => match data {
                    LicenseData::LicenseIdentifier(license_identifier) => {
                        Option::Some(license_identifier)
                    }
                    _ => Option::None {},
                },
                _ => Option::None {},
            })
            .collect()
    }

    pub fn get_as_dot(&self) -> String {
        let dot = Dot::with_config(&self.graph, &[]);
        format!("{:?}", dot)
    }
    pub fn get_condensed(&self) -> Graph<LicenseGraphNode, LicenseGraphEdge> {
        petgraph::algo::condensation(Graph::from(self.graph.clone()), false).map(
            |_idx, node| {
                if node.len() == 1 {
                    node.iter().next().unwrap().clone()
                } else {
                    LicenseGraphNode::Vec(node.clone())
                }
            },
            |_idx, edge| edge.clone(),
        )
    }
    pub fn get_condensed_as_dot(&self) -> String {
        let condensed = self.get_condensed();
        let condensed_and_filtered = condensed.filter_map(
            |_, node| Option::Some(node),
            |edx, edge| {
                if let Some((ida, idb)) = condensed.edge_endpoints(edx) {
                    if ida == idb {
                        Option::None
                    } else {
                        Option::Some(edge)
                    }
                } else {
                    Option::Some(edge)
                }
            },
        );
        let dot = Dot::with_config(&condensed_and_filtered, &[]);
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

#[cfg(test)]
mod tests {
    use crate::model::*;

    #[test]
    fn license_name_tests() {
        assert_eq!(LicenseIdentifier::new("MIT"), LicenseIdentifier::new("MIT"));
        assert_eq!(LicenseIdentifier::new("MIT"), LicenseIdentifier::new("mit"));
        assert_eq!(LicenseIdentifier::new("MIT"), LicenseIdentifier::new("mIt"));
    }

    #[test]
    fn license_name_statement_tests() {
        assert_eq!(
            LicenseGraphNode::license_name("MIT"),
            LicenseGraphNode::license_name("mIt")
        );
    }

    fn demo() -> LicenseGraph {
        let mut builder = LicenseGraphBuilder::new();

        let tasks_a = LicenseGraphBuilderTask::new1(LicenseGraphNode::license_name("MIT")).edge(
            LicenseGraphEdge::Same,
            vec![LicenseGraphNode::license_name("MIT License")],
        );

        builder = builder.add_tasks(
            vec![tasks_a],
            Box::new(Origin::new_with_url(
                "Origin_name_a",
                "https://domain.invalid/license.txt",
            )),
        );

        let tasks_b = LicenseGraphBuilderTask::new1(LicenseGraphNode::license_name("MIT"))
            .edge(
                LicenseGraphEdge::HintsTowards,
                vec![LicenseGraphNode::license_name("the mit license")],
            )
            .edge(
                LicenseGraphEdge::AppliesTo,
                vec![LicenseGraphNode::license_type("permissive")],
            );

        builder = builder.add_tasks(vec![tasks_b], Box::new(Origin::new("Origin_name_b")));

        builder.build()
    }

    #[test]
    fn demo_should_run() {
        let s = demo();
        println!("{s:#?}");

        println!("{}", s.get_as_dot());

        assert_eq!(s.graph.node_count(), 4);
        assert_eq!(s.get_idx_of_license("mit"), s.get_idx_of_license("MIT"));
        assert_ne!(
            s.get_idx_of_license("mit"),
            s.get_idx_of_license("BSD-3-Clause")
        );
        assert_eq!(Option::None, s.get_idx_of_license("BSD-3-Clause"));
    }
}
