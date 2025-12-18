use std::collections::{HashMap, HashSet};

use crate::coordinate_grid::CoordinateGrid;

/// Gets subtracted for progressing further from the hex core
const PROGRESSION_SUBTRACTION: usize = 5;
const BRANCH_MULTIPLIER: f64 = 0.5;

/// Used on all six sides of a Hex
pub enum HexWrapper {
    Affinity(usize),
    Hex(Box<Hex>),
    Blocked,
}

/// Simple enum for simplification
#[derive(PartialEq, Eq, Hash, Clone)]
pub enum Direction {
    Top,
    TopLeft,
    TopRight,
    BottomLeft,
    BottomRight,
    Bottom,
}
impl Direction {
    pub fn get_all() -> [Direction; 6] {
        [Self::Top, Self::TopLeft, Self::TopRight, Self::BottomLeft, Self::BottomRight, Self::Bottom]
    }

    /// Used for coordinate calculations
    pub fn to_offset(&self) -> (f64, f64) {
        match self {
            Direction::Top => {
                (0.0, 1.0)
            },
            Direction::TopLeft => {
                (-1.0, 0.5)
            },
            Direction::TopRight => {
                (1.0, 0.5)
            },
            Direction::BottomLeft => {
                (-1.0, -0.5)
            },
            Direction::BottomRight => {
                (1.0, -0.5)
            },
            Direction::Bottom => {
                (0.0, -1.0)
            },
        }
    }
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

    /// Retrieve the HexWrapper in any given direction
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

    /// Update the HexWrapper in any given direction, returning the previous one
    pub fn set_direction(&mut self, direction: &Direction, hex_wrapper: HexWrapper) -> HexWrapper {
        match direction {
            Direction::Top => std::mem::replace(&mut self.top, hex_wrapper),
            Direction::TopLeft => std::mem::replace(&mut self.top_left, hex_wrapper),
            Direction::TopRight => std::mem::replace(&mut self.top_right, hex_wrapper),
            Direction::BottomLeft => std::mem::replace(&mut self.bottom_left, hex_wrapper),
            Direction::BottomRight => std::mem::replace(&mut self.bottom_right, hex_wrapper),
            Direction::Bottom => std::mem::replace(&mut self.bottom, hex_wrapper),
        }
    }
}

/// Stores the core of the snowflake and all its info
pub struct CoreHex {
    hex: Hex,
    leaves: Vec<Vec<Direction>>,
    coordinate_grid: CoordinateGrid,
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
            coordinate_grid: CoordinateGrid::new(),
        }
    }

    /// Follows the path, returning the Hex and coords at the end location
    pub fn follow_path(&mut self, path: &Vec<Direction>) -> Option<(&mut Hex, f64, f64)> {
        let mut hex = &mut self.hex;
        let mut x_coord = 0.0;
        let mut y_coord = 0.0;
        for direction in path.iter() {
            // coordinate tracking
            let (dx, dy) = direction.to_offset();
            x_coord += dx;
            y_coord += dy;

            match hex.retrieve(direction) {
                HexWrapper::Affinity(_) => return None,
                HexWrapper::Hex(inner) => hex = inner,
                HexWrapper::Blocked => return None,
            }
        }
        return Some((hex, x_coord, y_coord));
    }

    /// Check hexagons around a new hex to ensure blocks are properly updated
    pub fn update_blocks(&mut self, new_hex_path: &Vec<Direction>) -> Option<()> {
        // check all six directions and update both this and other hexes
        // but how to find other hexes? we don't exactly have a universal grid
        // use the new coordinate_grid!
        return Some(());
    }

    /// Insert a new hexagon, returns the new path
    pub fn insert(&mut self, source_hex_path: &Vec<Direction>, direction: Direction) -> Option<Vec<Direction>> {
        // assumption is that the path is not blocked, because it shouldn't be

        // first generate affinities
        let (source_hex, source_x, source_y) = self.follow_path(&source_hex_path)?;
        let mut direction_affinity_map: HashMap<Direction, usize> = HashMap::new();
        match source_hex.retrieve(&direction) {
            HexWrapper::Affinity(source_affinity) => {
                //maybe considering the directionality towards root too if more aesthetic

                let mut directions_to_use: HashSet<Direction> = HashSet::from(Direction::get_all());

                // check to see if we're continuing a pole (no branch hit)
                if source_hex_path.last().is_some_and(|d| *d == direction) {
                    direction_affinity_map.insert(direction.clone(), *source_affinity - PROGRESSION_SUBTRACTION);
                    directions_to_use.remove(&direction);
                }

                // fill in the rest of the affinities (take the branch hit)
                directions_to_use.into_iter().for_each(|d| {
                    direction_affinity_map.insert(d, (*source_affinity as f64 * BRANCH_MULTIPLIER) as usize - PROGRESSION_SUBTRACTION);
                });
            },
            HexWrapper::Hex(_) => return None,
            HexWrapper::Blocked => return None,
        }

        // create hex and perform the insertion
        let new_hex = HexWrapper::Hex(Box::new(Hex {
            top: HexWrapper::Affinity(*direction_affinity_map.get(&Direction::Top)?),
            top_left: HexWrapper::Affinity(*direction_affinity_map.get(&Direction::TopLeft)?),
            top_right: HexWrapper::Affinity(*direction_affinity_map.get(&Direction::TopRight)?),
            bottom_left: HexWrapper::Affinity(*direction_affinity_map.get(&Direction::BottomLeft)?),
            bottom_right: HexWrapper::Affinity(*direction_affinity_map.get(&Direction::BottomRight)?),
            bottom: HexWrapper::Affinity(*direction_affinity_map.get(&Direction::Bottom)?),
        }));
        source_hex.set_direction(&direction, new_hex);

        // update the coordinate grid
        let new_offset = direction.to_offset();
        let new_coords = (source_x + new_offset.0, source_y + new_offset.1);
        let mut new_path = source_hex_path.clone();
        new_path.push(direction);
        self.coordinate_grid.insert(new_coords, new_path.clone());

        // update blocks (for this new hex and existing hexes)
        self.update_blocks(&new_path);

        return Some(new_path);
    }
}

