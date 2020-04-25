from . cell_type_manager import POLAR

REP_REGULAR = '0'
REP_CYLINDER = '1'
REP_MEOBIUS = '2'
REP_TORUS = '3'
REP_BOX = '4'


def generate_space_rep_enum(self, context):
    ret = [(REP_REGULAR, 'Plane', '')]
    if self.cell_type != POLAR:
        ret.extend((
            (REP_CYLINDER, 'Cylinder', ''),
            (REP_MEOBIUS, 'Moebius', ''),
            (REP_TORUS, 'Torus', ''),
            (REP_BOX, 'Box', '')))
    return ret
