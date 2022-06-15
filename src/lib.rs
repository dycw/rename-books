use regex::Regex;
use std::{
    fs::read_dir,
    io::Result,
    path::{Path, PathBuf},
};

pub fn get_dropbox_path() -> &'static Path {
    &Path::new("/data/derek/Dropbox/Temporary")
}

pub fn yield_files() -> Result<Vec<PathBuf>> {
    let path = get_dropbox_path();
    let dir = read_dir(path)?;

    let mut out = vec![];
    let re = Regex::new(r"\d{4} —").unwrap();

    for entry in dir.into_iter() {
        let entry = entry?;
        let p = entry.path();
        println!("i={:?}", p);
        if p.is_file() {
            if let Some(ext) = p.extension() {
                if ext == "pdf" && re.is_match(p.to_str().expect("asdf")) {
                    out.push(p);
                }
            }
        }
    }

    Ok(out)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_dropbox_path_exists() {
        let path = get_dropbox_path();
        assert!(path.exists())
    }

    #[test]
    fn test_yield_files() {
        let files = yield_files().expect("Failed");
        assert_eq!(files.len(), 10);

        let re = Regex::new(r"^\d+").unwrap();

        for file in &files {
            assert!(file.is_file());
            assert_eq!(file.extension().unwrap(), "pdf");
            assert!(re.is_match(file.to_str().unwrap()));
        }
    }
}
