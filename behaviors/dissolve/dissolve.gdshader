shader_type canvas_item;
uniform float progress: hint_range(0.0,1.0)=0.0;
uniform float edge_width: hint_range(0.0,0.5)=0.1;
uniform vec4 edge_color: source_color=vec4(1.0,0.5,0.0,1.0);
uniform sampler2D noise_texture: repeat_enable;
void fragment(){
	vec4 tex=texture(TEXTURE,UV);
	float noise=texture(noise_texture,UV).r;
	float threshold=progress+edge_width*noise;
	if(noise<threshold-progress) discard;
	if(noise<threshold) COLOR=edge_color;
	else COLOR=tex;
}
