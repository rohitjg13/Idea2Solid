side_length = 45;
wall_thickness = 3;
height = 80;
floor_thickness = 3;
lip_height = 5;
lip_offset = 1.5;

module hexagon(radius) {
    circle(r = radius, $fn = 6);
}

module main() {
    difference() {
        linear_extrude(height = height)
            hexagon(side_length);
        translate([0, 0, floor_thickness])
            linear_extrude(height = height)
                hexagon(side_length - wall_thickness);
    }
    translate([0, 0, height - lip_height])
        difference() {
            linear_extrude(height = lip_height)
                hexagon(side_length + lip_offset);
            linear_extrude(height = lip_height)
                hexagon(side_length);
        }
}

main();