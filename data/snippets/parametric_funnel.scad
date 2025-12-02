// Parametric Funnel
// A simple funnel with customizable top and bottom diameters

$fn = 60;

top_diameter = 80;      // Outer diameter of the wide top
spout_diameter = 15;    // Outer diameter of the narrow spout
top_height = 60;        // Height of the conical part
spout_height = 40;      // Height of the straight spout
wall_thickness = 2;     // Thickness of the walls

module main() {
    difference() {
        // Outer shell
        union() {
            // Cone section
            translate([0, 0, spout_height])
                cylinder(h = top_height, d1 = spout_diameter, d2 = top_diameter);
            // Spout section
            cylinder(h = spout_height, d = spout_diameter);
        }
        
        // Inner hollow (subtracted)
        union() {
            // Inner cone
            translate([0, 0, spout_height])
                cylinder(h = top_height + 0.1, d1 = spout_diameter - wall_thickness*2, d2 = top_diameter - wall_thickness*2);
            // Inner spout
            translate([0, 0, -0.1])
                cylinder(h = spout_height + 0.1, d = spout_diameter - wall_thickness*2);
        }
    }
}

main();
