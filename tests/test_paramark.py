import pytest


class Foo:
    def __init__(self, some_option=42, another_option='test'):
        self.some_option = some_option
        self.another_option = another_option


class Bar:
    def __init__(self, some_option=True, another_option=False):
        self.some_option = some_option
        self.another_option = another_option


# fmt: off
@pytest.fixture(indirect=True, params=[{}])
def foo(request):
    return Foo(**request.param)


@pytest.fixture(indirect=True, params=[{}])
def bar(request):
    return Bar(**request.param)


def test_default(foo, bar):
    assert foo.some_option == 42
    assert foo.another_option == 'test'

    assert bar.some_option is True
    assert bar.another_option is False


@pytest.mark.parametrize(
    ('foo.some_option', 'foo_plus_three',),
    [
        (1, 4),
        (7, 10),
    ],
)
def test_fixture_and_argument(foo, foo_plus_three):
    assert foo.some_option + 3 == foo_plus_three


@pytest.mark.parametrize(
    'qux',
    [
        4,
        10
    ]
)
@pytest.mark.parametrize(
    'foo.some_option',
    [
        1,
        2
    ],
)
def test_fixture_and_argument_product(foo, qux):
    assert foo.some_option in [1,2]
    assert qux in [4,10]


@pytest.mark.parametrize(
    ('foo.some_option', 'bar.some_option',),
    [
        (5, 5),
        (3, 7),
    ]
)
def test_two_fixtures(foo, bar):
    assert foo.some_option + bar.some_option == 10


@pytest.mark.parametrize(
    'foo',
    [
        pytest.param(dict(some_option=5, another_option=5), id="five-five"),
        pytest.param(dict(some_option=3, another_option=7), id="three-seven"),
        pytest.param(dict(some_option=1, another_option=9), id="one-nine"),
    ]
)
def test_parametrized_complete(foo):
    assert foo.some_option + foo.another_option == 10


@pytest.mark.parametrize(
    'foo',
    [
        dict(some_option=5, another_option=5),
        dict(some_option=3, another_option=7),
        dict(some_option=1, another_option=9),
    ]
)
@pytest.mark.parametrize(
    'foo',
    [
        pytest.param(dict(some_option=2, another_option=8)),
    ]
)
def test_parametrized_override_complete(foo):
    assert foo.some_option + foo.another_option == 10


@pytest.mark.parametrize(
    'foo.some_option',
    [
        0x420,
    ]
)
@pytest.mark.parametrize(
    'foo.another_option',
    [
        5,
        6,
    ]
)
def test_parametrized_update(foo):
    assert foo.some_option == 0x420
    assert foo.another_option in (5, 6)


@pytest.mark.parametrize(
    'foo',
    [
        dict(some_option=0x420, another_option='no override'),
    ]
)
@pytest.mark.parametrize(
    "foo.some_option",
    [
        "override"
    ]
)
def test_parametrized_override(foo):
    assert foo.some_option == "override"
    assert foo.another_option == "no override"


@pytest.mark.parametrize('foo.some_option', [3])
@pytest.mark.parametrize('foo.some_option', [1])
@pytest.mark.parametrize('foo.some_option', [2])
def test_parametrized_override_closest(foo):
    assert foo.some_option == 2


@pytest.mark.parametrize(
    ('foo.some_option', 'qux', 'bar.another_option'),
    [
        (0x420, 'QUX', 5),
    ]
)
def test_parametrized_mixed(foo, bar, qux):
    assert foo.some_option == 0x420
    assert bar.another_option == 5
    assert qux == 'QUX'



@pytest.mark.foo(some_option=24, another_option='five')
def test_shortcut(foo, bar):
    assert foo.some_option == 24
    assert foo.another_option == 'five'

    assert bar.some_option is True
    assert bar.another_option is False


@pytest.mark.foo(some_option=3)
@pytest.mark.foo(some_option=1)
@pytest.mark.foo(some_option=2)
def test_shortcut_override_closest(foo):
    assert foo.some_option == 2


@pytest.mark.parametrize(
    'foo',
    [dict(some_option=2)]
)
@pytest.mark.parametrize(
    'qux',
    ['QUX']
)
def test_parametrized_nonfixture(foo, qux):
    assert foo.some_option == 2
    assert qux == 'QUX'
