mod py_runtime;
pub use crate::py_runtime::{pytra};
use crate::py_runtime::*;

fn add(a: i64, b: i64) -> i64 {
    return a + b;
}

fn main() {
    println!("{}", add(3, 4));
}
