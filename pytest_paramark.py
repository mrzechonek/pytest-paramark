import sys
from collections import defaultdict

from _pytest import fixtures, python
from _pytest.mark import Mark, ParameterSet
from _pytest.mark.structures import normalize_mark_list

import pytest


def parametrize_indirect(metafunc, mark):
    # Transform this:
    #
    #     @pytest.mark.parametrize(
    #         ('foo.some_option', 'bar.some_option'),
    #         [
    #             pytest.param(5, 5),
    #             pytest.param(3, 7),
    #         ]
    #     )
    #
    # into this:
    #
    #     @pytest.mark.parametrize(
    #         ('foo, bar'),
    #         [
    #             (dict(some_option=5), dict(some_option=5)),
    #             (dict(some_option=3), dict(some_option=7)),
    #         ]
    #         indirect=['foo', 'bar']
    #     )

    if mark.name != "parametrize":
        return

    argnames, params = ParameterSet._for_parametrize(
        mark.args[0],
        mark.args[1],
        func=metafunc.function,
        config=metafunc.config,
        function_definition=metafunc.definition,
    )

    aggregates = []
    args = {}

    for name in argnames:
        try:
            name, suffix = name.split(".", 1)
        except ValueError:
            args[name] = False

            def aggregate(values, val, name=name):
                values.setdefault(name, val)
        else:
            args[name] = True

            def aggregate(values, val, name=name, suffix=suffix):
                if suffix == '*':
                    values[name].update(val)
                else:
                    values[name].setdefault(suffix, val)

        aggregates.append(aggregate)

    indirect = [name for name, indirect in args.items() if indirect]

    def aggregate(param):
        values = defaultdict(dict)

        for aggregate, value in zip(aggregates, param.values):
            aggregate(values, value)

        # TODO: move to own_markers instead of marking each ParameterSet
        return ParameterSet(
            values.values(),
            marks=[pytest.mark.nest_indirect(*indirect)] + list(param.marks),
            id=param.id,
        )

    mark_indirect = mark.kwargs.setdefault("indirect", [])

    if mark_indirect is not True:
        mark.kwargs["indirect"] = sorted(
            list(set(mark_indirect + indirect))
        )  # remove duplicates

    return Mark(
        name=mark.name,
        args=(tuple(args.keys()), [aggregate(param) for param in params]),
        kwargs=mark.kwargs,
    )


def pytest_configure(config):
    # Monkeypatch pytest to support multiple parametrize() marks with the same
    # argument name.
    #
    # This is needed to support nesting:
    #
    #     @pytest.mark.parametrize('foo.some_option', [1])
    #     @pytest.mark.parametrize('foo.another_option', [2])
    #     def test_nesting(request, foo):
    #         assert foo.some_option == 1
    #         assert foo.another_option == 2
    _setmulti2 = python.CallSpec2.setmulti2

    def setmulti2(self, valtypes, argnames, valset, id, marks, scopenum, param_index):
        try:
            nest_mark = next(m for m in marks if m.name == "nest_indirect")
        except StopIteration:
            return _setmulti2(
                self, valtypes, argnames, valset, id, marks, scopenum, param_index
            )

        for arg, val in zip(argnames, valset):
            valtype_for_arg = valtypes[arg]

            if arg in nest_mark.args:
                # merge request.param dictionaries instead of overwriting the
                # value
                val.update(getattr(self, valtype_for_arg).get(arg, {}))
            else:
                self._checkargnotcontained(arg)

            getattr(self, valtype_for_arg)[arg] = val
            self.indices[arg] = param_index
            self._arg2scopenum[arg] = scopenum
        self._idlist.append(id)
        self.marks.extend(normalize_mark_list(marks))

    python.CallSpec2.setmulti2 = setmulti2

    # Monkeypatch pytest to add fixture(indirect=) argument
    #
    # This is needed to provide empty defaults in request.params when
    # test function is not explicitly parametrized
    _fixture = pytest.fixture

    def fixture(*args, indirect=False, **kwargs):
        decorator = _fixture(*args, **kwargs)

        if isinstance(decorator, fixtures.FixtureFunctionMarker):
            def decorate(function):
                function.__indirect__ = indirect
                return decorator(function)

            return decorate

        return decorator

    pytest.fixture = fixture

    # register marker for nesting
    config.addinivalue_line(
        "markers", "nest_indirect",
    )

def pytest_fixture_setup(fixturedef, request):
    if hasattr(fixturedef.func, "__indirect__") and not hasattr(request, "param"):
        request.param = {}


def pytest_generate_tests(metafunc):
    shortcut_markers = []

    for mark in metafunc.definition.own_markers:
        if mark.name in metafunc.definition.fixturenames:
            shortcut_markers.append(Mark(name='parametrize', args=[('%s.*' % mark.name,), [(mark.kwargs,)]], kwargs={}))

    metafunc.definition.own_markers = [
        parametrize_indirect(metafunc, mark) for mark in metafunc.definition.own_markers + shortcut_markers
    ]
