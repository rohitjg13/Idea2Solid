base_width = 230;
base_depth = 250;
rise_height = 90;
panel_thickness = 4;
vent_count = 6;
rib_thickness = 6;

module deck_profile() {
    polygon([
        [0, 0],
        [0, panel_thickness],
        [base_depth, rise_height + panel_thickness],
        [base_depth, rise_height]
    ]);
}

module deck_solid() {
    rotate([0, -90, 0])
        linear_extrude(height = base_width, center = false)
            deck_profile();
}

module vents() {
    spacing = base_width / (vent_count + 1);
    for (i = [1 : vent_count]) {
        translate([
            i * spacing,
            base_depth * 0.25,
            rise_height * 0.5
        ])
            rotate([0, 0, 0])
                cube([
                    rib_thickness * 1.5,
                    base_depth * 0.5,
                    panel_thickness * 2
                ], center = true);
    }
}

module ribs() {
    spacing = base_width / 3;
    for (x_pos = [spacing, base_width - spacing]) {
        translate([x_pos, 0, 0])
            rotate([0, -90, 0])
                linear_extrude(height = rib_thickness, center = false)
                    polygon([
                        [0, 0],
                        [0, panel_thickness],
                        [base_depth * 0.9, rise_height],
                        [base_depth * 0.9, rise_height - panel_thickness]
                    ]);
    }
}

module main() {
    difference() {
        deck_solid();
        vents();
    }
    ribs();
    translate([0, -panel_thickness, 0])
        cube([base_width, panel_thickness, panel_thickness], center = false);
}

main();