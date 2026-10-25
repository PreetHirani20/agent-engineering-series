from people import initials, split_name


def test_simple():
    assert split_name("Ada Lovelace") == ("Ada", "Lovelace")


def test_middle_names_stay_with_first():
    assert split_name("Mary Ann Smith") == ("Mary Ann", "Smith")


def test_particles_stay_with_last():
    assert split_name("Ludwig van Beethoven") == ("Ludwig", "van Beethoven")
    assert split_name("Charles de la Vallee") == ("Charles", "de la Vallee")


def test_initials():
    assert initials("Ludwig van Beethoven") == "LB"


def test_one_word_name():
    assert split_name("Cher") == ("Cher", "")
