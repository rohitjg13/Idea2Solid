slot_count = 5;
slot_width = 14;
slot_depth = 26;
slot_spacing = 24;
base_length = 150;
base_width = 48;
base_height = 40;
corner_radius = 3;

module rounded_block(size_vec, radius) {
    minkowski() {
        cube([
            size_vec[0] - 2 * radius,
            size_vec[1] - 2 * radius,
            size_vec[2] - 2 * radius
        ], center = false);
        sphere(r = radius, $fn = 48);
    }
}

module main() {
    difference() {
        rounded_block([base_length, base_width, base_height], corner_radius);
        for (i = [0 : slot_count - 1]) {
            translate([
                (base_length - (slot_count - 1) * slot_spacing) / 2 + i * slot_spacing,
                (base_width - slot_depth) / 2,
                base_height * 0.3
            ])
                cube([
                    slot_width,
                    slot_depth,
                    base_height
                ], center = false);
        }
    }
}

main();