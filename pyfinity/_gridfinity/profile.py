from __future__ import annotations

from dataclasses import dataclass, field

from build123d import (
    Align,
    BaseSketchObject,
    BuildLine,
    BuildSketch,
    Mode,
    Polyline,
    make_face,
)

from pyfinity._gridfinity.spec import GF


@dataclass(frozen=True)
class ProfileSections:
    """Base class for profile section measurements in mm."""

    bottom: float
    middle: float
    top: float

    @property
    def total_height(self) -> float:
        return self.bottom + self.middle + self.top


@dataclass(frozen=True)
class BaseplateSections(ProfileSections):
    bottom: float = field(default=GF.BASEPLATE_BOTTOM_SECTION, init=False)
    middle: float = field(default=GF.BASEPLATE_MIDDLE_SECTION, init=False)
    top: float = field(default=GF.BASEPLATE_TOP_SECTION, init=False)


@dataclass(frozen=True)
class StackingLipSections(ProfileSections):
    bottom = GF.STACKING_LIP_BOTTOM_SECTION
    middle = GF.STACKING_LIP_MIDDLE_SECTION
    top = GF.STACKING_LIP_TOP_SECTION


class Profile(BaseSketchObject):
    def __init__(
        self,
        sections: ProfileSections,
        rotation: float = 0,
        align: Align | tuple[Align, Align] | None = None,
        mode: Mode = Mode.ADD,
    ) -> None:
        with BuildSketch() as profile:
            with BuildLine():
                Polyline(
                    (0, 0),
                    (0, sections.total_height),
                    (
                        sections.top,
                        sections.bottom + sections.middle,
                    ),
                    (sections.top, sections.bottom),
                    (sections.bottom + sections.top, 0),
                    close=True,
                )
            make_face()
        super().__init__(profile.face(), rotation, align, mode)
