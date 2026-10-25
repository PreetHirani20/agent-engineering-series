`split_name()` in `people.py` raises `ValueError` for one-word names like `"Cher"` or `"Madonna"`. These are real customers. A one-word name should return the name as the first name and an empty last name: `split_name("Cher") == ("Cher", "")`.

While you're there:
- Extra spaces anywhere should not matter: `split_name("  Ada   Lovelace ") == ("Ada", "Lovelace")`.
- An empty or blank string returns `("", "")`.
