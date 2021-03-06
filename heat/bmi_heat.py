#! /usr/bin/env python
import types
import numpy as np

from bmi import Bmi, BmiGridType
from .heat import Heat


class BmiHeat(Bmi):
    _name = 'The 2D Heat Equation'
    _input_var_names = ['plate_surface__temperature']
    _output_var_names = ['plate_surface__temperature']
    _var_units = {'plate_surface__temperature': 'K'}

    def __init__(self):
        self._model = None
        self._values = {}

    def initialize(self, config_file=None):
        if config_file is None:
            self._model = Heat()
        elif isinstance(config_file, types.StringTypes):
            with open(config_file, 'r') as fp:
                self._model = Heat.from_file_like(fp.read())
        else:
            self._model = Heat.from_file_like(config_file)

        self._values = {
            'plate_surface__temperature': self._model.z,
        }

    def update(self):
        self._model.advance_in_time()

    def update_frac(self, time_frac):
        dt = self.get_time_step()
        self._model.dt = time_frac * dt
        self.update()
        self._model.dt = dt

    def update_until(self, then):
        n_steps = (then - self.get_current_time()) / self.get_time_step()

        for _ in xrange(int(n_steps)):
            self.update()
        self.update_frac(n_steps - int(n_steps))

    def finalize(self):
        self._model = None

    def get_var_type (self, var_name):
        return str(self.get_value_ptr(var_name).dtype)

    def get_var_units(self, var_name):
        return self._var_units[var_name]

    def get_var_rank(self, var_name):
        return self.get_value_ptr(var_name).ndim

    def get_var_size(self, var_name):
        return self.get_value_ptr(var_name).size

    def get_var_nbytes(self, var_name):
        return self.get_value_ptr(var_name).nbytes

    def get_value_ptr(self, var_name):
        return self._values[var_name]

    def get_value(self, var_name):
        return self.get_value_ptr(var_name).copy()

    def get_value_at_indices(self, var_name, indices):
        return self.get_value_ptr(var_name).take(indices)

    def set_value(self, var_name, src):
        val = self.get_value_ptr(var_name)
        val[:] = src

    def set_value_at_indices(self, var_name, src, indices):
        val = self.get_value_ptr(var_name)
        val.flat[indices] = src

    def get_component_name(self):
        return self._name

    def get_input_var_names(self):
        return self._input_var_names

    def get_output_var_names(self):
        return self._output_var_names

    def get_grid_shape (self, var_name):
        return self.get_value_ptr(var_name).shape

    def get_grid_spacing(self, var_name):
        if var_name in self._values:
            return self._model.spacing

    def get_grid_origin(self, var_name):
        if var_name in self._values:
            return self._model.origin

    def get_grid_type(self, var_name):
        if var_name in self._values:
            return BmiGridType.UNIFORM
        else:
            return BmiGridType.UNKNOWN

    def get_start_time (self):
        return 0.

    def get_end_time (self):
        return np.finfo('d').max

    def get_current_time (self):
        return self._model.time

    def get_time_step (self):
        return self._model.dt
