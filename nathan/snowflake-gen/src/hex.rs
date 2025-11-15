/// Used on all six sides of a Hex
pub enum HexWrapper {
    Affinity(usize),
    Hex(Box<Hex>),
    Blocked,
}

/// Simple enum for simplification
pub enum Direction {
    Top,
    TopLeft,
    TopRight,
    BottomLeft,
    BottomRight,
    Bottom,
}

/// Fundamental struct used for a snowflake
pub struct Hex {
    top: HexWrapper,
    top_left: HexWrapper,
    top_right: HexWrapper,
    bottom_left: HexWrapper,
    bottom_right: HexWrapper,
    bottom: HexWrapper,
}
impl Hex {
    pub fn retrieve(&mut self, direction: &Direction) -> &mut HexWrapper {
        match direction {
            Direction::Top => &mut self.top,
            Direction::TopLeft => &mut self.top_left,
            Direction::TopRight => &mut self.top_right,
            Direction::BottomLeft => &mut self.bottom_left,
            Direction::BottomRight => &mut self.bottom_right,
            Direction::Bottom => &mut self.bottom,
        }
    }
}

/// Stores the core of the snowflake and all its info
pub struct CoreHex {
    hex: Hex,
    leaves: Vec<Vec<Direction>>,
    size: usize,
}
impl CoreHex {
    pub fn new() -> Self {
        let hex = Hex {
            top: HexWrapper::Affinity(100),
            top_left: HexWrapper::Affinity(100),
            top_right: HexWrapper::Affinity(100),
            bottom_left: HexWrapper::Affinity(100),
            bottom_right: HexWrapper::Affinity(100),
            bottom: HexWrapper::Affinity(100),
        };
        CoreHex {
            hex,
            leaves: vec![],
            size: 0,
        }
    }

    /// Follows the path, returning the Hex and coords at the end location
    pub fn follow_path(&mut self, path: Vec<Direction>) -> Option<(&mut Hex, f64, f64)> {
        let mut hex = &mut self.hex;
        let mut x_coord = 0.0;
        let mut y_coord = 0.0;
        for direction in path.iter() {
            match direction {
                Direction::Top => {
                    y_coord += 1.0;
                },
                Direction::TopLeft => {
                    x_coord -= 1.0;
                    y_coord += 0.5;
                },
                Direction::TopRight => {
                    x_coord += 1.0;
                    y_coord += 0.5;
                },
                Direction::BottomLeft => {
                    x_coord -= 1.0;
                    y_coord -= 0.5;
                },
                Direction::BottomRight => {
                    x_coord += 1.0;
                    y_coord -= 0.5;
                },
                Direction::Bottom => {
                    y_coord -= 1.0;
                },
            }
            match hex.retrieve(direction) {
                HexWrapper::Affinity(_) => return None,
                HexWrapper::Hex(inner) => hex = inner,
                HexWrapper::Blocked => return None,
            }
        }
        return Some((hex, x_coord, y_coord));
    }

    /// Insert a new hexagon
    pub fn insert(&mut self, path: Vec<Direction>, direction: Direction) -> Option<()> {
        let end_hex = self.follow_path(path)?;
        match end_hex.0.retrieve(&direction) {
            HexWrapper::Affinity(source_affinity) => {
                //TODO, need to insert new hex and generate its new affinities,
                //maybe considering the directionality towards root too and distance,
                //and also find out which sides are blocked
            },
            HexWrapper::Hex(_) => return None,
            HexWrapper::Blocked => return None,
        }
        return None;
    }
}

