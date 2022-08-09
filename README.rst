===============
pytest-paramark
===============

.. image:: https://img.shields.io/pypi/v/pytest-paramark.svg
    :target: https://pypi.org/project/pytest-paramark
    :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/pytest-paramark.svg
    :target: https://pypi.org/project/pytest-paramark
    :alt: Python versions

.. image:: https://travis-ci.org/mrzechonek/pytest-paramark.svg?branch=master
    :target: https://travis-ci.org/mrzechonek/pytest-paramark
    :alt: See Build Status on Travis CI

Configure pytest fixtures using combination of parametrize and markers

----


What is this thing?
-------------------

The problem
===========

Pytest fixture names must be unique within the whole dependency graph
(`#3966`_).

This means that when you want to parametrize fixtures, each argument name must
be unique, and you have to remember which fixture uses which argument (or
introduce some kind of convention):

.. code-block:: python

    import pytest

    @pytest.fixture
    def foo(foo_option):
        return {'option': foo_option}


    @pytest.fixture
    def bar(bar_option):
        return {'option': bar_option}


    @pytest.mark.parametrize(
        'foo_option, bar_option',
        [
            (42, 24),
        ]
    )
    def test_options(foo, bar):
        assert foo['option'] == 42
        assert bar['option'] == 24

Also, if you want to provide default vaules for options, they need to be fixtures as well:

.. code-block:: python

    @pytest.fixture
    def foo_option():
        return 'default_foo_option'


    @pytest.fixture
    def bar_option():
        return 'default_bar_option'


    @pytest.fixture
    def foo(foo_option):
        return {'option': foo_option}


    @pytest.fixture
    def bar(bar_option):
        return {'option': bar_option}


    def test_options(foo, bar):
        assert foo['option'] == 'default_foo_option'
        assert bar['option'] == 'default_bar_option'

In some cases, indirect parametrization helps, but the usage is rather verbose,
requires adding ``indirect`` specifiers to all tests, and is a bit inconvenient
when you want to specify defaults:

.. code-block:: python

    @pytest.fixture
    def foo(request):
        default = {'option': 'default_foo_option'}
        return {**defaults, **getattr(request, 'param', {})}


    @pytest.fixture
    def bar(request):
        default = {'option': 'default_bar_option'}
        return {**defaults, **getattr(request, 'param', {})}


    @pytest.mark.parametrize('foo', [dict(option='custom_foo_option')], indirect=['foo'])
    def test_options(foo, bar):
        assert foo['option'] == 'custom_foo_option'
        assert bar['option'] == 'default_bar_option'


The solution
============

This plugin automagically adds indirect parametrization to tests using selected
fixtures, then allows specifying individual parametrization arguments, and
nesting them:

.. code-block:: python

    @pytest.fixture(indirect=True)  #  HERE
    def foo(request):
        return request.param


    @pytest.mark.parametrize('foo.first', [1])  # AND HERE
    @pytest.mark.parametrize('foo.second', [2])
    def test_options(foo):
        assert foo['first'] == 1
        assert bar['second'] == 2


    # shorthand syntax
    @pytest.mark.foo(first=1)
    @pytest.mark.bar(second=2)
    def test_options(foo):
        assert foo['first'] == 1
        assert bar['second'] == 2


    # all fixture params
    @pytest.mark.parametrize('foo', [dict(first=1, second=2)])
    def test_options(foo):
        assert foo['first'] == 1
        assert bar['second'] == 2

As can be seen in the example, ``request.param`` returns a dictionary with keys
pulled from ``parametrize``'s extended argument name syntax: ``'<fixture>.<key>'``.

.. note::
    For shorthand notation to work, marks still need to be `registered`_.

.. warning::
    Obviously, specifying fixture as ``indirect=True`` makes no sense when also
    passing ``params=...```.

Having this, you no longer need to mark tests with ``parametrize(indirect=...)``:

.. code-block:: python

   @pytest.fixture(indirect=True)
   def foo(request):
      default = {'option': 'default_foo_option'}
      return {**default, **request.param)


   @pytest.fixture(indirect=True)
   def bar(paramark):
      default = {'option': 'default_bar_option'}
      return {**default, **request.param)


   @pytest.mark.parametrize('foo.option', ['custom_foo_option'])
   def test_options(foo, bar):
      assert foo['option'] == 'custom_foo_option'
      assert bar['option'] == 'default_bar_option'

Also, you can group and nest such parametrizations:

.. code-block:: python

    @pytest.mark.foo(option=True)
    class TestGroup:
        def test_default(self, foo):
            assert foo['option']

        @pytest.mark.foo(option=False)
        def test_override(self, foo):
            assert not foo['option']


or, if you want to be safer and fancier:

.. code-block:: python

   import typing


   @pytest.fixture(indirect=True)
   def foo(request):
      class Foo(typing.NamedTuple):
         option: str = 'default_foo_option'

      return Foo(**request.param)


   @pytest.fixture(indirect=True)
   def bar(request):
      class Bar(typing.NamedTuple):
         option: str = 'default_bar_option'

      return Bar(**request.param)


   @pytest.mark.parametrize('foo.option', ['custom_foo_option'])
   def test_options(foo, bar):
      assert foo.option == 'custom_foo_option'
      assert bar.option == 'default_bar_option'


Installation
------------

You can install "pytest-paramark" via `pip`_ from `PyPI`_::

    $ pip install pytest-paramark


Contributing
------------
Contributions are very welcome. Tests can be run with `tox`_, please ensure
the coverage at least stays the same before you submit a pull request.


License
-------

Distributed under the terms of the `MIT`_ license, "pytest-paramark" is free and open source software


Issues
------

If you encounter any problems, please `file an issue`_ along with a detailed description.

.. _`MIT`: http://opensource.org/licenses/MIT
.. _`file an issue`: https://github.com/mrzechonek/pytest-paramark/issues
.. _`pytest`: https://github.com/pytest-dev/pytest
.. _`tox`: https://tox.readthedocs.io/en/latest/
.. _`pip`: https://pypi.org/project/pip/
.. _`PyPI`: https://pypi.org/project
.. _`#3966`: https://github.com/pytest-dev/pytest/issues/3966
.. _`registered`: http://doc.pytest.org/en/latest/example/markers.html#registering-markers
