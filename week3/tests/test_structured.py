import pytest
from pydantic import ValidationError
from src.structured import MovieReview


def test_valid_output():
    """Valid output should pass validation."""
    data = {
        'title': 'Inception',
        'genre': 'Sci-Fi',
        'rating': 8.8,
        'summary': 'A thief enters dreams to steal secrets.',
        'recommended': True
    }
    review = MovieReview(**data)
    assert review.title == 'Inception'
    assert review.rating == 8.8


def test_missing_field_fails():
    """Missing required field should fail validation."""
    data = {
        'title': 'Inception',
        'genre': 'Sci-Fi',
        'summary': 'A thief enters dreams.',
        'recommended': True
    }
    with pytest.raises(ValidationError):
        MovieReview(**data)


def test_wrong_type_fails():
    """Wrong type for rating should fail validation."""
    data = {
        'title': 'Inception',
        'genre': 'Sci-Fi',
        'rating': 'very good',
        'summary': 'A thief enters dreams.',
        'recommended': True
    }
    with pytest.raises(ValidationError):
        MovieReview(**data)


def test_invalid_recommended_fails():
    """Non boolean recommended field should fail validation."""
    data = {
        'title': 'Inception',
        'genre': 'Sci-Fi',
        'rating': 8.8,
        'summary': 'A thief enters dreams.',
        'recommended': 'yes'
    }
    with pytest.raises(ValidationError):
        MovieReview(**data)
