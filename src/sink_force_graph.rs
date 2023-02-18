use crate::model::*;
use petgraph::stable_graph::NodeIndex;
use serde_derive::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Clone, Serialize, Deserialize)]
struct ForceGraphNode {
    id: String,
    name: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct ForceGraphLink {
    source: String,
    target: String,
    name: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct ForceGraph {
    nodes: Vec<ForceGraphNode>,
    links: Vec<ForceGraphLink>,
}

fn node_index_to_id(idx: NodeIndex) -> String {
    format!("id_{:?}", idx)
}

fn to_force_graph(graph: LicenseGraph) -> ForceGraph {
    let graph = graph.get_internal_graph();

    let mut nodes_map: HashMap<NodeIndex, ForceGraphNode> = HashMap::new();
    let mut links: Vec<ForceGraphLink> = vec![];

    graph
        .edge_indices()
        .for_each(|eidx| match graph.edge_endpoints(eidx) {
            Option::Some((lidx, ridx)) => {
                let eweight = graph.edge_weight(eidx).unwrap();
                let lweight = graph.node_weight(lidx).unwrap();
                let rweight = graph.node_weight(ridx).unwrap();

                nodes_map.insert(
                    lidx,
                    ForceGraphNode {
                        id: node_index_to_id(lidx),
                        name: format!("{:?}", lweight),
                    },
                );
                nodes_map.insert(
                    ridx,
                    ForceGraphNode {
                        id: node_index_to_id(ridx),
                        name: format!("{:?}", rweight),
                    },
                );

                links.push(ForceGraphLink {
                    source: node_index_to_id(lidx),
                    target: node_index_to_id(ridx),
                    name: format!("{:?}", eweight),
                });
            }
            Option::None {} => {}
        });

    let nodes: Vec<ForceGraphNode> = nodes_map.values().map(|node| node.clone()).collect();

    ForceGraph { nodes, links }
}

pub fn to_force_graph_json(graph: LicenseGraph) -> String {
    serde_json::to_string(&to_force_graph(graph)).unwrap()
}

const JS_HEADER: &str = r#"
    const gData = 
"#;
const JS_FOOTER: &str = r#"
;

let selfLoopLinks = {};
let sameNodesLinks = {};
const curvatureMinMax = 0.2;

// 1. assign each link a nodePairId that combines their source and target independent of the links direction
// 2. group links together that share the same two nodes or are self-loops
gData.links.forEach(link => {
  link.nodePairId = link.source <= link.target ? (link.source + "_" + link.target) : (link.target + "_" + link.source);
  let map = link.source === link.target ? selfLoopLinks : sameNodesLinks;
  if (!map[link.nodePairId]) {
    map[link.nodePairId] = [];
  }
  map[link.nodePairId].push(link);
});

// Compute the curvature for self-loop links to avoid overlaps
Object.keys(selfLoopLinks).forEach(id => {
  let links = selfLoopLinks[id];
  let lastIndex = links.length - 1;
  links[lastIndex].curvature = 1;
  let delta = (1 - curvatureMinMax) / lastIndex;
  for (let i = 0; i < lastIndex; i++) {
    links[i].curvature = curvatureMinMax + i * delta;
  }
});

// Compute the curvature for links sharing the same two nodes to avoid overlaps
Object.keys(sameNodesLinks).filter(nodePairId => sameNodesLinks[nodePairId].length > 1).forEach(nodePairId => {
  let links = sameNodesLinks[nodePairId];
  let lastIndex = links.length - 1;
  let lastLink = links[lastIndex];
  lastLink.curvature = curvatureMinMax;
  let delta = 2 * curvatureMinMax / lastIndex;
  for (let i = 0; i < lastIndex; i++) {
    links[i].curvature = - curvatureMinMax + i * delta;
    if (lastLink.source !== links[i].source) {
      links[i].curvature *= -1; // flip it around, otherwise they overlap
    }
  }
});

const Graph = ForceGraph()
  (document.getElementById('graph'))
    .nodeAutoColorBy('type')
    .linkAutoColorBy('label')
    //.dagMode('lr').dagLevelDistance(300)
    //.d3Force('collide', d3.forceCollide(13)).d3AlphaDecay(0.02).d3VelocityDecay(0.3)
    .linkCurvature('curvature')
    .linkDirectionalArrowRelPos(1)
    .linkDirectionalArrowLength(6)
  .nodeCanvasObject((node, ctx, globalScale) => {
    const label = node.name;
    const fontSize = 12/globalScale;
    ctx.font = `${fontSize}px Sans-Serif`;
    const textWidth = ctx.measureText(label).width;
    const bckgDimensions = [textWidth, fontSize].map(n => n + fontSize * 0.2); // some padding

    ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
    ctx.fillRect(node.x - bckgDimensions[0] / 2, node.y - bckgDimensions[1] / 2, ...bckgDimensions);

    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillStyle = node.color;
    ctx.fillText(label, node.x, node.y);

    node.__bckgDimensions = bckgDimensions; // to re-use in nodePointerAreaPaint
  })
  .nodePointerAreaPaint((node, color, ctx) => {
    ctx.fillStyle = color;
    const bckgDimensions = node.__bckgDimensions;
    bckgDimensions && ctx.fillRect(node.x - bckgDimensions[0] / 2, node.y - bckgDimensions[1] / 2, ...bckgDimensions);
  })
  .linkCanvasObjectMode(() => 'after')
  .linkCanvasObject((link, ctx) => {
    const MAX_FONT_SIZE = 4;
    const LABEL_NODE_MARGIN = Graph.nodeRelSize() * 1.5;

    const start = link.source;
    const end = link.target;

    // ignore unbound links
    if (typeof start !== 'object' || typeof end !== 'object') return;

    // calculate label positioning
    const textPos = Object.assign(...['x', 'y'].map(c => ({
      [c]: start[c] + (end[c] - start[c]) / 2 // calc middle point
    })));

    const relLink = { x: end.x - start.x, y: end.y - start.y };

    const maxTextLength = Math.sqrt(Math.pow(relLink.x, 2) + Math.pow(relLink.y, 2)) - LABEL_NODE_MARGIN * 2;

    let textAngle = Math.atan2(relLink.y, relLink.x);
    // maintain label vertical orientation for legibility
    if (textAngle > Math.PI / 2) textAngle = -(Math.PI - textAngle);
    if (textAngle < -Math.PI / 2) textAngle = -(-Math.PI - textAngle);

    const label = `${link.name}`;

    // estimate fontSize to fit in link length
    ctx.font = '1px Sans-Serif';
    const fontSize = Math.min(MAX_FONT_SIZE, maxTextLength / ctx.measureText(label).width);
    ctx.font = `${fontSize}px Sans-Serif`;
    const textWidth = ctx.measureText(label).width;
    const bckgDimensions = [textWidth, fontSize].map(n => n + fontSize * 0.2); // some padding

    // draw text label (with background rect)
    ctx.save();
    ctx.translate(textPos.x, textPos.y);
    ctx.rotate(textAngle);

    ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
    ctx.fillRect(- bckgDimensions[0] / 2, - bckgDimensions[1] / 2, ...bckgDimensions);

    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillStyle = 'darkgrey';
    ctx.fillText(label, 0, 0);
    ctx.restore();
  })
    .graphData(gData);
  // Spread nodes a little wider
  Graph.d3Force('charge').strength(-120);
"#;

pub fn to_force_graph_js(graph: LicenseGraph) -> String {
    format!("{}{}{}", JS_HEADER, to_force_graph_json(graph), JS_FOOTER)
}


const HTML_HEADER: &str = r#"
<head>
  <style> body { margin: 0; } </style>
  <script src="https://unpkg.com/force-graph"></script>
</head>

<body>
  <div id="graph"></div>

  <script>
"#;
const HTML_FOOTER: &str = r#"
</script>
</body>
"#;


pub fn to_force_graph_html(graph: LicenseGraph) -> String {
    format!("{}{}{}", HTML_HEADER, to_force_graph_js(graph), HTML_FOOTER)
}
