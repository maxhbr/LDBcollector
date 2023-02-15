use crate::model::graph::{LicenseGraph, LicenseGraphBuilder};
use crate::model::*;
use crate::*;
use warp::Filter;
use build_html::*;

pub async fn serve(graph: Box<LicenseGraph>) {
    let graph2 = graph.clone();

    // GET / -> index html
    let index = warp::path::end().map(move ||{
        let license_names = graph2.get_license_names();
        let html: String = HtmlPage::new()
            .with_title("ldbcollector")
            .with_header(1, "Licenses:")
            .with_container(
                license_names.iter()
                    .fold( Container::new(ContainerType::Div), |acc, license_name| {
                        acc.with_container(
                            Container::new(ContainerType::Div)
                                .with_link(format!("license/{}", license_name), format!("{:?}", license_name))
                        )
                    })
            )
            .to_html_string();

        warp::reply::html(html)
    });

    // GET /license/MIT
    let ldb = warp::path!("license" / String)
        .map(move |license: String| {
            let focused = graph.focus(crate::model::core::LicenseName::new(license.to_string().clone()));
            let html: String = HtmlPage::new()
                .with_title("license")
                .with_header(1, "dot:")
                .with_preformatted(format!("{}", focused.get_as_dot()))
                .to_html_string();
            warp::reply::html(html)
        });

    warp::serve(index.or(ldb))
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