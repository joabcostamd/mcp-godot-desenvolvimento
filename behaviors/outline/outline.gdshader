shader_type canvas_item;
uniform vec4 color : source_color = vec4(1.0);
uniform float width : hint_range(1.0, 10.0) = 2.0;
uniform bool enabled = true;

void fragment() {
	if (!enabled) { COLOR = texture(TEXTURE, UV); return; }
	vec4 tex = texture(TEXTURE, UV);
	vec2 ps = TEXTURE_PIXEL_SIZE * width;
	float a = tex.a;
	float max_a = a;
	max_a = max(max_a, texture(TEXTURE, UV + vec2(ps.x, 0)).a);
	max_a = max(max_a, texture(TEXTURE, UV + vec2(-ps.x, 0)).a);
	max_a = max(max_a, texture(TEXTURE, UV + vec2(0, ps.y)).a);
	max_a = max(max_a, texture(TEXTURE, UV + vec2(0, -ps.y)).a);
	if (a == 0.0 && max_a > 0.0) {
		COLOR = color;
	} else {
		COLOR = tex;
	}
}
