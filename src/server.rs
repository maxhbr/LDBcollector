use crate::model::*;
use crate::sink_dot::*;
use crate::sink_force_graph::*;
use crate::sink_html::*;
use crate::*;
use build_html::*;
use warp::Filter;

pub async fn serve(graph: Box<LicenseGraph>) {
    let graph_for_index = graph.clone();
    // GET / -> index html
    let warp_index = warp::path::end().map(move || {
        let license_names = graph_for_index.get_license_names();
        let html: String = HtmlPage::new()
            .with_title("ldbcollector")
            .with_header(1, "Licenses:")
            .with_container(license_names.iter().fold(
                Container::new(ContainerType::Div),
                |acc, license_name| {
                    acc.with_container(Container::new(ContainerType::Div).with_link(
                        license_name,
                        format!("{:?}", license_name),
                    ))
                },
            ))
            .to_html_string();

        warp::reply::html(html)
    });

    let graph_for_dot = graph.clone();
    // GET /dot/MIT
    let warp_dot = warp::path!(String / "dot").map(move |license: String| {
        let focused = graph_for_dot.focus(LicenseName::new(license.to_string().clone()));
        format!("{}", focused.get_as_dot())
    });

    let graph_for_svg = graph.clone();
    // GET /svg/MIT
    let warp_svg = warp::path!(String / "svg").map(move |license: String| {
        let focused = graph_for_svg.focus(LicenseName::new(license.to_string().clone()));
        format!("{}", render_dot(focused))
    });

    let graph_for_graph = graph.clone();
    // GET /graph/MIT
    let warp_graph = warp::path!(String / "graph").map(move |license: String| {
        let focused = graph_for_graph.focus(LicenseName::new(license.to_string().clone()));
        warp::reply::html(to_force_graph_html(focused))
    });

    let graph_for_html = graph.clone();
    // GET /html/MIT
    let warp_html = warp::path!(String).map(move |license: String| {
        warp::reply::html(license_graph_to_tree_string(
            &graph_for_html,
            LicenseName::new(license.to_string().clone()),
        ))
    });

    warp::serve(warp_index.or(warp_dot).or(warp_svg).or(warp_graph).or(warp_html))
        .run(([127, 0, 0, 1], 3030))
        .await;
}

pub fn sync_serve(graph: Box<LicenseGraph>) {
    tokio::runtime::Builder::new_multi_thread()
        .enable_all()
        .build()
        .unwrap()
        .block_on(server::serve(graph))
}
