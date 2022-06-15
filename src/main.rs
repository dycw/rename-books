use rename_books;

fn main() {
    let path = rename_books::yield_files();

    println!("{:?}", path);
}
