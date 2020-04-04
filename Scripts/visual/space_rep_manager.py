from . cell_type_manager import POLAR

REP_REGULAR = '0'
REP_STAIRS = '1'
REP_CYLINDER = '2'
REP_MEOBIUS = '3'
REP_TORUS = '4'
REP_BOX = '5'


def generate_space_rep_enum(self, context):
    ret = [(REP_REGULAR, 'Plane', ''), (REP_STAIRS, 'Stairs', '')]
    if self.cell_type != POLAR:
        ret.extend((
            (REP_CYLINDER, 'Cylinder', ''),
            (REP_MEOBIUS, 'Moebius', ''),
            (REP_TORUS, 'Torus', ''),
            (REP_BOX, 'Box', '')))
    return ret
