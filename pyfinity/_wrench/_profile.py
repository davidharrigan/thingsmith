from __future__ import annotations

import math

from build123d import (
    Align,
    BaseSketchObject,
    BuildLine,
    BuildSketch,
    Mode,
    Polyline,
    RadiusArc,
    make_face,
)


class InsertProfile(BaseSketchObject):
    __profile_width: float
    __profile_height: float

    def __init__(
        self,
        width: float,
        height: float,
        rotation: float = 0,
        align: Align | tuple[Align, Align] | None = None,
        mode: Mode = Mode.ADD,
    ) -> None:
        angle_degrees = 40
        angle_radians = math.radians(angle_degrees)
        bottom_width = width * (2 / 5)
        angle_height = (width - bottom_width) * math.tan(angle_radians)

        lip_w = 3
        lip_h = 3
        l0 = (lip_w, 0)
        l1 = (lip_w, -lip_h / 2)
        l2 = (0, -lip_h)

        p0 = (0, 0)  # top left
        p1 = (0, -height)  # bottom left
        p2 = (bottom_width, -height)  # bottm middle
        p3 = (width, -angle_height)  # bottom right
        p4 = (width, 0)  # top right

        with BuildSketch() as profile:
            with BuildLine():
                Polyline(l0, l1, l2)
                RadiusArc(l2, p0, -100)
                Polyline(p0, p1, p2, p3, p4, l0)
            make_face()

        self.__profile_width = width
        self.__profile_height = height
        super().__init__(profile.face(), rotation, align, mode)

    @property
    def profile_width(self) -> float:
        return self.__profile_width

    @property
    def profile_height(self) -> float:
        return self.__profile_height

    @staticmethod
    def from_collection(
        dimensions: list[tuple[float, float]],
        rotation: float = 0,
        align: Align | tuple[Align, Align] | None = None,
        mode: Mode = Mode.ADD,
    ) -> list[InsertProfile]:
        profiles: list[InsertProfile] = []
        for w, h in dimensions:
            profile = InsertProfile(w, h, rotation, align, mode)
            profiles.append(profile)
        return profiles
