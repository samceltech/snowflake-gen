use std::collections::HashMap;

use crate::hex::Direction;

/// The entire point of this is because floats (idiotically) cannot be used for hash keys
pub struct CoordinateGrid {
    map: HashMap<(usize, usize), Vec<Direction>>,
}
impl CoordinateGrid {
    pub fn new() -> Self {
        CoordinateGrid {map: HashMap::new()}
    }

    /// Insert the path to a Hex at specific coordinates
    pub fn insert(&mut self, coordinates: (f64, f64), path: Vec<Direction>) {
        // don't have to modify x coordinates, but y coordinates must be decompressed
        let (x, y) = coordinates;
        let nx = x as usize;
        let ny = (y * 2.0) as usize;
        self.map.insert((nx, ny), path);
    }

    /// Retrieve a path if it exists at specific coordinates
    pub fn retrieve(&mut self, coordinates: (f64, f64)) -> Option<&Vec<Direction>> {
        let (x, y) = coordinates;
        let nx = x as usize;
        let ny = (y * 2.0) as usize;
        self.map.get(&(nx, ny))
    }

    /// Remove a specific set of coordinates, returning the path if it exists
    pub fn remove(&mut self, coordinates: (f64, f64)) -> Option<Vec<Direction>> {
        let (x, y) = coordinates;
        let nx = x as usize;
        let ny = (y * 2.0) as usize;
        self.map.remove(&(nx, ny))
    }
}


