outer_diameter = 120;
inner_diameter = 104;
height = 110;
base_thickness = 4;
drain_hole_diameter = 8;
rim_thickness = 3;

module main() {
    difference() {
        linear_extrude(height = height, scale = 0.8, center = false)
            circle(d = outer_diameter, $fn = 96);
        translate([0, 0, base_thickness])
            linear_extrude(height = height, scale = 0.8, center = false)
                circle(d = inner_diameter, $fn = 96);
        cylinder(d = drain_hole_diameter, h = base_thickness + 2, center = false, $fn = 48);
    }
    translate([0, 0, height - rim_thickness])
        difference() {
            linear_extrude(height = rim_thickness, center = false)
                circle(d = outer_diameter + rim_thickness * 2, $fn = 96);
            linear_extrude(height = rim_thickness, center = false)
                circle(d = outer_diameter, $fn = 96);
        }
}

main();