from namedlist import namedlist

import pytest


# fmt: off
@pytest.fixture(indirect=True)
def foo(request):
    Foo = namedlist('Foo', (
        ('some_option', 42),
        ('another_option', 'test'),
    ))

    return Foo(**request.param)


@pytest.fixture(indirect=True)
def bar(request):
    Bar = namedlist('Bar', (
        ('some_option', True),
        ('another_option', False),
    ))

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
    ('foo.some_option', 'bar.some_option',),
    [
        (5, 5),
        (3, 7),
    ]
)
def test_two_fixtures(foo, bar):
    assert foo.some_option + bar.some_option == 10


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
def test_parametrized_nesting(request, foo):
    assert foo.some_option == 0x420
    assert foo.another_option in (5, 6)


@pytest.mark.parametrize(
    'foo.*',
    [
        dict(some_option=0x420),
    ]
)
def test_indirect(request, foo):
    assert foo.some_option == 0x420


@pytest.mark.parametrize(
    ('foo.some_option', 'qux', 'bar.another_option'),
    [
        (0x420, 'qux', 5),
    ]
)
def test_parametrized_mixed(foo, bar, qux):
    assert foo.some_option == 0x420
    assert bar.another_option == 5
    assert qux == 'qux'

@pytest.mark.foo(some_option=24, another_option='five')
def test_shortcut(foo, bar):
    assert foo.some_option == 24
    assert foo.another_option == 'five'

    assert bar.some_option is True
    assert bar.another_option is False


@pytest.mark.parametrize('foo.some_option', [3])
@pytest.mark.parametrize('foo.some_option', [1])
@pytest.mark.parametrize('foo.some_option', [2])
def test_closest(foo):
    assert foo.some_option == 2


@pytest.mark.foo(some_option=3)
@pytest.mark.foo(some_option=1)
@pytest.mark.foo(some_option=2)
def test_closest_shortcut(foo):
    assert foo.some_option == 2
