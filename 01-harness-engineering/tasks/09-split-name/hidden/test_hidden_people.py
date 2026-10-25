from people import initials, split_name


def test_whitespace():
    assert split_name("  Ada   Lovelace ") == ("Ada", "Lovelace")
    assert split_name("Mary  Ann   Smith") == ("Mary Ann", "Smith")


def test_blank():
    assert split_name("") == ("", "")
    assert split_name("   ") == ("", "")


def test_particles_still_work():
    assert split_name("Vincent  van Gogh") == ("Vincent", "van Gogh")
    assert split_name("Jean Claude de la Fontaine") == ("Jean Claude", "de la Fontaine")


def test_mononym_initials():
    assert initials("Madonna") == "M"
