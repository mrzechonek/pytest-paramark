import sys
from copy import deepcopy
from collections import defaultdict
import functools

import pytest
from _pytest import fixtures, python
from _pytest.mark import Mark, MarkDecorator, ParameterSet
from _pytest.mark.structures import normalize_mark_list
from typing import Iterable, Union, Mapping


def collapse_indirect(metafunc, mark):
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
        return mark

    _argnames, params = ParameterSet._for_parametrize(
        argnames=mark.args[0],
        argvalues=mark.args[1],
        func=metafunc.function,
        config=metafunc.config,
        nodeid=metafunc.definition.nodeid,
    )

    argnames = []
    aggregates = []

    for name in _argnames:
        try:
            name, suffix = name.split(".", 1)
        except ValueError:
            def aggregate(values, val, name=name):
                values.setdefault(name, val)

        else:
            def aggregate(values, val, name=name, suffix=suffix):
                values[name].setdefault(suffix, val)
        finally:
            argnames.append(name)

        aggregates.append(aggregate)


    def aggregate(param):
        values = defaultdict(dict)

        for aggregate, value in zip(aggregates, param.values):
            aggregate(values, value)

        return ParameterSet(
            values=values.values(),
            marks=param.marks,
            id=param.id,
        )

    return pytest.mark.parametrize(
        argnames,
        [aggregate(param) for param in params],
        **mark.kwargs,
    ).mark


def is_indirect_fixture(metafunc, argname):
    try:
        fixturedefs = metafunc.fixtureinfo.name2fixturedefs[argname]
    except KeyError:
        return False
    else:
        return any(f.indirect for f in fixturedefs)



def parametrize_shortcut(metafunc, mark):
    if is_indirect_fixture(metafunc, mark.name):
        return pytest.mark.parametrize(
            mark.name,
            [mark.kwargs]
        ).mark
    else:
        return mark


def pytest_generate_tests(metafunc):
    metafunc.definition.own_markers = [
        parametrize_shortcut(metafunc, mark)
        for mark in metafunc.definition.iter_markers()
    ]

    metafunc.definition.own_markers = [
        collapse_indirect(metafunc, mark)
        for mark in metafunc.definition.own_markers
    ]

    # FIXME: after collapsing remove parametrizations of indirect fixtures from parents
    metafunc.definition.parent = None

    own_markers = []
    indirect_params = defaultdict(dict)

    # HERE BE DRAGONS
    has_direct = set()

    for mark in metafunc.definition.own_markers:
        indirect_params2 = deepcopy(indirect_params)

        if mark.name != 'parametrize':
            own_markers.append(mark)
            continue

        indirect_argnames = {
            name: index
            for index, name in enumerate(mark.args[0])
            if is_indirect_fixture(metafunc, name)
        }

        indirect_argindexes = {
            index: name
            for index, name in enumerate(mark.args[0])
            if is_indirect_fixture(metafunc, name)
        }

        direct_argnames = [
            name
            for name in mark.args[0]
            if not name in indirect_argnames
        ]

        params = []

        for param in mark.args[1]:
            for index, value in enumerate(param.values):
                try:
                    argname = indirect_argindexes[index]
                except KeyError:
                    pass
                else:
                    indirect_params2[argname].update(value)

            params.append(
                ParameterSet(
                    values=
                        [value for index, value in enumerate(param.values) if not index in indirect_argindexes] +
                        [deepcopy(i) for i in indirect_params2.values()],
                    marks=param.marks,
                    id=param.id,
                )
            )

        for k, v in indirect_params2.items():
            indirect_params[k] = {**v, **indirect_params[k]}

        if direct_argnames:
            own_markers.append(
                pytest.mark.parametrize(
                    [*direct_argnames, *indirect_params.keys()],
                    params,
                    **mark.kwargs,
                ).mark
            )

            has_direct.update({*direct_argnames, *indirect_params.keys()})


    own_markers.append(
        pytest.mark.parametrize(
            list(k for k,v in indirect_params.items() if k not in has_direct),
            [
                ParameterSet(
                    values=list(v for k,v in indirect_params.items() if k not in has_direct),
                    marks=[],
                    id=None,
                )
            ]
        ).mark
    )

    metafunc.definition.own_markers = own_markers
    print(metafunc.function.__name__, metafunc.definition.own_markers)

    # if user provided parameters for indirect fixtures, strip the defaults from callspec params
    parametrized = set()

    for mark in metafunc.definition.own_markers:
        if mark.name != "parametrize":
            continue

        parametrized.update(
            arg for arg in mark.args[0]
            if is_indirect_fixture(metafunc, arg)
        )

    for callspec in metafunc._calls:
        for p in parametrized:
            callspec.params.pop(p, None)
