import pytest

from dsp_tools.commands.create.models.create_problems import CollectedProblems
from dsp_tools.commands.create.models.create_problems import InputProblemType
from dsp_tools.commands.create.models.parsed_ontology import ParsedClass
from dsp_tools.commands.create.models.parsed_project import ClassifiedLimitedViewPermissions
from dsp_tools.commands.create.models.parsed_project import DefaultPermissions
from dsp_tools.commands.create.models.parsed_project import GlobalLimitedViewPermission
from dsp_tools.commands.create.models.parsed_project import LimitedViewPermissionsSelection
from dsp_tools.commands.create.models.parsed_project import ParsedPermissions
from dsp_tools.commands.create.project_validate import _check_for_invalid_default_permissions_overrule
from dsp_tools.commands.create.project_validate import _get_limited_view_classes
from dsp_tools.utils.rdf_constants import KNORA_API_PREFIX
from test.unittests.commands.create.constants import ONTO_IRI
from test.unittests.commands.create.constants import ONTO_NAMESPACE_STR

KNORA_STILL_IMAGE = f"{KNORA_API_PREFIX}StillImageRepresentation"
KNORA_MOVING_IMAGE = f"{KNORA_API_PREFIX}MovingImageRepresentation"
KNORA_AUDIO = f"{KNORA_API_PREFIX}AudioRepresentation"

TEST_STILL_IMAGE = f"{ONTO_NAMESPACE_STR}TestStillImage"
TEST_MOVING_IMAGE = f"{ONTO_NAMESPACE_STR}TestMovingImage"
TEST_AUDIO = f"{ONTO_NAMESPACE_STR}TestAudio"
TEST_RESOURCE = f"{ONTO_NAMESPACE_STR}TestResource"
TEST_PROPERTY = f"{ONTO_NAMESPACE_STR}hasName"


@pytest.fixture
def known_props() -> list[str]:
    return [TEST_PROPERTY]


@pytest.fixture
def known_classes() -> list[str]:
    return [TEST_STILL_IMAGE, TEST_MOVING_IMAGE, TEST_AUDIO, TEST_RESOURCE]


@pytest.fixture
def still_image_classes() -> set[str]:
    return {TEST_STILL_IMAGE, f"{ONTO_NAMESPACE_STR}TestStillImage2"}


@pytest.fixture
def moving_image_classes() -> set[str]:
    return {TEST_MOVING_IMAGE}


@pytest.fixture
def audio_classes() -> set[str]:
    return {TEST_AUDIO}


def test_check_overrule_no_overrule_private(
    known_props, known_classes, still_image_classes, moving_image_classes, audio_classes
) -> None:
    perm = ParsedPermissions(
        default_permissions=DefaultPermissions.PRIVATE,
        overrule_private=None,
        overrule_limited_view=GlobalLimitedViewPermission.NONE,
    )
    result = _check_for_invalid_default_permissions_overrule(
        perm, known_props, known_classes, still_image_classes, moving_image_classes, audio_classes
    )
    assert result.problems is None
    assert result.classified is None


def test_check_overrule_no_overrule_public(
    known_props, known_classes, still_image_classes, moving_image_classes, audio_classes
) -> None:
    perm = ParsedPermissions(
        default_permissions=DefaultPermissions.PUBLIC,
        overrule_private=None,
        overrule_limited_view=GlobalLimitedViewPermission.NONE,
    )
    result = _check_for_invalid_default_permissions_overrule(
        perm, known_props, known_classes, still_image_classes, moving_image_classes, audio_classes
    )
    assert result.problems is None
    assert result.classified is None


def test_check_overrule_no_limited_view(
    known_props, known_classes, still_image_classes, moving_image_classes, audio_classes
) -> None:
    perm = ParsedPermissions(
        default_permissions=DefaultPermissions.PUBLIC,
        overrule_private=[TEST_RESOURCE],
        overrule_limited_view=GlobalLimitedViewPermission.NONE,
    )
    result = _check_for_invalid_default_permissions_overrule(
        perm, known_props, known_classes, still_image_classes, moving_image_classes, audio_classes
    )
    assert result.problems is None
    assert result.classified is None


def test_check_overrule_limited_view_all(
    known_props, known_classes, still_image_classes, moving_image_classes, audio_classes
) -> None:
    perm = ParsedPermissions(
        default_permissions=DefaultPermissions.PUBLIC,
        overrule_private=None,
        overrule_limited_view=GlobalLimitedViewPermission.ALL,
    )
    result = _check_for_invalid_default_permissions_overrule(
        perm, known_props, known_classes, still_image_classes, moving_image_classes, audio_classes
    )
    assert result.problems is None
    assert result.classified is None


def test_check_overrule_valid_still_image(
    known_props, known_classes, still_image_classes, moving_image_classes, audio_classes
) -> None:
    perm = ParsedPermissions(
        default_permissions=DefaultPermissions.PUBLIC,
        overrule_private=None,
        overrule_limited_view=LimitedViewPermissionsSelection([TEST_STILL_IMAGE]),
    )
    result = _check_for_invalid_default_permissions_overrule(
        perm, known_props, known_classes, still_image_classes, moving_image_classes, audio_classes
    )
    assert result.problems is None
    assert isinstance(result.classified, ClassifiedLimitedViewPermissions)
    assert result.classified.still_image == [TEST_STILL_IMAGE]
    assert result.classified.moving_image == []
    assert result.classified.audio == []


def test_check_overrule_valid_moving_image(
    known_props, known_classes, still_image_classes, moving_image_classes, audio_classes
) -> None:
    perm = ParsedPermissions(
        default_permissions=DefaultPermissions.PUBLIC,
        overrule_private=None,
        overrule_limited_view=LimitedViewPermissionsSelection([TEST_MOVING_IMAGE]),
    )
    result = _check_for_invalid_default_permissions_overrule(
        perm, known_props, known_classes, still_image_classes, moving_image_classes, audio_classes
    )
    assert result.problems is None
    assert isinstance(result.classified, ClassifiedLimitedViewPermissions)
    assert result.classified.still_image == []
    assert result.classified.moving_image == [TEST_MOVING_IMAGE]
    assert result.classified.audio == []


def test_check_overrule_valid_audio(
    known_props, known_classes, still_image_classes, moving_image_classes, audio_classes
) -> None:
    perm = ParsedPermissions(
        default_permissions=DefaultPermissions.PUBLIC,
        overrule_private=None,
        overrule_limited_view=LimitedViewPermissionsSelection([TEST_AUDIO]),
    )
    result = _check_for_invalid_default_permissions_overrule(
        perm, known_props, known_classes, still_image_classes, moving_image_classes, audio_classes
    )
    assert result.problems is None
    assert isinstance(result.classified, ClassifiedLimitedViewPermissions)
    assert result.classified.still_image == []
    assert result.classified.moving_image == []
    assert result.classified.audio == [TEST_AUDIO]


def test_check_overrule_unknown_private(
    known_props, known_classes, still_image_classes, moving_image_classes, audio_classes
) -> None:
    perm = ParsedPermissions(
        default_permissions=DefaultPermissions.PUBLIC,
        overrule_private=[f"{ONTO_NAMESPACE_STR}Unknown"],
        overrule_limited_view=LimitedViewPermissionsSelection([TEST_STILL_IMAGE]),
    )
    result = _check_for_invalid_default_permissions_overrule(
        perm, known_props, known_classes, still_image_classes, moving_image_classes, audio_classes
    )
    assert isinstance(result.problems, CollectedProblems)
    assert len(result.problems.problems) == 1
    assert result.problems.problems[0].problem == InputProblemType.UNKNOWN_IRI_IN_PERMISSIONS_OVERRULE
    assert result.problems.problems[0].problematic_object == "onto:Unknown"


def test_check_overrule_unknown_limited_view(
    known_props, known_classes, still_image_classes, moving_image_classes, audio_classes
) -> None:
    perm = ParsedPermissions(
        default_permissions=DefaultPermissions.PUBLIC,
        overrule_private=None,
        overrule_limited_view=LimitedViewPermissionsSelection([f"{ONTO_NAMESPACE_STR}Unknown"]),
    )
    result = _check_for_invalid_default_permissions_overrule(
        perm, known_props, known_classes, still_image_classes, moving_image_classes, audio_classes
    )
    assert isinstance(result.problems, CollectedProblems)
    assert len(result.problems.problems) == 1
    assert result.problems.problems[0].problem == InputProblemType.UNKNOWN_IRI_IN_PERMISSIONS_OVERRULE
    assert result.problems.problems[0].problematic_object == "onto:Unknown"


def test_check_overrule_invalid_wrong_superclass(
    known_props, known_classes, still_image_classes, moving_image_classes, audio_classes
) -> None:
    perm = ParsedPermissions(
        default_permissions=DefaultPermissions.PUBLIC,
        overrule_private=None,
        overrule_limited_view=LimitedViewPermissionsSelection([TEST_RESOURCE]),
    )
    result = _check_for_invalid_default_permissions_overrule(
        perm, known_props, known_classes, still_image_classes, moving_image_classes, audio_classes
    )
    assert isinstance(result.problems, CollectedProblems)
    assert len(result.problems.problems) == 1
    assert result.problems.problems[0].problem == InputProblemType.INVALID_LIMITED_VIEW_PERMISSIONS_OVERRULE
    assert result.problems.problems[0].problematic_object == "onto:TestResource"


class TestGetLimitedViewClasses:
    def test_no_limited_view_classes(self) -> None:
        classes = [
            ParsedClass(
                name=f"{ONTO_NAMESPACE_STR}TextResource",
                labels={"en": "Text"},
                comments={},
                supers=[f"{KNORA_API_PREFIX}Resource"],
                onto_iri=ONTO_IRI,
            ),
            ParsedClass(
                name=f"{ONTO_NAMESPACE_STR}PDFResource",
                labels={"en": "PDF"},
                comments={},
                supers=[f"{KNORA_API_PREFIX}DocumentRepresentation"],
                onto_iri=ONTO_IRI,
            ),
        ]
        still_image, moving_image, audio = _get_limited_view_classes(classes)
        assert still_image == set()
        assert moving_image == set()
        assert audio == set()

    def test_direct_still_image_inheritance(self) -> None:
        classes = [
            ParsedClass(
                name=f"{ONTO_NAMESPACE_STR}Photo",
                labels={"en": "Photo"},
                comments={},
                supers=[KNORA_STILL_IMAGE],
                onto_iri=ONTO_IRI,
            ),
            ParsedClass(
                name=f"{ONTO_NAMESPACE_STR}Painting",
                labels={"en": "Painting"},
                comments={},
                supers=[KNORA_STILL_IMAGE],
                onto_iri=ONTO_IRI,
            ),
        ]
        still_image, moving_image, audio = _get_limited_view_classes(classes)
        assert still_image == {f"{ONTO_NAMESPACE_STR}Photo", f"{ONTO_NAMESPACE_STR}Painting"}
        assert moving_image == set()
        assert audio == set()

    def test_direct_moving_image_inheritance(self) -> None:
        classes = [
            ParsedClass(
                name=f"{ONTO_NAMESPACE_STR}Video",
                labels={"en": "Video"},
                comments={},
                supers=[KNORA_MOVING_IMAGE],
                onto_iri=ONTO_IRI,
            ),
        ]
        still_image, moving_image, audio = _get_limited_view_classes(classes)
        assert still_image == set()
        assert moving_image == {f"{ONTO_NAMESPACE_STR}Video"}
        assert audio == set()

    def test_direct_audio_inheritance(self) -> None:
        classes = [
            ParsedClass(
                name=f"{ONTO_NAMESPACE_STR}Recording",
                labels={"en": "Recording"},
                comments={},
                supers=[KNORA_AUDIO],
                onto_iri=ONTO_IRI,
            ),
        ]
        still_image, moving_image, audio = _get_limited_view_classes(classes)
        assert still_image == set()
        assert moving_image == set()
        assert audio == {f"{ONTO_NAMESPACE_STR}Recording"}

    def test_deep_still_image_inheritance(self) -> None:
        classes = [
            ParsedClass(
                name=f"{ONTO_NAMESPACE_STR}Level1",
                labels={"en": "L1"},
                comments={},
                supers=[KNORA_STILL_IMAGE],
                onto_iri=ONTO_IRI,
            ),
            ParsedClass(
                name=f"{ONTO_NAMESPACE_STR}Level2",
                labels={"en": "L2"},
                comments={},
                supers=[f"{ONTO_NAMESPACE_STR}Level1", f"{KNORA_API_PREFIX}Resource"],
                onto_iri=ONTO_IRI,
            ),
            ParsedClass(
                name=f"{ONTO_NAMESPACE_STR}Level3",
                labels={"en": "L3"},
                comments={},
                supers=[f"{ONTO_NAMESPACE_STR}Level2"],
                onto_iri=ONTO_IRI,
            ),
            ParsedClass(
                name=f"{ONTO_NAMESPACE_STR}Level4",
                labels={"en": "L4"},
                comments={},
                supers=[f"{ONTO_NAMESPACE_STR}Level3"],
                onto_iri=ONTO_IRI,
            ),
            ParsedClass(
                name=f"{ONTO_NAMESPACE_STR}Level5",
                labels={"en": "L5"},
                comments={},
                supers=[f"{ONTO_NAMESPACE_STR}Level4"],
                onto_iri=ONTO_IRI,
            ),
            ParsedClass(
                name=f"{ONTO_NAMESPACE_STR}Level6",
                labels={"en": "L6"},
                comments={},
                supers=[f"{ONTO_NAMESPACE_STR}Level5"],
                onto_iri=ONTO_IRI,
            ),
            ParsedClass(
                name=f"{ONTO_NAMESPACE_STR}Level7",
                labels={"en": "L7"},
                comments={},
                supers=[f"{ONTO_NAMESPACE_STR}Level6"],
                onto_iri=ONTO_IRI,
            ),
        ]
        still_image, moving_image, audio = _get_limited_view_classes(classes)
        assert still_image == {
            f"{ONTO_NAMESPACE_STR}Level1",
            f"{ONTO_NAMESPACE_STR}Level2",
            f"{ONTO_NAMESPACE_STR}Level3",
            f"{ONTO_NAMESPACE_STR}Level4",
            f"{ONTO_NAMESPACE_STR}Level5",
            f"{ONTO_NAMESPACE_STR}Level6",
            f"{ONTO_NAMESPACE_STR}Level7",
        }
        assert moving_image == set()
        assert audio == set()

    def test_complex_multi_branch_hierarchy(self) -> None:
        classes = [
            ParsedClass(
                name=f"{ONTO_NAMESPACE_STR}Photo",
                labels={"en": "Photo"},
                comments={},
                supers=[KNORA_STILL_IMAGE],
                onto_iri=ONTO_IRI,
            ),
            ParsedClass(
                name=f"{ONTO_NAMESPACE_STR}Painting",
                labels={"en": "Painting"},
                comments={},
                supers=[KNORA_STILL_IMAGE],
                onto_iri=ONTO_IRI,
            ),
            ParsedClass(
                name=f"{ONTO_NAMESPACE_STR}DigitalPhoto",
                labels={"en": "Digital"},
                comments={},
                supers=[f"{ONTO_NAMESPACE_STR}Photo"],
                onto_iri=ONTO_IRI,
            ),
            ParsedClass(
                name=f"{ONTO_NAMESPACE_STR}FilmPhoto",
                labels={"en": "Film"},
                comments={},
                supers=[f"{ONTO_NAMESPACE_STR}Photo"],
                onto_iri=ONTO_IRI,
            ),
            ParsedClass(
                name=f"{ONTO_NAMESPACE_STR}OilPainting",
                labels={"en": "Oil"},
                comments={},
                supers=[f"{ONTO_NAMESPACE_STR}Painting"],
                onto_iri=ONTO_IRI,
            ),
            ParsedClass(
                name=f"{ONTO_NAMESPACE_STR}Watercolor",
                labels={"en": "Water"},
                comments={},
                supers=[f"{ONTO_NAMESPACE_STR}Painting"],
                onto_iri=ONTO_IRI,
            ),
            ParsedClass(
                name=f"{ONTO_NAMESPACE_STR}HDRPhoto",
                labels={"en": "HDR"},
                comments={},
                supers=[f"{ONTO_NAMESPACE_STR}DigitalPhoto"],
                onto_iri=ONTO_IRI,
            ),
        ]
        still_image, moving_image, audio = _get_limited_view_classes(classes)
        assert still_image == {
            f"{ONTO_NAMESPACE_STR}Photo",
            f"{ONTO_NAMESPACE_STR}Painting",
            f"{ONTO_NAMESPACE_STR}DigitalPhoto",
            f"{ONTO_NAMESPACE_STR}FilmPhoto",
            f"{ONTO_NAMESPACE_STR}OilPainting",
            f"{ONTO_NAMESPACE_STR}Watercolor",
            f"{ONTO_NAMESPACE_STR}HDRPhoto",
        }
        assert moving_image == set()
        assert audio == set()

    def test_mixed_representation_types(self) -> None:
        classes = [
            ParsedClass(
                name=f"{ONTO_NAMESPACE_STR}Photo",
                labels={"en": "Photo"},
                comments={},
                supers=[KNORA_STILL_IMAGE],
                onto_iri=ONTO_IRI,
            ),
            ParsedClass(
                name=f"{ONTO_NAMESPACE_STR}DigitalPhoto",
                labels={"en": "Digital"},
                comments={},
                supers=[f"{ONTO_NAMESPACE_STR}Photo"],
                onto_iri=ONTO_IRI,
            ),
            ParsedClass(
                name=f"{ONTO_NAMESPACE_STR}Video",
                labels={"en": "Video"},
                comments={},
                supers=[KNORA_MOVING_IMAGE],
                onto_iri=ONTO_IRI,
            ),
            ParsedClass(
                name=f"{ONTO_NAMESPACE_STR}Recording",
                labels={"en": "Recording"},
                comments={},
                supers=[KNORA_AUDIO],
                onto_iri=ONTO_IRI,
            ),
            ParsedClass(
                name=f"{ONTO_NAMESPACE_STR}PDF",
                labels={"en": "PDF"},
                comments={},
                supers=[f"{KNORA_API_PREFIX}DocumentRepresentation"],
                onto_iri=ONTO_IRI,
            ),
            ParsedClass(
                name=f"{ONTO_NAMESPACE_STR}Text",
                labels={"en": "Text"},
                comments={},
                supers=[f"{KNORA_API_PREFIX}Resource"],
                onto_iri=ONTO_IRI,
            ),
        ]
        still_image, moving_image, audio = _get_limited_view_classes(classes)
        assert still_image == {f"{ONTO_NAMESPACE_STR}Photo", f"{ONTO_NAMESPACE_STR}DigitalPhoto"}
        assert moving_image == {f"{ONTO_NAMESPACE_STR}Video"}
        assert audio == {f"{ONTO_NAMESPACE_STR}Recording"}
