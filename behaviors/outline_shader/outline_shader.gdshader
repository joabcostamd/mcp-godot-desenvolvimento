shader_type canvas_item;
uniform vec4 outline_color: source_color=vec4(0.0,1.0,1.0,1.0);
uniform float outline_width: hint_range(0.0,5.0)=1.0;
void fragment(){
	vec4 tex=texture(TEXTURE,UV);
	vec2 ps=TEXTURE_PIXEL_SIZE*outline_width;
	float a=tex.a;
	a=max(a,texture(TEXTURE,UV+vec2(ps.x,0)).a);
	a=max(a,texture(TEXTURE,UV+vec2(-ps.x,0)).a);
	a=max(a,texture(TEXTURE,UV+vec2(0,ps.y)).a);
	a=max(a,texture(TEXTURE,UV+vec2(0,-ps.y)).a);
	if(tex.a==0.0&&a>0.0) COLOR=outline_color; else COLOR=tex;
}
