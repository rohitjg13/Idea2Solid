base_width = 80;
base_depth = 90;
back_height = 120;
tilt_angle = 18;
panel_thickness = 4;
lip_height = 10;

module main() {
    union() {
        cube([base_width, base_depth, panel_thickness], center = false);
        translate([0, 0, panel_thickness])
            cube([base_width, panel_thickness, lip_height], center = false);
        translate([0, base_depth - panel_thickness, panel_thickness])
            rotate([tilt_angle, 0, 0])
                cube([base_width, panel_thickness, back_height], center = false);
        translate([panel_thickness, base_depth - 2 * panel_thickness, panel_thickness])
            hull() {
                cube([panel_thickness, panel_thickness, panel_thickness], center = false);
                translate([0, panel_thickness, back_height * 0.5])
                    cube([
                        panel_thickness,
                        panel_thickness,
                        panel_thickness
                    ], center = false);
            }
    }
}

main();