use crate::model::*;
use crate::sink_dot::*;
use crate::sink_force_graph::*;
use crate::sink_html::*;
use crate::*;
use build_html::*;
use regex::Regex;
use warp::Filter;

pub async fn serve(graph: Box<LicenseGraph>) {
    let graph_for_index = graph.clone();
    // GET / -> index html
    let warp_index = warp::path::end().map(move || {
        let license_names = graph_for_index.get_license_names();
        let re = Regex::new(r"^[0-9A-Za-z_\-+.,]+$").unwrap();
        let html: String = HtmlPage::new()
            .with_title("ldbcollector")
            .with_header(1, "Licenses:")
            .with_table(
                Table::from(
                    license_names
                        .iter()
                        .filter(|license_name| re.is_match(&format!("{}", license_name)))
                        .map(|license_name| {
                            vec![
                                Container::new(ContainerType::Div)
                                    .with_link(license_name, format!("{:?}", license_name))
                                    .to_html_string(),
                                Container::new(ContainerType::Div)
                                    .with_link(format!("{}/graph", license_name), "graph")
                                    .to_html_string(),
                                Container::new(ContainerType::Div)
                                    .with_link(format!("{}/svg", license_name), "svg")
                                    .to_html_string(),
                            ]
                        }),
                )
                .with_header_row(["License Name", "graph", "svg"]),
            )
            .to_html_string();

        warp::reply::html(html)
    });

    let graph_for_formats = graph.clone();
    // GET /graph/MIT
    let warp_formats = warp::path!(String / String).map(move |license: String, format: String| {
        match graph_for_formats.focus(&license) {
            Result::Ok(focused) => {
                if format == "graph" {
                    warp::reply::html(to_force_graph_html(focused))
                } else if format == "svg" {
                    warp::reply::html(render_dot(&focused, true, true))
                } else if format == "svg_raw" {
                    warp::reply::html(render_dot(&focused, false, true))
                } else {
                    warp::reply::html(format!("unsupported format {:?}", format))
                }
            }
            Result::Err(err) => warp::reply::html(format!("{:#?}", err)),
        }
    });

    let graph_for_html = graph.clone();
    // GET /MIT
    let warp_html = warp::path!(String).map(move |license_list: String| {
        warp::reply::html(license_graph_to_tree_string(
            &graph_for_html,
            license_list.split(",").collect(),
        ))
    });

    warp::serve(warp_index.or(warp_formats).or(warp_html))
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
