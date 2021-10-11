def draw(self, context):
    self.layout.prop(context.scene.mg_props.algorithm, "algorithm", icon="HAND", text="Solver")
