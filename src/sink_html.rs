use crate::model::*;
use crate::sink_dot::render_condensed_dot;
use crate::sink_force_graph::*;
use build_html::*;
use graphviz_rust::attributes::weight;
use itertools::Itertools;
use petgraph::dot::{Config, Dot};
use petgraph::graph::{Edge, EdgeIndex, Frozen, Node, NodeIndex};
use petgraph::stable_graph::StableGraph;
use petgraph::visit::EdgeRef;
use petgraph::Direction;
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
    origins: Vec<Origin>,
}

fn license_graph_to_tree_for_node(
    direction: Direction,
    graph: &LicenseGraph,
    idx: NodeIndex,
    traversed_edges: HashSet<EdgeIndex>,
) -> LicenseGraphTree {
    let edges: Vec<LicenseGraphTreeEdge> = graph
        .graph
        .edges_directed(idx, direction)
        .filter(|e| !(traversed_edges.contains(&e.id())))
        .group_by(|e| {
            if direction == Direction::Outgoing {
                e.target()
            } else {
                e.source()
            }
        })
        .into_iter()
        .map(|(next, es)| {
            let mut traversed_edges = traversed_edges.clone();
            let weights = es
                .into_iter()
                .map(|e| {
                    traversed_edges.insert(e.id());
                    (e.id(), e.weight())
                })
                .collect();
            let to = license_graph_to_tree_for_node(direction, graph, next, traversed_edges);
            LicenseGraphTreeEdge { to, weights }
        })
        .collect();

    let weight = graph.graph.node_weight(idx).unwrap();

    let default = Vec::new();
    let origins = graph.node_origins.get_vec(&idx).unwrap_or(&default);
    LicenseGraphTree {
        id: idx,
        weight,
        edges,
        origins: origins.clone(),
    }
}

fn license_graph_to_tree(
    direction: Direction,
    graph: &LicenseGraph,
    license_name: String,
) -> Option<LicenseGraphTree> {
    let root_idx = graph.get_idx_of_license(&license_name)?;
    Some(license_graph_to_tree_for_node(
        direction,
        graph,
        root_idx,
        HashSet::new(),
    ))
}

fn render_weight(weight: &LicenseGraphNode, c: &mut Container) -> () {
    match weight {
        LicenseGraphNode::Data(d) => c.add_preformatted(match d {
            LicenseData::LicenseText(text) => text.clone(),
            // LicenseData::LicenseIdentifier(_) => todo!(),
            // LicenseData::LicenseType(_) => todo!(),
            // LicenseData::LicenseFlag(_) => todo!(),
            // LicenseData::LicenseRating(_) => todo!(),
            _ => format!("{:#?}", d),
        }),
        LicenseGraphNode::Note(note) => c.add_paragraph(note),
        LicenseGraphNode::URL(url) => c.add_paragraph(url),
        LicenseGraphNode::Vec(vec) => {
            let mut l = Container::new(ContainerType::UnorderedList);
            vec.iter().for_each(|weight| render_weight(weight, &mut l));
            c.add_container(l)
        }
        LicenseGraphNode::Statement { statement_content } => c.add_paragraph(statement_content),
        LicenseGraphNode::StatementRule { statement_content } => {
            c.add_preformatted(statement_content)
        }
    };
}

fn tree_to_html(
    direction: Direction,
    tree: &LicenseGraphTree,
    from_edge: Option<&LicenseGraphTreeEdge>,
    written_nodes: &mut HashSet<NodeIndex>,
) -> Container {
    match tree {
        LicenseGraphTree {
            id,
            weight,
            edges,
            origins,
        } => {
            let mut c = Container::new(ContainerType::Div).with_attributes([("class", "tree")]);
            match from_edge {
                Option::Some(LicenseGraphTreeEdge { to, weights }) => {
                    let weights: Vec<&LicenseGraphEdge> = weights.iter().map(|(_, w)| *w).collect();
                    if direction == Direction::Outgoing {
                        c.add_header(3, format!("{:?} {:?}&rarr;", weight, weights));
                    } else {
                        c.add_header(3, format!("&larr;{:?} {:?}", weights, weight));
                    };
                }
                Option::None {} => c.add_header(3, format!("{:?}", weight)),
            }

            if written_nodes.contains(id) {
                c.with_link(format!("#{:?}", id), "&uarr;")
            } else {
                c.add_container(
                    Container::new(ContainerType::Div)
                        .with_attributes([("class", "anchor"), ("id", &format!("{:?}", id))]),
                );
                written_nodes.insert(*id);
                render_weight(*weight, &mut c);
                c.add_header(5, "Edge Origins:");
                // TODO
                c.add_header(5, "Node Origins:");
                c.add_container(origins.iter().fold(
                    Container::new(ContainerType::UnorderedList),
                    |acc, origin| match origin.url.clone() {
                        Option::Some(url) => acc.with_link(url, &origin.name),
                        Option::None {} => acc.with_paragraph(&origin.name),
                    },
                ));
                c.with_container(edges.iter().fold(
                    Container::new(ContainerType::Div),
                    |acc, edge| {
                        acc.with_container(match edge {
                            LicenseGraphTreeEdge { to, weights } => {
                                tree_to_html(direction, &to, Option::Some(edge), written_nodes)
                            }
                        })
                    },
                ))
            }
        }
    }
}

fn license_graph_to_html(
    direction: Direction,
    graph: &LicenseGraph,
    license_name: &str,
) -> Container {
    match license_graph_to_tree(direction, graph, String::from(license_name)) {
        Some(tree) => tree_to_html(direction, &tree, Option::None, &mut HashSet::new()),
        None => Container::new(ContainerType::Div).with_paragraph(format!(
            "failed `license_graph_to_html` for {}",
            license_name
        )),
    }
}

fn license_graph_to_html_both_directions(graph: &LicenseGraph, license_name: &str) -> Container {
    Container::new(ContainerType::Div)
        .with_header(2, "backward")
        .with_container(license_graph_to_html(
            Direction::Incoming,
            graph,
            license_name.clone(),
        ))
        .with_header(2, "forward")
        .with_container(license_graph_to_html(
            Direction::Outgoing,
            graph,
            license_name.clone(),
        ))
}

pub fn license_graph_to_tree_string(graph: &LicenseGraph, license_names: Vec<&str>) -> String {
    match graph.focus_many(license_names.clone()) {
        Result::Ok(focused) => HtmlPage::new()
            .with_title(format!("{:?}", license_names))
            .with_stylesheet("https://unpkg.com/modern-css-reset/dist/reset.min.css")
            .with_script_link("https://unpkg.com/force-graph")
            .with_style(
                r#"
                div.tree {
                    border-left: 8mm ridge rgba(220, 220, 220, .6);
                    margin: 5px;
                    padding: 5px;
                }
                div#graph {
                    background: #EEEEEE;
                }
                p{font-family:"Liberation Serif";}
                .svg > svg {
                    display: block;
                    margin: auto;
                }
                "#,
            )
            .with_container(
                Container::new(ContainerType::Div)
                    .with_attributes([("class", "svg")])
                    .with_raw(render_condensed_dot(&focused)),
            )
            .with_header(1, format!("{:?}", &license_names))
            .with_table(
                Table::from(vec![license_names
                    .iter()
                    .map(|license_name| {
                        license_graph_to_html_both_directions(graph, *license_name).to_html_string()
                    })
                    .collect::<Vec<_>>()])
                .with_header_row(license_names),
            )
            .to_html_string(),
        Result::Err(err) => {
            format!("{:?}", err)
        }
    }
}
