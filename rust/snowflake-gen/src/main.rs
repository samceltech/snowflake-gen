use crate::hex::CoreHex;

mod hex;
mod coordinate_grid;

fn main() {
    let snowflake = CoreHex::new();
    println!("Hello, world!");
}

/*
TODO

implement the block updating function
REMEMBER ABOUT THE FRONTIER, WE FORGOT ABOUT THE FRONTIER
add a function to choose where to insert a new hex (accounting for all the affinities)
add a loop function which inserts x number of hexes (parameter which we call here in main)

*/




