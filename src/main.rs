use ldbcolector::*;
use spdx::identifiers::LICENSES;

fn add_spdx_licenses(s: state::State) -> state::State {
    LICENSES.into_iter()
        .take(10)
        .fold(s, |acc : state::State, (name,full_name,_)| 
            acc.add_alias(
                license::LicenseName::new(full_name),
                license::LicenseName::new(name),
                state::LicenseRelation::Same,
            )
        )

}

fn main() {
    let s0 = state::State::new();
    let s1 = add_spdx_licenses(s0);

    println!("{:#?}", s1);
    println!("{:#?}", s1.get_component());
}
