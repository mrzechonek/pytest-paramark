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

This means that when you want to parametrize fixtures, each parameter name must
be unique:

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

This is inconvenient when number of options and fixtures increases, and you end
up with lots of boilerplate code like this:

.. code-block:: python

   @pytest.fixture()
   def app_elements():
      {}


   @pytest.fixture()
   def app_sequence():
      return None


   @pytest.fixture()
   def app_uuid(uuid=None):
      return uuid or uuid4()


   @pytest.fixture
   def app_app_key():
      return ApplicationKey(bytes.fromhex('63964771734fbd76e3b40519d1d94a48'))


   @pytest.fixture
   def app_net_key():
      return NetworkKey(bytes.fromhex('7dd7364cd842ad18c17c2b820c84c3d6'))


   @pytest.fixture
   def app_dev_key():
      return DeviceKey(bytes.fromhex('9d6dd0e96eb25dc19a40ed9914f8f03f'))


   @pytest.fixture
   def app_addr():
      return 0x5f2


   @pytest.fixture
   def app_iv_index():
      return 0


   @pytest.fixture()
   def application(app_uuid, app_elements, app_dev_key, app_app_key, app_net_ket,
                   app_addr, app_iv_index, app_sequence):
      ...


The solution
============

This plugin provides a cleaner way to pass such options to selected fixutres,
by implementing a magic fixture called ``paramark``, which returns a *different* value
for each of the fixtures that depend on it:

.. code-block:: python

   @pytest.fixture
   def foo(paramark):
      return paramark


   @pytest.fixture
   def bar(paramark):
      return paramark


   @pytest.mark.foo(option=42)
   @pytest.mark.bar(option=24)
   def test_options(foo, bar):
      assert foo['option'] == 42
      assert bar['option'] == 24

As can be seen in the example, ``paramark`` returns a dictionary with keys and
values pulled from a custom mark with *the same name* as the dependant fixture.
Note that these marks still need to be `registered`_.

This also works with ``parametrize``, by extending the argument name syntax to include a dot:

.. code-block:: python

   @pytest.mark.parametrize(
      'foo.option, bar.option',
      [
         (43, 24),
      ]
   )
   @pytest.mark.bar(option=24)
   def test_options(foo, bar):
      assert foo['option'] == 42
      assert bar['option'] == 24

or, if you want to parametrize the whole dictionary:

.. code-block:: python

   @pytest.mark.parametrize(
      'foo.*, bar.option',
      [
         ({'option': 42, 'another: 17}, 24),
      ]
   )
   @pytest.mark.bar(option=24)
   def test_options(foo, bar):
      assert foo['option'] == 42
      assert foo['another'] == 17
      assert bar['option'] == 24

Having this, defining default values no longer requires separate fixture for each option:

.. code-block:: python

   @pytest.fixture
   def foo(paramark):
      default = {'option': 'default_foo_option'}
      return {**default, **paramark)


   @pytest.fixture
   def bar(paramark):
      default = {'option': 'default_bar_option'}
      return {**default, **paramark)


   @pytest.mark.foo(option='custom_foo_option')
   def test_options(foo, bar):
      assert foo['option'] == 'custom_foo_option'
      assert bar['option'] == 'default_bar_option'

or, if you want to be safer and fancier:

.. code-block:: python

   import typing


   @pytest.fixture
   def foo(paramark):
      class Foo(typing.NamedTuple):
         option: str = 'default_foo_option'

      return Foo(**paramark)


   def test_options(foo):
      assert foo.option == 'default_foo_option'


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
