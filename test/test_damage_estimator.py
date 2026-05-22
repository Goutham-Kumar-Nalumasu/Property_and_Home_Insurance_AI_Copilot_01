from app.tools.damage_estimator import damage_estimator


def test_damage_estimator_loads():
    assert damage_estimator.df is not None


def test_damage_estimator_search():
    result = damage_estimator.estimate(
        damage_type="burst pipe",
        property_size_category="3-bed semi-detached house",
    )

    assert "found" in result
    assert "matches" in result