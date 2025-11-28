clip_width = 28;
clip_depth = 18;
clip_height = 12;
slot_diameter = 8;
gap_width = 2;
base_thickness = 2;

module main() {
    difference() {
        union() {
            cube([clip_width, clip_depth, base_thickness], center = false);
            translate([0, 0, base_thickness])
                cube([
                    clip_width,
                    clip_depth,
                    clip_height - base_thickness
                ], center = false);
        }
        translate([
            clip_width / 2,
            clip_depth / 2,
            base_thickness + slot_diameter / 2
        ])
            rotate([0, 90, 0])
                cylinder(d = slot_diameter, h = clip_width + 4, center = true, $fn = 64);
        translate([
            (clip_width - gap_width) / 2,
            -1,
            base_thickness
        ])
            cube([gap_width, clip_depth + 2, clip_height], center = false);
    }
}

main();