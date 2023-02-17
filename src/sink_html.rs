use petgraph::dot::{Config, Dot};
use petgraph::graph::{Edge, EdgeIndex, Frozen, Node, NodeIndex};
use petgraph::stable_graph::StableGraph;
use std::collections::HashSet;
use crate::model::*;

pub struct LicenseGraphTreeLink {
    to: LicenseGraphTree,
    edges: Vec<LicenseGraphEdge>,
}

pub struct LicenseGraphTree {
    node: LicenseGraphNode,
    links: Vec<LicenseGraphTreeLink>,
}

fn license_graph_to_tree_for_node(graph: &LicenseGraph, idx: NodeIndex, seen_ids: HashSet<NodeIndex>) -> LicenseGraphTree {

    

    todo!()
}

pub fn license_graph_to_tree(graph: &LicenseGraph, license_name: LicenseName) -> LicenseGraphTree {
    // let graph = graph.clone();
    let root_idx = graph.get_idx_of_license(license_name).unwrap();

    license_graph_to_tree_for_node(graph, root_idx, HashSet::new())
}