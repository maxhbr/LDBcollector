use crate::model::graph::{LicenseGraph, LicenseGraphBuilder};
use crate::model::*;
use crate::*;
use warp::Filter;
use build_html::*;

pub async fn serve(graph: Box<LicenseGraph>) {
    // GET /hello/warp => 200 OK with body "Hello, warp!"
    let ldb = warp::path!("license" / String)
        .map(|license: String| {
            let focused = graph.focus(crate::model::core::LicenseName::new(license.to_string().clone()));
            format!("<body>\n<pre>\n{:?}\n</pre>\n</body>", focused.get_as_dot())
        });

    // GET / -> index html
    let index = warp::path::end().map(||{
        let license_names = graph.get_license_names();
        let index: String = HtmlPage::new()
            .with_title("ldbcollector")
            .with_header(1, "Licenses:")
            .with_container(
                license_names.iter()
                    .fold( Container::new(ContainerType::Div), |acc, license_name| {
                        acc.with_paragraph(format!("{:?}", license_name))
                    })
                // Container::new(ContainerType::Article)
                //     .with_attributes([("id", "article1")])
                //     .with_header_attr(2, "Hello, World", [("id", "article-head")])
                //     .with_paragraph("This is a simple HTML demo")
            )
            .to_html_string();

        warp::reply::html(index)
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


static INDEX_HTML: &str = r#"<!DOCTYPE html>
<html lang="en">
    <head>
        <title>ldbcollector</title>
    </head>
    <body>
        <h1>ldbcollector</h1>
    </body>
</html>
"#;