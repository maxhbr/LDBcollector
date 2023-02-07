use ldbcolector::demo;

fn main() {
    let s = demo();
    println!("{s:#?}");
    println!("{:#?}", s.get_component());
}
