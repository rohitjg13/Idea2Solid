tooth_count = 20;
module_size = 2.5;
thickness = 8;
bore_diameter = 6;
hole_count = 6;
hole_diameter = 5;

pitch_radius = module_size * tooth_count / 2;
addendum = module_size;
dedendum = 1.25 * module_size;
root_radius = pitch_radius - dedendum;
outer_radius = pitch_radius + addendum;
tooth_arc = 2 * PI * pitch_radius / tooth_count;
tooth_thickness = tooth_arc * 0.45;

module tooth(angle) {
    rotate([0, 0, angle])
        translate([root_radius, -tooth_thickness / 2, 0])
            cube([
                outer_radius - root_radius,
                tooth_thickness,
                thickness
            ], center = false);
}

module main() {
    difference() {
        union() {
            cylinder(r = root_radius, h = thickness, $fn = tooth_count * 6);
            for (i = [0 : tooth_count - 1])
                tooth(i * 360 / tooth_count);
        }
        cylinder(d = bore_diameter, h = thickness + 2, center = false);
        for (i = [0 : hole_count - 1])
            rotate([0, 0, i * 360 / hole_count])
                translate([pitch_radius * 0.5, 0, 0])
                    cylinder(d = hole_diameter, h = thickness + 2, center = false);
    }
}

main();