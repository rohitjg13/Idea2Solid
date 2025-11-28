plate_width = 140;
plate_depth = 50;
plate_height = 45;
base_thickness = 4;
text_string = "Idea2Solid";
font_size = 18;
text_depth = 2;
tilt_angle = 60;

module wedge_body() {
    hull() {
        cube([plate_width, plate_depth, base_thickness], center = false);
        translate([0, plate_depth - base_thickness, plate_height])
            cube([plate_width, base_thickness, base_thickness], center = false);
    }
}

module main() {
    difference() {
        wedge_body();
        translate([plate_width / 2, plate_depth / 2, -0.5])
            cylinder(d = 6, h = base_thickness + 1, $fn = 48);
    }
    translate([plate_width / 2, plate_depth - base_thickness, base_thickness])
        rotate([tilt_angle, 0, 0])
            linear_extrude(height = text_depth)
                text(text_string, size = font_size, halign = "center", valign = "center");
}

main();