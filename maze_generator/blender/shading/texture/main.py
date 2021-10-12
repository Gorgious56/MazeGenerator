from maze_generator.blender.shading.texture.constants import TEX_DISP_NAME


def generate_textures(textures, props) -> None:
    tex_disp = textures.get(TEX_DISP_NAME)
    if not tex_disp:
        tex_disp = textures.new(name=TEX_DISP_NAME, type="CLOUDS")
        tex_disp.noise_scale = 50
    tex_disp.cloud_type = "COLOR"
    props.textures.displacement = tex_disp
