from nodes.neurochain.neurochain_utils.fill_template import FillTemplate


def test_simple_template_replacement():
    template = "Hello [name]!"
    data = {"name": "World"}

    fill = FillTemplate()
    result = fill.process(data, template)[0]

    assert result == "Hello World!"


def test_multiple_replacements():
    template = "My name is [name] and I am [age] years old"
    data = {"name": "Alice", "age": "30"}

    fill = FillTemplate()
    result = fill.process(data, template)[0]

    assert result == "My name is Alice and I am 30 years old"


def test_nested_dict_replacement():
    template = "User: [user.name], Email: [user.contact.email]"
    data = {"user": {"name": "Bob", "contact": {"email": "bob@example.com"}}}

    fill = FillTemplate()
    result = fill.process(data, template)[0]

    assert result == "User: Bob, Email: bob@example.com"


def test_no_replacements_needed():
    template = "Plain text without any replacements"
    data = {"unused": "value"}

    fill = FillTemplate()
    result = fill.process(data, template)[0]

    assert result == "Plain text without any replacements"


def test_empty_dict():
    template = "Hello [name]!"
    data = {}

    fill = FillTemplate()
    result = fill.process(data, template)[0]

    assert result == "Hello [name]!"


def test_non_string_values():
    template = "Number: [number], Boolean: [bool], None: [null]"
    data = {"number": 42, "bool": True, "null": None}

    fill = FillTemplate()
    result = fill.process(data, template)[0]

    assert result == "Number: 42, Boolean: True, None: None"
