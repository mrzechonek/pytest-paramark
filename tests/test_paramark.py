from namedlist import namedlist
import pytest


@pytest.fixture
def foo(paramark):
    Foo = namedlist('Foo', (
        ('some_option', 42),
        ('another_option', 'test'),
    ))

    return Foo(**paramark)


@pytest.fixture
def bar(paramark):
    Bar = namedlist('Bar', (
        ('some_option', True),
        ('another_option', False),
    ))

    return Bar(**paramark)


def test_default(foo, bar):
    assert foo.some_option == 42
    assert foo.another_option == 'test'

    assert bar.some_option is True
    assert bar.another_option is False


@pytest.mark.foo(some_option=24, another_option='five')
def test_custom(foo, bar):
    assert foo.some_option == 24
    assert foo.another_option == 'five'

    assert bar.some_option is True
    assert bar.another_option is False


@pytest.mark.parametrize(
    'foo.some_option, bar.some_option',
    [
        pytest.param(24, 5),
    ]
)
def test_parametrized(foo, bar):
    assert foo.some_option == 24
    assert bar.some_option == 5


@pytest.mark.parametrize('foo.some_option', [
    pytest.param(0x420),
])
@pytest.mark.parametrize('foo.another_option', [
    pytest.param(5),
    pytest.param(6),
])
def test_parametrized_nesting(request, foo):
    assert foo.some_option == 0x420
    assert foo.another_option in (5, 6)


@pytest.mark.parametrize('foo.*', [
    pytest.param(dict(some_option=0x420)),
])
def test_parametrized_kwargs(request, foo):
    assert foo.some_option == 0x420


@pytest.mark.parametrize(
    'foo.some_option, qux, bar.another_option',
    [
        pytest.param(0x420, 'qux', 5),
    ]
)
def test_parametrized_mixed(foo, bar, qux):
    assert foo.some_option == 0x420
    assert bar.another_option == 5
    assert qux == 'qux'


@pytest.mark.foo(some_option=3)
@pytest.mark.foo(some_option=1)
@pytest.mark.foo(some_option=2)
def test_paramark_closest(foo):
    assert foo.some_option == 2
