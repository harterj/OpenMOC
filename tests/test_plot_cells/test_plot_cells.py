#!/usr/bin/env python

import os
import sys
sys.path.insert(0, os.pardir)
sys.path.insert(0, os.path.join(os.pardir, 'openmoc'))
from testing_harness import PlottingTestHarness
from input_set import SimpleLatticeInput
from openmoc.plotter import plot_cells


class PlotCellsTestHarness(PlottingTestHarness):
    """Test cell plotting with a 4x4 lattice."""

    def __init__(self):
        super(PlotCellsTestHarness, self).__init__()
        self.input_set = SimpleLatticeInput()

    def _run_openmoc(self):
        """Plot the cells in the geometry."""

        # Create a series of Matplotlib Figures / PIL Images for different
        # plotting parameters and append to figures list
        self.figures.append(
            plot_cells(self.input_set.geometry, gridsize=100, 
                       get_figure=True))
        self.figures.append(
            plot_cells(self.input_set.geometry, gridsize=100, 
                       zcoord=10., get_figure=True))
        self.figures.append(
            plot_cells(self.input_set.geometry, gridsize=100, 
                       get_figure=True, xlim=(0., 2.), ylim=(0., 2.)))
        self.figures.append(
            plot_cells(self.input_set.geometry, gridsize=100, 
                       get_figure=True, library='pil'))


if __name__ == '__main__':
    harness = PlotCellsTestHarness()
    harness.main()
