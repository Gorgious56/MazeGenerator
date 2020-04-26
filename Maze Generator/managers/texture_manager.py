class TextureManager:
    tex_disp_name = 'MG_Tex_Disp'
    tex_disp = None

    def generate_textures(textures) -> None:
        self = TextureManager

        tex_disp = textures.get(self.tex_disp_name)
        if not tex_disp:
            tex_disp = textures.new(name=self.tex_disp_name, type='CLOUDS')
            tex_disp.noise_scale = 50
        tex_disp.cloud_type = 'COLOR'
        self.tex_disp = tex_disp
