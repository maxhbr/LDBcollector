use crate::model::*;
use build_html::*;
use itertools::Itertools;
use petgraph::dot::{Config, Dot};
use petgraph::graph::{Edge, EdgeIndex, Frozen, Node, NodeIndex};
use petgraph::stable_graph::StableGraph;
use petgraph::visit::EdgeRef;
use std::collections::HashSet;

#[derive(Debug)]
pub struct LicenseGraphTreeEdge<'a> {
    to: LicenseGraphTree<'a>,
    weights: Vec<(EdgeIndex, &'a LicenseGraphEdge)>,
}

#[derive(Debug)]
pub struct LicenseGraphTree<'a> {
    id: NodeIndex,
    weight: &'a LicenseGraphNode,
    edges: Vec<LicenseGraphTreeEdge<'a>>,
}

fn license_graph_to_tree_for_node(
    graph: &LicenseGraph,
    idx: NodeIndex,
    traversed_edges: HashSet<EdgeIndex>,
) -> LicenseGraphTree {
    let edges: Vec<LicenseGraphTreeEdge> = graph
        .graph
        .edges(idx)
        .filter(|e| !(traversed_edges.contains(&e.id())))
        .group_by(|e| e.target())
        .into_iter()
        .map(|(target, es)| {
            let mut traversed_edges = traversed_edges.clone();
            let weights = es
                .into_iter()
                .map(|e| {
                    traversed_edges.insert(e.id());
                    (e.id(), e.weight())
                })
                .collect();
            let to = license_graph_to_tree_for_node(graph, target, traversed_edges);
            LicenseGraphTreeEdge { to, weights }
        })
        .collect();

    let weight = graph.graph.node_weight(idx).unwrap();
    LicenseGraphTree {
        id: idx,
        weight,
        edges,
    }
}

pub fn license_graph_to_tree(graph: &LicenseGraph, license_name: LicenseName) -> LicenseGraphTree {
    // let graph = graph.clone();
    let root_idx = graph.get_idx_of_license(license_name).unwrap();

    license_graph_to_tree_for_node(graph, root_idx, HashSet::new())
}

fn tree_edge_to_html(edge: &LicenseGraphTreeEdge) -> Container {
    match edge {
        LicenseGraphTreeEdge { to, weights } => Container::new(ContainerType::Div)
            .with_attributes([("class", "tree_edge")])
            .with_header(2, format!("{:?}", weights))
            .with_container(tree_to_html(to)),
    }
}

fn tree_to_html(tree: &LicenseGraphTree) -> Container {
    match tree {
        LicenseGraphTree { id, weight, edges } => Container::new(ContainerType::Div)
            .with_attributes([("class", "tree")])
            .with_header(2, format!("{:?}: {:?}", id, weight))
            .with_container(
                edges
                    .iter()
                    .fold(Container::new(ContainerType::Div), |acc, edge| {
                        acc.with_container(tree_edge_to_html(edge))
                    }),
            ),
    }
}

pub fn license_graph_to_tree_string(graph: &LicenseGraph, license_name: LicenseName) -> String {
    HtmlPage::new()
        .with_title(format!("{:?}", &license_name))
        .with_script_link("https://unpkg.com/force-graph")
        .with_style(
            r#"
        div.tree {
            border-left: 8mm ridge rgba(220, 220, 220, .6);
        }
        div.tree_edge {
            border-left: 8mm ridge rgba(120, 120, 120, .6);
        }
        p{font-family:"Liberation Serif";}
        "#,
        )
        .with_header(1, format!("{:?}", &license_name))
        .with_container({
            let tree = license_graph_to_tree(graph, license_name);
            tree_to_html(&tree)
        })
        .to_html_string()
}
