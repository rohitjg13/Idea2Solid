outer_length = 90;
outer_width = 60;
outer_height = 50;
wall_thickness = 3;
lip_height = 5;

module main() {
    difference() {
        cube([outer_length, outer_width, outer_height], center = false);
        translate([wall_thickness, wall_thickness, wall_thickness])
            cube([
                outer_length - 2 * wall_thickness,
                outer_width - 2 * wall_thickness,
                outer_height
            ], center = false);
    }
    translate([0, 0, outer_height - lip_height])
        difference() {
            cube([outer_length, outer_width, lip_height], center = false);
            translate([wall_thickness, wall_thickness, 0])
                cube([
                    outer_length - 2 * wall_thickness,
                    outer_width - 2 * wall_thickness,
                    lip_height
                ], center = false);
        }
}

main();