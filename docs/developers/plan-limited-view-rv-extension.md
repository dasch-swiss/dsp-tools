# Plan: Extend `limited_view` to Support MovingImageRepresentation and AudioRepresentation

## Context

`default_permissions_overrule > limited_view` restricts Restricted View (RV) permissions to certain media classes.
Previously the DSP-API backend only supported RV for `StillImageRepresentation` subclasses,
so dsp-tools validated and hard-coded accordingly.
The backend now also supports RV for `MovingImageRepresentation` and `AudioRepresentation`,
so dsp-tools must be updated to:

1. **Validate** that `limited_view` accepts subclasses of all three representation types
2. **Create** the correct DOAPs (with the right `forProperty` IRI) for each type
3. **Read back** (`dsp-tools get`) the new DOAP types correctly

There is no `hasFileValue` super-property usable in DOAPs — each type needs its own DOAP.
For `limited_view: "all"`, three DOAPs are created (one per property type, all with `forResourceClass: null`).

---

## Files to Change

### 1. `src/dsp_tools/commands/create/models/create_problems.py`

Update `INVALID_LIMITED_VIEW_PERMISSIONS_OVERRULE` error message to mention all three representation types:

```
"This class cannot be used in limited_view permissions because it is not a subclass of "
"StillImageRepresentation, MovingImageRepresentation, or AudioRepresentation."
```

### 2. `src/dsp_tools/commands/create/models/parsed_project.py`

Add three classified lists to `LimitedViewPermissionsSelection`
(populated during validation, consumed by DOAP creation):

```python
@dataclass
class LimitedViewPermissionsSelection:
    limited_selection: list[str]          # raw IRIs from parsing (unchanged)
    still_image: list[str] = field(default_factory=list)   # classified by validation
    moving_image: list[str] = field(default_factory=list)
    audio: list[str] = field(default_factory=list)
```

### 3. `src/dsp_tools/commands/create/project_validate.py`

- **Rename** `_get_still_image_classes` → `_get_limited_view_classes`.
  Change it to return a **tuple of three sets** `(still_image, moving_image, audio)`
  by traversing descendants of each of the three knora-api parent classes.

- **Update** `_check_limited_view_selection` signature:
    - Accept `still_image_classes`, `moving_image_classes`, `audio_classes` sets
    - Validate that each IRI belongs to one of the three sets (existing unknown-IRI check stays unchanged)
    - After validation, **populate** `limited_view.still_image`, `limited_view.moving_image`,
      `limited_view.audio` from the inputs (mutation is intentional — the model carries the classification
      forward for DOAP creation)

- **Update** `_check_for_invalid_default_permissions_overrule` to accept the three sets
  and pass them to `_check_limited_view_selection`.

- **Update** the call site in `_complex_parsed_project_validation`:

```python
still_image_classes, moving_image_classes, audio_classes = _get_limited_view_classes(cls_flattened)
```

### 4. `src/dsp_tools/commands/create/create_on_server/default_permissions.py`

- **Change** `_create_one_limited_view_overrule` to accept `file_value_prop_iri: str`
  instead of hard-coding `hasStillImageFileValue`.

- **Update** `_handle_limited_view_overrule`:
    - `LimitedViewPermissionsSelection` case: iterate the three classified lists,
      calling `_create_one_limited_view_overrule` with the correct property IRI per type:
        - `still_image` → `knora-api:hasStillImageFileValue`
        - `moving_image` → `knora-api:hasMovingImageFileValue`
        - `audio` → `knora-api:hasAudioFileValue`
    - `GlobalLimitedViewPermission.ALL` case: create **three DOAPs**
      (one for each property, `forResourceClass=None`)

Property IRIs (prefix: `http://api.knora.org/ontology/knora-api/v2#`):

- `hasStillImageFileValue`
- `hasMovingImageFileValue`
- `hasAudioFileValue`

### 5. `src/dsp_tools/commands/get/get_permissions.py`

The `get` command reads existing project DOAPs back from the server.
It currently only recognises `hasStillImageFileValue` DOAPs for `limited_view`.
Update to also handle the two new property types:

- `_categorize_doaps`: extend the match to also categorise `hasMovingImageFileValue`
  and `hasAudioFileValue` DOAPs into `has_img_specific_class_doaps` / `has_img_all_classes_doaps`.
- `_construct_overrule_object`: map DOAPs for all three property types back to the `limited_view` list.
- Update related comments/log messages that reference `hasStillImageFileValue` exclusively.

### 6. `docs/data-model/json-project/overview.md`

- Update the inline comment:
  `"all" | [  // "all" means all subclasses of StillImageRepresentation`
  → `"all" | [  // "all" means all subclasses of StillImageRepresentation, MovingImageRepresentation,`
  `//           and AudioRepresentation`
- Update the `limited_view` bullet description to mention all three representation types.

### 7. Tests

**`test/unittests/commands/create/project_validate/test_default_permissions_overrule.py`**:

- Update import: `_get_still_image_classes` → `_get_limited_view_classes`
- Rename `TestGetStillImageClasses` → `TestGetLimitedViewClasses`;
  add parallel test cases for MovingImage and Audio subclasses
- Add tests for `_check_for_invalid_default_permissions_overrule` accepting MovingImage/Audio subclasses
  and correctly rejecting other classes (e.g. `DocumentRepresentation` subclasses)

**`test/integration/commands/create/test_project_create_default_permissions.py`**:

- Update `test_create_default_permissions_with_limited_view_all` to expect **three DOAP calls**
  (one per file value property)
- Update `test_create_default_permissions_with_limited_view_specific_classes` to verify correct
  `forProperty` per class type; add cases for moving image and audio classes

### 8. `src/dsp_tools/commands/create/CLAUDE.md`

Update the validation section:

> "validates that all referenced IRIs exist and are `StillImageRepresentation` subclasses"

→

> "validates that all referenced IRIs exist and are subclasses of `StillImageRepresentation`,
> `MovingImageRepresentation`, or `AudioRepresentation`"

---

## Architecture Note

Mutating `LimitedViewPermissionsSelection.still_image/.moving_image/.audio` during validation
is a pragmatic choice: the class-hierarchy information needed for DOAP creation is only available
at validation time (from `ParsedClass` objects).
Carrying it forward via the model avoids adding new parameters to `create_default_permissions`
or running another traversal pass later.

---

## Verification

```bash
pytest test/unittests/commands/create/project_validate/test_default_permissions_overrule.py -v
pytest test/integration/commands/create/test_project_create_default_permissions.py -v
just lint
```
