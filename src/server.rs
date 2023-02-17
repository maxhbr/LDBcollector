use crate::model::*;
use crate::sink_dot::*;
use crate::sink_force_graph::*;
use crate::*;
use warp::Filter;
use build_html::*;

pub async fn serve(graph: Box<LicenseGraph>) {

    let graph_for_index = graph.clone();
    // GET / -> index html
    let index = warp::path::end().map(move ||{
        let license_names = graph_for_index.get_license_names();
        let html: String = HtmlPage::new()
            .with_title("ldbcollector")
            .with_header(1, "Licenses:")
            .with_container(
                license_names.iter()
                    .fold( Container::new(ContainerType::Div), |acc, license_name| {
                        acc.with_container(
                            Container::new(ContainerType::Div)
                                .with_link(format!("graph/{}", license_name), format!("{:?}", license_name))
                        )
                    })
            )
            .to_html_string();

        warp::reply::html(html)
    });

    let graph_for_dot = graph.clone();
    // GET /dot/MIT
    let dot = warp::path!("dot" / String)
        .map(move |license: String| {
            let focused = graph_for_dot.focus(LicenseName::new(license.to_string().clone()));
            let html: String = HtmlPage::new()
                .with_title("license")
                .with_header(1, "dot:")
                .with_preformatted(format!("{}", focused.get_as_dot()))
                .with_header(1, "force_graph:")
                .with_preformatted( to_force_graph_json(focused))
                .to_html_string();
            warp::reply::html(html)
        });

    let graph_for_graph = graph.clone();
    // GET /graph/MIT
    let graph = warp::path!("graph" / String)
        .map(move |license: String| {
            let focused = graph_for_graph.focus(LicenseName::new(license.to_string().clone()));
            warp::reply::html(to_force_graph_html(focused))
        });

    warp::serve(index.or(dot).or(graph))
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