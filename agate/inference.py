#!/usr/bin/env python

from copy import copy

try:
    from collections import OrderedDict
except ImportError: # pragma: no cover
    from ordereddict import OrderedDict

from agate.column_types import *
from agate.exceptions import *

class TypeTester(object):
    """
    Infer types for the columns in a given set of data.

    :param force: A dictionary where each key is a column name and each
        value is a :class:`.ColumnType` instance that overrides inference.
    """
    def __init__(self, force={}):
        self._force = force

        # In order of preference
        self._possible_types =[
            BooleanType(),
            NumberType(),
            TimeDeltaType(),
            DateTimeType(),
            TextType()
        ]

    def run(self, rows, column_names):
        """
        Apply inference to the provided data and return an array of
        :code:`(column_name, column_type)` tuples suitable as an argument to
        :class:`.Table`.

        :param rows: The data as a sequence of any sequences: tuples, lists,
            etc.
        :param column_names: A sequence of column names.
        """
        num_columns = len(column_names)
        hypotheses = [set(self._possible_types) for i in range(num_columns)]

        force_indices = [column_names.index(name) for name in self._force.keys()]

        for row in rows:
            for i in range(num_columns):
                if i in force_indices:
                    continue

                h = hypotheses[i]

                if len(h) == 1:
                    continue

                for column_type in copy(h):
                    if not column_type.test(row[i]):
                        h.remove(column_type)

        column_types = []

        for i in range(num_columns):
            if i in force_indices:
                column_types.append(self._force[column_names[i]])
                continue

            h = hypotheses[i]

            # Select in prefer order
            for t in self._possible_types:
                if t in h:
                    column_types.append(t)
                    break

        return zip(column_names, column_types)
