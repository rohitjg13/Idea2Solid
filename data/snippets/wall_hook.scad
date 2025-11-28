base_width = 50;
base_height = 80;
base_thickness = 6;
hook_radius = 25;
hook_thickness = 8;
screw_hole_diameter = 4;

module hook_arm() {
    union() {
        translate([0, 0, 0])
            rotate([90, 0, 0])
                rotate_extrude(angle = 210, $fn = 120)
                    translate([hook_radius, 0, 0])
                        square([hook_thickness, hook_thickness], center = true);
        translate([hook_radius, 0, -hook_thickness / 2])
            cube([hook_thickness, hook_thickness, hook_thickness], center = true);
    }
}

module main() {
    difference() {
        union() {
            cube([base_width, base_height, base_thickness], center = false);
            translate([base_width / 2, base_height / 3, base_thickness])
                rotate([0, 0, 90])
                    hook_arm();
            translate([
                base_width / 2 - hook_thickness / 2,
                base_height / 3 - hook_thickness / 2,
                base_thickness
            ])
                cube([
                    hook_thickness,
                    hook_thickness,
                    hook_radius
                ], center = false);
        }
        for (y_pos = [base_height * 0.25, base_height * 0.75])
            translate([base_width / 2, y_pos, -1])
                cylinder(d = screw_hole_diameter, h = base_thickness + 2, center = false, $fn = 48);
    }
}

main();