from build123d import MM


class GF:
    """
    Gridfinity design constants.

    See: https://gridfinity.xyz/specification/
    """

    GRID_UNIT = 42 * MM  # 1u = 42mm in width/length
    HEIGHT_UNIT = 7.0 * MM  # 1u = 7mm in height
    FULL_2U_HEIGHT = 18.4 * MM  # Total height of a 2u module

    STACKING_LIP_BOTTOM_SECTION = 0.7 * MM
    STACKING_LIP_MIDDLE_SECTION = 1.8 * MM
    STACKING_LIP_TOP_SECTION = 1.9 * MM
    STACKING_LIP_OFFSET = 0.25 * MM
    STACKABLE_LIP_HEIGHT = 4.4 * MM

    BASEPLATE_TOP_SECTION = 2.15 * MM
    BASEPLATE_MIDDLE_SECTION = 1.8 * MM
    BASEPLATE_BOTTOM_SECTION = 0.7 * MM
    BASEPLATE_OUTER_RADIUS = 8 * MM
    BASEPLATE_HEIGHT = 5.0 * MM

    BLOCK_OUTER_RADIUS = 7.5 * MM
    BLOCK_SIZE = 41.5 * MM
