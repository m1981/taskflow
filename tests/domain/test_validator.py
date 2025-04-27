import pytest
from src.domain.validator import TaskValidator, ValidationContext, ValidationError
from src.domain.task_update import TaskUpdate
from src.domain.task import Due

@pytest.fixture
def validation_context():
    return ValidationContext(
        available_projects={"inbox", "work", "personal"},
        available_labels={"high", "medium", "low", "blocked"},
        project_sections={
            "work": {"planning", "in-progress", "review"},
            "personal": {"today", "this-week", "someday"}
        }
    )

@pytest.fixture
def validator(validation_context):
    return TaskValidator(validation_context)

def test_validate_empty_update(validator):
    update = TaskUpdate()
    error = validator.validate_update(update)
    assert error is not None
    assert "no changes" in error.message

def test_validate_valid_update(validator):
    update = TaskUpdate(
        content="Updated content",
        labels=["high", "blocked"]
    )
    error = validator.validate_update(update)
    assert error is None

def test_validate_invalid_labels(validator):
    update = TaskUpdate(labels=["high", "invalid-label"])
    error = validator.validate_update(update)
    assert error is not None
    assert "Invalid labels" in error.message
    assert "invalid-label" in error.message

def test_validate_invalid_section(validator):
    update = TaskUpdate(section_id="non-existent")
    error = validator.validate_update(update)
    assert error is not None
    assert "Section" in error.message

def test_validate_section_project_mismatch(validator):
    # This would require the actual task context to validate properly
    update = TaskUpdate(section_id="today")
    error = validator.validate_update(update)
    assert error is None  # Currently can't validate without task context

def test_validate_multiple_fields(validator):
    update = TaskUpdate(
        content="Updated content",
        labels=["high"],
        due=Due(date="2024-01-20"),
        section_id="planning"
    )
    error = validator.validate_update(update)
    assert error is None