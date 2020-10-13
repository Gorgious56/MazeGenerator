import bpy


TEX_DISP_NAME = 'MG_Tex_Disp'
# tex_disp = None


def generate_textures(textures, props) -> None:
    tex_disp = textures.get(TEX_DISP_NAME)
    if not tex_disp:
        tex_disp = textures.new(name=TEX_DISP_NAME, type='CLOUDS')
        tex_disp.noise_scale = 50
    tex_disp.cloud_type = 'COLOR'
    props.textures.displacement = tex_disp
    # tex_disp = tex_disp


class TexturesPropertyGroup(bpy.types.PropertyGroup):
    """
    Property group storing pointers to the textures
    """
    displacement: bpy.props.PointerProperty(
        name="Displacement",
        type=bpy.types.Texture)
