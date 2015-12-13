##
# @file plotter.py
# @package openmoc.plotter
# @brief The plotter module provides utility functions to plot data from
#        OpenMOCs C++ classes, in particular, the geomery, including Material,
#        Cells and flat source regions, and fluxes and pin powers.
# @author William Boyd (wboyd@mit.edu)
# @date March 10, 2013

import os
import sys
import numpy as np
import numpy.random
import matplotlib

# force headless backend, or set 'backend' to 'Agg'
# in your ~/.matplotlib/matplotlibrc
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cmx

import openmoc

# For Python 2.X.X
if (sys.version_info[0] == 2):
    from log import *
    from process import *
# For Python 3.X.X
else:
    from openmoc.log import *
    from openmoc.process import *

# Force non-interactive mode, or set 'interactive' to False
# in your ~/.matplotlib/matplotlibrc
plt.ioff()

## A static variable for the output directory in which to save plots
subdirectory = "/plots/"

TINY_MOVE = openmoc.TINY_MOVE


##
# @brief Plots the characteristic tracks from an OpenMOC simulation.
# @details This method requires that Tracks have been generated by a
#          TrackGenerator object. A user may invoke this function from
#          an OpenMOC Python file as follows:
#
# @code
#         openmoc.plotter.plot_tracks(track_generator)
# @endcode
#
# @param track_generator the TrackGenerator which has generated Tracks
def plot_tracks(track_generator):

    global subdirectory

    directory = openmoc.get_output_directory() + subdirectory

    # Make directory if it does not exist
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Error checking
    if 'TrackGenerator' not in str(type(track_generator)):
        py_printf('ERROR', 'Unable to plot Tracks since from %s rather ' +
                  'than a TrackGenerator', str(type(track_generator)))

    if not track_generator.containsTracks():
        py_printf('ERROR', 'Unable to plot Tracks since the track ' +
                  'generator has not yet generated tracks')

    py_printf('NORMAL', 'Plotting the tracks...')

    # Retrieve data from TrackGenerator
    vals_per_track = openmoc.NUM_VALUES_PER_RETRIEVED_TRACK
    num_azim = track_generator.getNumAzim()
    spacing = track_generator.getTrackSpacing()
    num_tracks = track_generator.getNumTracks()
    coords = track_generator.retrieveTrackCoords(num_tracks*vals_per_track)

    # Convert data to NumPy arrays
    coords = np.array(coords)
    x = coords[0::vals_per_track/2]
    y = coords[1::vals_per_track/2]

    # Make figure of line segments for each Track
    fig = plt.figure()
    for i in range(num_tracks):
        plt.plot([x[i*2], x[i*2+1]], [y[i*2], y[i*2+1]], 'b-')

    plt.xlim([x.min(), x.max()])
    plt.ylim([y.min(), y.max()])

    title = 'Tracks for {0} angles and {1} cm spacing'.format(num_azim, spacing)
    plt.title(title)

    filename = 'tracks-{1}-angles-{2}.png'.format(directory, num_azim, spacing)
    fig.savefig(directory+filename, bbox_inches='tight')
    plt.close(fig)


##
# @brief Plots the characteristic Track segments from an OpenMOC simulation.
# @details This method requires that tracks have been generated by a
#          TrackGenerator object. Each segment is colored by the ID of the
#          unique flat flat source region it is within. A user may invoke
#          this function from an OpenMOC Python file as follows:
#
# @code
#         openmoc.plotter.plot_segments(track_generator)
# @endcode
#
# @param track_generator the TrackGenerator which has generated Tracks
def plot_segments(track_generator):

    global subdirectory
    directory = openmoc.get_output_directory() + subdirectory

    # Make directory if it does not exist
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Error checking
    if 'TrackGenerator' not in str(type(track_generator)):
        py_printf('ERROR', 'Unable to plot Track segments from %s ' +
                  'rather than a TrackGenerator', str(type(track_generator)))

    if not track_generator.containsTracks():
        py_printf('ERROR', 'Unable to plot Track segments since the ' +
                  'TrackGenerator has not yet generated Tracks.')

    py_printf('NORMAL', 'Plotting the track segments...')

    # Retrieve data from TrackGenerator
    vals_per_segment = openmoc.NUM_VALUES_PER_RETRIEVED_SEGMENT
    num_azim = track_generator.getNumAzim()
    spacing = track_generator.getTrackSpacing()
    num_segments = track_generator.getNumSegments()
    num_fsrs = track_generator.getGeometry().getNumFSRs()
    coords = track_generator.retrieveSegmentCoords(num_segments*vals_per_segment)

    # Convert data to NumPy arrays
    coords = np.array(coords)
    x = np.zeros(num_segments*2)
    y = np.zeros(num_segments*2)
    z = np.zeros(num_segments*2)
    fsrs = np.zeros(num_segments)

    for i in range(num_segments):
        fsrs[i] = coords[i*vals_per_segment]
        x[i*2] = coords[i*vals_per_segment+1]
        y[i*2] = coords[i*vals_per_segment+2]
        z[i*2] = coords[i*vals_per_segment+3]
        x[i*2+1] = coords[i*vals_per_segment+4]
        y[i*2+1] = coords[i*vals_per_segment+5]
        z[i*2+1] = coords[i*vals_per_segment+6]

    # Create array of equally spaced randomized floats as a color map for plots
    # Seed the NumPy random number generator to ensure reproducible color maps
    numpy.random.seed(1)
    color_map = np.linspace(0., 1., num_fsrs, endpoint=False)
    numpy.random.shuffle(color_map)

    # Make figure of line segments for each track
    fig = plt.figure()

    # Create a color map corresponding to FSR IDs
    for i in range(num_segments):
        cNorm  = colors.Normalize(vmin=0, vmax=max(color_map))
        scalarMap = cmx.ScalarMappable(norm=cNorm)
        color = scalarMap.to_rgba(color_map[fsrs[i] % num_fsrs])
        plt.plot([x[i*2], x[i*2+1]], [y[i*2], y[i*2+1]], c=color)

    plt.xlim([x.min(), x.max()])
    plt.ylim([y.min(), y.max()])

    suptitle = 'Segments ({0} angles, {1} cm spacing)'.format(num_azim, spacing)
    title = 'z = {0}'.format(z[0])
    plt.suptitle(suptitle)
    plt.title(title)

    filename = 'segments-{0}-angles-{1}-spacing'.format(num_azim, spacing)
    filename = '{0}-z-{1}.png'.format(filename, z[0])
    fig.savefig(directory+filename, bbox_inches='tight')
    plt.close(fig)


##
# @brief This method takes in a Geometry object and plots a color-coded 2D
#        surface plot representing the Materials in the Geometry.
# @details The Geometry object must be initialized with Materials, Cells,
#          Universes and lattices before being passed into this method. A user
#          may invoke this function from an OpenMOC Python file as follows:
#
# @code
#         openmoc.plotter.plot_materials(geometry)
# @endcode
#
# @param geometry a geometry object which has been initialized with Materials,
#        Cells, Universes and Lattices
# @param gridsize an optional number of grid cells for the plot
# @param xlim optional list/tuple of the minimim/maximum x-coordinates
# @param ylim optional list/tuple of the minimim/maximum y-coordinates
# @param zcoord optional the z coordinate (default is 0.0)
def plot_materials(geometry, gridsize=250, xlim=None, ylim=None, zcoord=None):

    # Error checking
    if 'Geometry' not in str(type(geometry)):
        py_printf('ERROR', 'Unable to plot the Materials since input %s ' +
                  'is not a Geometry class object', str(geometry))

    # If zcoord was not set, set the zcoord to 0.0
    if zcoord is None:
        zcoord = 0.0

    # Check z-coord
    _check_zcoord(geometry, zcoord)

    py_printf('NORMAL', 'Plotting the materials...')

    # Create a NumPy array to map FSRs to Materials
    num_fsrs = geometry.getNumFSRs()
    fsrs_to_materials = np.zeros(num_fsrs, dtype=np.int64)
    for fsr_id in range(num_fsrs):
        cell = geometry.findCellContainingFSR(fsr_id)
        fsrs_to_materials[fsr_id] = cell.getFillMaterial().getId()

    # Create an array of random integer colors for each Material
    materials = geometry.getAllMaterials()
    num_materials = len(materials)
    material_ids = [material_id for material_id in materials]
    numpy.random.seed(1)
    numpy.random.shuffle(material_ids)
    for i, material_id in enumerate(fsrs_to_materials):
        fsrs_to_materials[i] = np.where(material_ids == material_id)[0]

    # Plot a 2D color map of the Materials
    suptitle = 'Materials'
    title = 'z = {0}'.format(zcoord)
    filename = 'materials-z-{0}.png'.format(zcoord)
    plot_spatial_data(geometry, fsrs_to_materials, False, False, zcoord,
                      gridsize, xlim, ylim, False, title, suptitle, filename,
                      'nearest', plt.get_cmap('spectral'), 0, num_materials)


##
# @brief This method takes in a Geometry object and plots a color-coded 2D
#        surface plot representing the Cells in the Geometry.
# @details The geometry object must be initialized with Materials, Cells,
#          Universes and Lattices before being passed into this method. A user
#          may invoke this function from an OpenMOC Python file as follows:
#
# @code
#         openmoc.plotter.plot_cells(geometry)
# @endcode
#
# @param geometry a Geometry object which has been initialized with Materials,
#        Cells, Universes and Lattices
# @param gridsize an optional number of grid cells for the plot
# @param xlim optional list/tuple of the minimim/maximum x-coordinates
# @param ylim optional list/tuple of the minimim/maximum y-coordinates
# @param zcoord optional the z coordinate (default is 0.0)
def plot_cells(geometry, gridsize=250, xlim=None, ylim=None, zcoord=None):

    # Error checking
    if 'Geometry' not in str(type(geometry)):
        py_printf('ERROR', 'Unable to plot the Cells since %s ' +
                  'input is not a Geometry class object', str(geometry))

    if zcoord is None:
        zcoord = 0.0

    # Check z-coord
    _check_zcoord(geometry, zcoord)

    py_printf('NORMAL', 'Plotting the cells...')

    # Create a NumPy array to map FSRs to Cells
    num_fsrs = geometry.getNumFSRs()
    fsrs_to_cells = np.zeros(num_fsrs, dtype=np.int64)
    for fsr_id in range(num_fsrs):
        cell = geometry.findCellContainingFSR(fsr_id)
        fsrs_to_cells[fsr_id] = cell.getId()

    # Create an array of random integer colors for each Cell
    material_cells = geometry.getAllMaterialCells()
    num_cells = len(material_cells)
    cell_ids = [cell_id for cell_id in material_cells]
    numpy.random.seed(1)
    numpy.random.shuffle(cell_ids)
    for i, cell_id in enumerate(fsrs_to_cells):
        fsrs_to_cells[i] = np.where(cell_ids == cell_id)[0]

    # Plot a 2D color map of the Cells
    suptitle = 'Cells'
    title = 'z = {0}'.format(zcoord)
    filename = 'cells-z-{0}.png'.format(zcoord)
    plot_spatial_data(geometry, fsrs_to_cells, False, False, zcoord, gridsize,
                      xlim, ylim, False, title, suptitle, filename,
                      'nearest', plt.get_cmap('spectral'), 0, num_cells)


#    plt.imshow(colors, extent=coords['bounds'],
#               interpolation='nearest', cmap=cmap, vmin=0, vmax=num_cells)


##
# @brief This method takes in a Geometry object and plots a color-coded 2D
#        surface plot representing the flat source regions in the Geometry.
#        The FSR centroids are plotted as black circles on top of the FSRs if
#        the centroids boolean is set to True.
# @details The Geometry object must be initialized with Materials, Cells,
#          Universes and Lattices before being passed into this method. A user
#          may invoke this function from an OpenMOC Python file as follows:
#
# @code
#         openmoc.plotter.plot_flat_source_regions(geometry)
# @endcode
#
# @param geometry a geometry object which has been initialized with Materials,
#        Cells, Universes and Lattices
# @param gridsize an optional number of grid cells for the plot
# @param xlim optional list/tuple of the minimim/maximum x-coordinates
# @param ylim optional list/tuple of the minimim/maximum y-coordinates
# @param centroids optional boolean to plot the FSR centroids
# @param marker_type optional string to set the centroids marker type
# @param marker_size optional int/float to set the centroids marker size
def plot_flat_source_regions(geometry, gridsize=250, xlim=None, ylim=None,
                             centroids=False, marker_type='o', marker_size=2):

    global subdirectory
    directory = openmoc.get_output_directory() + subdirectory

    # Error checking
    if 'Geometry' not in str(type(geometry)):
        py_printf('ERROR', 'Unable to plot the flat source regions since %s ' +
                  'input is not a Geometry class object', str(geometry))

    if not isinstance(centroids, bool):
        py_printf('ERROR', 'Unable to plot the flat source regions since ' +
                  'centroids is not a boolean')

    if not isinstance(marker_type, str):
        py_printf('ERROR', 'Unable to plot the flat source regions since ' +
                  'marker_type is a string')

    if marker_type not in matplotlib.markers.MarkerStyle().markers.keys():
        py_printf('ERROR', 'Unable to plot the flat source regions since ' +
                  'marker_type is not a valid marker (%d)', marker_type)

    if not is_float(marker_size) and not is_integer(marker_size):
        py_printf('ERROR', 'Unable to plot the flat source regions since ' +
                  'marker_size is not an int or float', marker_size)

    if marker_size <= 0:
        py_printf('ERROR', 'Unable to plot the flat source regions ' +
                  'with a negative marker_size (%d)', marker_size)

    if geometry.getNumFSRs() == 0:
        py_printf('ERROR', 'Unable to plot the flat source regions ' +
                  'since no tracks have been generated.')

    py_printf('NORMAL', 'Plotting the flat source regions...')

    # Get the Geometry's z-coord
    zcoord = geometry.getFSRPoint(0).getZ()

    num_fsrs = geometry.getNumFSRs()
    fsrs_to_fsrs = np.arange(num_fsrs, dtype=np.int64)
    fsrs_to_fsrs = _colorize(fsrs_to_fsrs, num_fsrs)

    # Plot a 2D color map of the flat source regions
    suptitle = 'Flat Source Regions'
    title = 'z = {0}'.format(zcoord)
    filename = 'flat-source-regions-z-{0}.png'.format(zcoord)
    fig = plot_spatial_data(geometry, fsrs_to_fsrs, False, False, zcoord,
                            gridsize, xlim, ylim, False, title, suptitle,
                            filename, 'nearest', plt.get_cmap('spectral'),
                            0, num_fsrs, True)

    # Plot centroids on top of 2D flat source region color map
    if centroids:
        centroids = np.zeros((num_fsrs, 2), dtype=np.float)
        for fsr_id in range(num_fsrs):
            point = geometry.getFSRCentroid(fsr_id)
            centroids[fsr_id,:] = [point.getX(), point.getY()]

        plt.scatter(centroids[:,0], centroids[:,1], color='k',
                    marker=marker_type, s=marker_size)

    # Set the plot title and save the figure
    fig.savefig(directory+filename, bbox_inches='tight')
    plt.close(fig)


##
# @brief This method takes in a Geometry and Cmfd object and plots a
#        color-coded 2D surface plot representing the CMFD cells in a geometry.
# @details The Geometry object must be initialized with Materials, Cells,
#          Universes and Lattices before being passed into this method.
#          Plotting the CMFD cells requires that segments must have been
#          created for the geometry and FSR IDs assigned to regions. A user
#          may invoke this function from an OpenMOC Python file as follows:
#
# @code
#         openmoc.plotter.plot_cmfd_cells(geometry, cmfd)
# @endcode
#
# @param geometry a geometry object which has been initialized with Materials,
#        Cells, Universes and Lattices. Segments must have been created or
#        extracted from a file.
# @param cmfd a Cmfd object which has been used with the geometry in
#        generating segments. The Cmfd object must have the _overlay_mesh
#        flag set to true; otherwise, the map linking FSR IDs to CMFD cells
#        would not have been created.
# @param gridsize an optional number of grid cells for the plot
# @param xlim optional list/tuple of the minimim/maximum x-coordinates
# @param ylim optional list/tuple of the minimim/maximum y-coordinates
def plot_cmfd_cells(geometry, cmfd, gridsize=250, xlim=None, ylim=None):

    # Error checking
    if 'Geometry' not in str(type(geometry)):
        py_printf('ERROR', 'Unable to plot the CMFD cells since %s ' +
                  'input is not a geometry class object', str(geometry))

    if 'Cmfd' not in str(type(cmfd)):
        py_printf('ERROR', 'Unable to plot the CMFD cells since %s ' +
                  'input is not a CMFD class object', str(cmfd))

    py_printf('NORMAL', 'Plotting the CMFD cells...')

    zcoord = geometry.getFSRPoint(0).getZ()
    num_fsrs = geometry.getNumFSRs()

    # Create a NumPy array to map FSRs to CMFD cells
    fsrs_to_cmfd_cells = np.zeros(num_fsrs, dtype=np.int64)
    for fsr_id in range(num_fsrs):
        fsrs_to_cmfd_cells[fsr_id] = cmfd.convertFSRIdToCmfdCell(fsr_id)

    # Assign random color scheme to CMFD cells
    num_cmfd_cells = cmfd.getNumCells()
    fsrs_to_cmfd_cells = _colorize(fsrs_to_cmfd_cells, num_cmfd_cells)

    # Plot the CMFD cells
    title = 'CMFD cells'
    filename = 'cmfd-cells.png'
    plot_spatial_data(geometry, fsrs_to_cmfd_cells, False, False, zcoord,
                      gridsize, xlim, ylim, False, title, None, filename)


##
# @brief This method takes in a Solver object and plots a color-coded 2D
#        surface plot representing the flat source region scalar fluxes.
# @details The Solver must have converged the flat source sources prior to
#          calling this routine. A user may invoke this function from an
#          OpenMOC Python file as follows:
#
# @code
#         openmoc.plotter.plot_spatial_fluxes(solver, energy_groups=[1,7])
# @endcode
#
# @param solver a Solver object that has converged the source for the Geometry
# @param energy_groups a Python list of integer energy groups to plot
# @param norm normalize the fluxes to the maximum flux
# @param gridsize an optional number of grid cells for the plot
# @param xlim optional list/tuple of the minimim/maximum x-coordinates
# @param ylim optional list/tuple of the minimim/maximum y-coordinates
def plot_spatial_fluxes(solver, energy_groups=[1], norm=False,
                        gridsize=250, xlim=None, ylim=None):

    if 'Solver' not in str(type(solver)):
        py_printf('ERROR', 'Unable to plot the FSR flux since the ' +
                  'input did not contain a solver class object')

    if not isinstance(energy_groups, (list, tuple, np.ndarray)):
        py_printf('ERROR', 'Unable to plot the FSR flux since the ' +
                  'energy_groups is not a Python tuple/list or NumPy array')

    py_printf('NORMAL', 'Plotting the FSR scalar fluxes...')

    geometry = solver.getGeometry()
    zcoord = geometry.getFSRPoint(0).getZ()

    # Get array of FSR energy-dependent fluxes
    fluxes = get_scalar_fluxes(solver)

    # Loop over all energy group and create a plot
    # Plot a 2D color map of the flat source regions
    for index, group in enumerate(energy_groups):
        suptitle = 'FSR Scalar Flux (Group {0})'.format(group)
        title = 'z = {0}'.format(zcoord)
        filename = 'fsr-flux-group-{0}-z-{1}.png'.format(group, zcoord)
        plot_spatial_data(geometry, fluxes[:,index], norm, False, zcoord,
                          gridsize, xlim, ylim, True, title, suptitle, filename)


##
# @brief This method takes in a Solver object and plots the scalar
#        flux vs. energy for one or more flat source regions.
# @details The Solver must have converged the flat source sources prior to
#          calling this routine. The routine will generate a step plot of the
#          flat flux across each energy group.
#
#          An optional parameter for the energy group bounds may be input.
#          The group bounds should be input in increasing order of energy.
#          If group bounds are not specified, the routine will use equal
#          width steps for each energy group.
#
#          A user may invoke this function from an OpenMOC Python file
#          as follows:
#
# @code
#         openmoc.plotter.plot_energy_fluxes(solver, fsrs=[1,5,20],
#                                            group_bounds=[0., 0.625, 2e7])
# @endcode
#
# @param solver a Solver object that has converged the source for the Geometry
# @param fsrs the flat source region IDs of interest
# @param group_bounds an optional Python list of the energy group bounds (eV)
# @param norm normalize the fluxes to the total energy-integrated flux
# @param loglog boolean indicating whether to plot use a log-log scale
def plot_energy_fluxes(solver, fsrs, group_bounds=None, norm=True, loglog=True):

    global subdirectory
    directory = openmoc.get_output_directory() + subdirectory

    # Make directory if it does not exist
    if not os.path.exists(directory):
        os.makedirs(directory)

    if 'Solver' not in str(type(solver)):
      py_printf('ERROR', 'Unable to plot the flux vs. energy ' +
                'since input did not contain a Solver class object')

    geometry = solver.getGeometry()
    num_fsrs = geometry.getNumFSRs()
    num_groups = geometry.getNumEnergyGroups()

    if isinstance(fsrs, (tuple, list, np.ndarray)):
        for fsr in fsrs:
            if not is_integer(fsr):
                py_printf('ERROR', 'Unable to plot the flux vs. energy ' +
                          'non-integer FSR %s', str(fsr))

            elif fsr < 0:
                py_printf('ERROR', 'Unable to plot the flux vs. energy ' +
                          'for negative FSR %d', fsr)

            elif fsr >= num_fsrs:
                py_printf('ERROR', 'Unable to plot the flux vs. energy ' +
                          'for FSR %d in problem with %d FSRs', fsr, num_fsrs)

    else:
        py_printf('ERROR', 'Unable to plot the flux vs. energy since ' +
                  'the fsrs is not a Python tuple, list or NumPy array')

    if isinstance(group_bounds, (tuple, list, np.ndarray)):

        if not all(low < up for low, up in zip(group_bounds, group_bounds[1:])):
            py_printf('ERROR', 'Unable to plot the flux vs. energy since ' +
                      'the group bounds are not monotonically increasing')

        elif len(group_bounds) != geometry.getNumEnergyGroups()+1:
            py_printf('ERROR', 'Unable to plot the flux vs. energy with ' +
                      '%d group bounds', len(group_bounds))

        for bound in group_bounds:
            if not is_integer(bound) and not is_float(bound):
                py_printf('ERROR', 'Unable to plot the flux vs. energy ' +
                          'with group bound %s', str(fsr))

            elif bound < 0:
                py_printf('ERROR', 'Unable to plot the flux vs. energy ' +
                          'with a negative group bound %f', bound)

    elif group_bounds is None:
        group_bounds = np.arange(num_groups+1, dtype=np.int)
        loglog = False

    else:
        py_printf('ERROR', 'Unable to plot the flux vs. energy since ' +
                  'the group bounds is not a Python tuple, list or NumPy array')

    py_printf('NORMAL', 'Plotting the scalar fluxes vs. energy...')

    # Compute difference in energy bounds for each group
    group_deltas = np.ediff1d(group_bounds)
    group_bounds = np.flipud(group_bounds)
    group_deltas = np.flipud(group_deltas)

    # Iterate over all flat source regions
    for fsr in fsrs:

        # Allocate memory for an array of this FSR's fluxes
        fluxes = np.zeros(num_groups, dtype=np.float)

        # Extract the flux in each energy group
        for group in range(num_groups):
            fluxes[group] = solver.getFlux(fsr, group+1)

        # Normalize fluxes to the total integrated flux
        if norm:
            fluxes /= np.sum(group_deltas * fluxes)

        # Initialize a separate plot for this FSR's fluxes
        fig = plt.figure()

        # Draw horizontal/vertical lines on the plot for each energy group
        for group in range(num_groups):

            # Horizontal line
            if loglog:
                plt.loglog(group_bounds[group:group+2], [fluxes[group]]*2,
                           linewidth=3, c='b', label='openmoc', linestyle='-')
            else:
                plt.plot(group_bounds[group:group+2], [fluxes[group]]*2,
                         linewidth=3, c='b', label='openmoc', linestyle='-')

            # Vertical lines
            if group < num_groups - 1:
                if loglog:
                    plt.loglog([group_bounds[group+1]]*2, fluxes[group:group+2],
                               c='b', linestyle='--')
                else:
                    plt.plot([group_bounds[group+1]]*2, fluxes[group:group+2],
                             c='b', linestyle='--')

        plt.xlabel('Energy')
        plt.ylabel('Flux')
        plt.xlim((min(group_bounds), max(group_bounds)))
        plt.grid()
        plt.title('FSR {0} Flux ({1} groups)'.format(fsr, num_groups))
        filename = 'flux-fsr-{0}.png'.format(fsr)
        plt.savefig(directory+filename, bbox_inches='tight')
        plt.close(fig)


##
# @brief This method plots a color-coded 2D surface plot representing the
#        FSR fission rates in the Geometry.
# @details The Solver must have converged the flat source sources prior to
#          calling this routine. A user may invoke this function from an
#          OpenMOC Python file as follows:
#
# @code
#         openmoc.plotter.plot_fission_rates(solver)
# @endcode
#
# @param solver a Solver object that has converged the source for the Geometry
# @param norm normalize the fission rates to the maximum fission rate
# @param transparent_zeros make regions without fission transparent
# @param gridsize an optional number of grid cells for the plot
# @param xlim optional list/tuple of the minimim/maximum x-coordinates
# @param ylim optional list/tuple of the minimim/maximum y-coordinates
def plot_fission_rates(solver, norm=False, transparent_zeros=True,
                       gridsize=250, xlim=None, ylim=None):

    if 'Solver' not in str(type(solver)):
        py_printf('ERROR', 'Unable to plot the fission rates ' +
                  'since input did not contain a solver class object')

    py_printf('NORMAL', 'Plotting the flat source region fission rates...')

    # Compute the volume-weighted fission rates for each FSR
    geometry = solver.getGeometry()
    fission_rates = solver.computeFSRFissionRates(geometry.getNumFSRs())
    zcoord = geometry.getFSRPoint(0).getZ()

    # Plot the fission rates
    suptitle = 'Flat Source Region Fission Rates'
    title = 'z = {0}'.format(zcoord)
    filename = 'fission-rates-z-{0}.png'.format(zcoord)
    plot_spatial_data(geometry, fission_rates, norm, transparent_zeros, zcoord,
                      gridsize, xlim, ylim, True, title, suptitle, filename)


##
# @brief This method plots a color-coded 2D surface plot representing the
#        FSR scalar fluxes for various eigenmodes from an IRAMSolver.
# @details The IRAMSolver must have computed the eigenmodes prior to
#          calling this routine. A user may invoke this function from
#          an OpenMOC Python file as follows:
#
# @code
#         openmoc.plotter.plot_eigenmode_fluxes(iramsolver, energy_groups=[1,7])
# @endcode
#
# @param iramsolver an IRAMSolver object that has computed the eigenmodes
# @param eigenmodes a Python list of integer eigenmodes to plot
# @param energy_groups a Python list of integer energy groups to plot
# @param norm normalize the fluxes to the maximum flux
# @param gridsize an optional number of grid cells for the plot
# @param xlim optional list/tuple of the minimim/maximum x-coordinates
# @param ylim optional list/tuple of the minimim/maximum y-coordinates
def plot_eigenmode_fluxes(iramsolver, eigenmodes=[], norm=False,
                          energy_groups=[1], gridsize=250, xlim=None, ylim=None):

    global subdirectory
    directory = openmoc.get_output_directory() + subdirectory

    # Make directory if it does not exist
    if not os.path.exists(directory):
        os.makedirs(directory)

    if 'IRAMSolver' not in str(type(iramsolver)):
      py_printf('ERROR', 'Unable to plot the eigenmode fluxes ' +
                'since input did not contain an IRAMSolver class object')

    # Get the total number of eigenmodes
    num_modes = iramsolver._num_modes

    if isinstance(eigenmodes, (list, tuple, np.ndarray)):

        # If eigenmodes parameters is empty list, plot all eigenmodes
        if len(eigenmodes) == 0:
          eigenmodes = np.arange(1, num_modes+1)

        for mode in eigenmodes:
            if not is_integer(mode):
                py_printf('ERROR', 'Unable to plot the eigenmode flux ' +
                          'for eigenmode %s', str(mode))

            elif mode <= 0:
                py_printf('ERROR', 'Unable to plot the eigenmode flux ' +
                          'for negative eigenmode %d', mode)

            elif mode > num_modes:
                py_printf('ERROR', 'Unable to plot the eigenmode flux for ' +
                          'eigenmode %d out of %d modes', mode, num_modes)

    else:
        py_printf('ERROR', 'Unable to plot the eigenmode flux since the ' +
                  'eigenmodes is not a Python tuple/list or NumPy array')

    py_printf('NORMAL', 'Plotting the eigenmode fluxes...')

    # Extract the MOC Solver from the IRAMSolver
    moc_solver = iramsolver._moc_solver

    # Loop over each eigenmode
    for mode in eigenmodes:

        # Extract the eigenvector for this eigenmode from the IRAMSolver
        eigenvec = iramsolver._eigenvectors[:,mode-1]

        # Convert it into a form that SWIG will be happy with
        eigenvec = np.squeeze(np.ascontiguousarray(eigenvec))
        eigenvec = np.real(eigenvec).astype(iramsolver._precision)

        # Ensure the primary eigenvector is positive
        if mode == 1:
            eigenvec = np.abs(eigenvec)

        # Insert eigenvector into MOC Solver object
        moc_solver.setFluxes(eigenvec)

        # Set subdirectory folder for this eigenmode
        num_digits = len(str(max(eigenmodes)))
        subdirectory = '/plots/eig-{0}-flux/'.format(str(mode).zfill(num_digits))

        # Plot this eigenmode's spatial fluxes
        plot_spatial_fluxes(moc_solver, energy_groups, norm, gridsize, xlim, ylim)

    # Reset global subdirectory
    subdirectory = '/plots/'


##
# @brief This is a helper method to define coordinates for a plotting window.
# @details This routine builds a coordinate surface map for the plotting
#          window defined for by the user. If no window was defined, then
#          this routine uses the outer bounding box around the geometry as
#          the plotting window.
# @param geometry a Geometry object which has been initialized with Materials,
#        Cells, Universes and Lattices
# @param gridsize an optional number of grid cells for the plot
# @param xlim optional list/tuple of the minimim/maximum x-coordinates
# @param ylim optional list/tuple of the minimim/maximum y-coordinates
# @return a dictionary with the plotting window map and bounding box
def _get_pixel_coords(geometry, gridsize, xlim, ylim):

    # initialize variables to be returned
    bounds = [geometry.getMinX() + TINY_MOVE, geometry.getMaxX() - TINY_MOVE,
              geometry.getMinY() + TINY_MOVE, geometry.getMaxY() - TINY_MOVE]
    coords = dict()

    if not xlim is None:
        bounds[0] = xlim[0]
        bounds[1] = xlim[1]

    if not ylim is None:
        bounds[2] = ylim[0]
        bounds[3] = ylim[1]

    xcoords = np.linspace(bounds[0], bounds[1], gridsize)
    ycoords = np.linspace(bounds[2], bounds[3], gridsize)

    # add attributes to coords dictionary
    coords['x'] = xcoords
    coords['y'] = ycoords
    coords['bounds'] = bounds

    return coords


##
# @brief This is a helper method to check that z-coord falls within the bounds
#        of the geometry.
# @param geometry a Geometry object which has been initialized with Materials,
#        Cells, Universes and Lattices
# @param zcoord the z coordinate
def _check_zcoord(geometry, zcoord):

    if not is_float(zcoord):
        py_printf('ERROR', 'Unable to produce plot since ' +
                  'the z-coord %d is not a float', zcoord)

    elif zcoord < geometry.getMinZ() or zcoord > geometry.getMaxZ():
        py_printf('ERROR', 'Unable to produce plot since ' +
                  'the z-coord %d is outside the geometry z-bounds (%d, %d)',
                  geometry.getMinZ(), geometry.getMaxZ())


##
# @brief Replace unique data values with a random but reproducible color ID.
# @param data a NumPy array of data to colorize
# @param num_colors the number of random colors to generate
# @param seed the random number seed used to generate colors
# @return
def _colorize(data, num_colors, seed=1):

    # Generate linearly-spaced array of color indices
    all_ids = np.arange(num_colors, dtype=np.int64)

    # Generate linearly-spaced integer color IDs
    id_colors = np.arange(num_colors, dtype=np.int64)

    # Randomly shuffle the linearly-spaced integer color IDs
    numpy.random.seed(1)
    np.random.shuffle(id_colors)

    # Insert random colors into appropriate locations in data array
    ids_to_colors = np.arange(num_colors, dtype=np.int64)
    ids_to_colors[all_ids] = id_colors

    return ids_to_colors.take(data)


##
# @brief This method plots a color-coded 2D surface plot representing the
#        arbitrary data mapped to each FSR in the Geometry.
# @details The routine takes as its first parameter a NumPy array with
#          data for each flat source region must have converged the flat source sources prior to
#          calling this routine. A user may invoke this function from an
#          OpenMOC Python file as follows:
#
# @code
#         num_fsrs = geometry.getNumFSRS()
#         fsrs_to_data = numpy.random.rand(num_fsrs)
#         openmoc.plotter.plot_spatial_data(fsrs_to_data, geometry)
# @endcode
#
# @param fsrs_to_data an array mapping flat source regions to numerical data
# @param geometry a Geometry object which has initialized flat source regions
# @param norm normalize the fission rates to the maximum fission rate
# @param transparent_zeros make regions without fission transparent
# @param gridsize an optional number of grid cells for the plot
# @param xlim optional list/tuple of the minimim/maximum x-coordinates
# @param ylim optional list/tuple of the minimim/maximum y-coordinates
# @param colorbar
# @param title
# @param suptitle
# @param filename
# @param interpolation
# @parma cmap
# @param vmin
# @param vmax
# @param get_figure
def plot_spatial_data(geometry, fsrs_to_data, norm=False, transparent_zeros=True,
                     zcoord=None, gridsize=250, xlim=None, ylim=None,
                     colorbar=False, title=None, suptitle=None,
                     filename='spatial-data', interpolation=None,
                     cmap=None, vmin=None, vmax=None, get_figure=False):

    global subdirectory
    directory = openmoc.get_output_directory() + subdirectory

    # Make directory if it does not exist
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Error checking
    if 'Geometry' not in str(type(geometry)):
        py_printf('ERROR', 'Unable to plot spatial data since %s ' +
                  'input is not a Geometry class object', str(geometry))

    if not isinstance(fsrs_to_data, np.ndarray):
        py_printf('ERROR', 'Unable to plot spatial data since ' +
                  'fsrs_to_data is not a NumPy array')

    if len(fsrs_to_data) != geometry.getNumFSRs():
        py_printf('ERROR', 'Unable to plot spatial data since fsrs_to_data ' +
                  'is length %d but there are %d FSRs in the Geometry',
                  len(fsrs_to_data), geometry.getNumFSRs())

    if not is_integer(gridsize):
        py_printf('ERROR', 'Unable to plot spatial data ' +
                  'since the gridsize %s is not an integer', str(gridsize))

    if gridsize <= 0:
        py_printf('ERROR', 'Unable to plot spatial data ' +
                  'with a negative gridsize (%d)', gridsize)

    if title and not isinstance(title, str):
        py_printf('ERROR', 'Unable to plot spatial data with a '
                  'non-string title %s', str(title))

    if suptitle and not isinstance(suptitle, str):
        py_printf('ERROR', 'Unable to plot spatial data with a '
                  'non-string suptitle %s', str(suptitle))

    if not isinstance(filename, str):
        py_printf('ERROR', 'Unable to plot spatial data with a '
                  'non-string filename %s', str(filename))

    if zcoord is None:
        zcoord = 0.0

    # Check z-coord
    _check_zcoord(geometry, zcoord)

    # Initialize a numpy array of fission rates
    surface = np.zeros((gridsize, gridsize))

    # Retrieve the pixel coordinates
    coords = _get_pixel_coords(geometry, gridsize, xlim, ylim)

    for i in range(gridsize):
        for j in range(gridsize):

            # Find the flat source region IDs for each grid point
            x = coords['y'][i]
            y = coords['x'][j]

            point = openmoc.LocalCoords(x, y, zcoord)
            point.setUniverse(geometry.getRootUniverse())
            geometry.findCellContainingCoords(point)
            fsr_id = geometry.getFSRId(point)

            # If we did not find a region, use a -1 "bad" number color
            if np.isnan(fsr_id):
                surface[j][i] = -1
            # Get the fission rate in this FSR
            else:
                surface[j][i] = fsrs_to_data[fsr_id]

    # Normalize data to maximum if requested
    if norm:
        surface /= np.max(surface)

    # Set zero data entries to NaN so Matplotlib will make them transparent
    if transparent_zeros:
        indices = np.where(surface == 0.0)
        surface[indices] = np.nan

    if cmap is None:
        cmap = plt.get_cmap()

    # Make Matplotlib color "bad" numbers (ie, NaN, INF) with transparent pixels
    cmap.set_bad(alpha=0.0)

    # Plot a 2D color map of the flat source regions fission rates
    fig = plt.figure()
    plt.imshow(np.flipud(surface), extent=coords['bounds'], cmap=cmap,
               vmin=vmin, vmax=vmax, interpolation=interpolation)

    if colorbar:
        plt.colorbar()
    if suptitle:
        plt.suptitle(suptitle)
    if title:
        plt.title(title)

    if get_figure:
        return fig
    else:
        fig.savefig(directory+filename, bbox_inches='tight')
        plt.close()
