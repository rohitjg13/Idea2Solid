// Vented Electronics Enclosure
// A box with a snap-fit lid and ventilation slots

$fn = 30;

width = 80;
depth = 60;
height = 30;
wall_thickness = 2;
vent_width = 3;
vent_spacing = 6;

module main() {
    // Base Box
    difference() {
        // Outer shell
        cube([width, depth, height]);
        
        // Inner hollow
        translate([wall_thickness, wall_thickness, wall_thickness])
            cube([width - wall_thickness*2, depth - wall_thickness*2, height]);
            
        // Ventilation slots on the sides
        for (x = [10 : vent_spacing : width - 10]) {
            translate([x, -1, height/2])
                cube([vent_width, wall_thickness + 2, height/2]);
            translate([x, depth - wall_thickness - 1, height/2])
                cube([vent_width, wall_thickness + 2, height/2]);
        }
    }
    
    // Mounting posts (standoffs) in corners
    post_offset = 5;
    post_height = 5;
    for (x = [post_offset, width - post_offset]) {
        for (y = [post_offset, depth - post_offset]) {
            translate([x, y, wall_thickness])
                cylinder(h = post_height, d = 4);
            translate([x, y, wall_thickness + post_height])
                cylinder(h = 2, d = 2); // Screw hole marker
        }
    }
}

main();
