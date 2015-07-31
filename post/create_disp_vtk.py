""" create VTK data file from nodout ASCII file generated by ls-dyna

EXAMPLE: python create_disp_vtk.py

Copyright 2015 Mark L. Palmeri (mlp6@duke.edu) and Ningrui Li (nl91@duke.edu)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

def main():
    # let's read in some command-line arguments
    args = parse_cli()

    nodout = open(args.nodout, 'r')

    create_vtk(args, nodout)


def create_vtk(args, nodout):
    """create VTK files to load into Paraview
    this uses the StructuredGrid VTK XML format outlined here:
    http://vtk.org/VTK/img/file-formats.pdf (pages 11-15)
    :param args: CLI input arguments
    :param nodout: nodout filename
    """
    import sys
    from os import remove
    from create_disp_dat import correct_Enot

    disp_position = open('pos_temp.txt', 'w')
    disp_displace = open('disp_temp.txt', 'w')

    # firstStep flag is True only for the first timestep. This is useful
    # because there are certain expension operations that need to be done only
    # once. These operations include creating the temporary positions file and
    # figuring out the number of values along each dimension.
    firstStep = True

    firstLine = True
    timestep_read = False
    timestep_count = 0
    # time value for each timestep
    timestep_values = []
    # number of total nodes, used to write node_ids into vtk
    numNodes = 0
    # x, y, and z hold the range (min, max) of values in each dimension.
    # they also hold the step values/differences between consecutive
    # values in each dimension. This is used to calculate the number of
    # elements going in each dimension.
    x = []
    y = []
    z = []
    xStepFound = False
    yStepFound = False
    zStepFound = False

    disp_position = open('pos_temp.txt', 'w')
    for line in nodout:
        if 'n o d a l' in line:
            raw_data = line.split()
            # get time value of timestep
            # TODO: consider using regular expressions rather than hardcoding this value?
            timestep_values.append(str(float(raw_data[28])))
        if 'nodal' in line:

            # open temporary files for writing displacements
            disp_displace = open('disp_temp.txt', 'w')

            timestep_read = True
            timestep_count += 1
            if timestep_count == 1:
                sys.stdout.write('Time Step: ')
                sys.stdout.flush()
            sys.stdout.write('%i ' % timestep_count)
            sys.stdout.flush()
            continue
        if timestep_read:
            if line.startswith('\n'):  # done reading a time step
                timestep_read = False
                # get last read coordinates - now have range of x, y, z
                # coordinates as well as x, y, z steps. this allows us to get
                # number of steps in x, y, z directions, which is necessary to
                # construct the VTK file.

                if firstStep:
                    x.append(float(lastReadCoords[0]))
                    y.append(float(lastReadCoords[1]))
                    z.append(float(lastReadCoords[2]))

                # no longer reading the first step, so can close temporary
                # point coordinate file.
                if firstStep:
                    disp_position.close()
                    firstStep = False
                # done creating .vts file for this timestep, so we can close
                # temporary displacement file.
                disp_displace.close()

                createVTKFile(args, x, y, z, numNodes, timestep_count)
            else:
                # reading position and displacement data inside a timestep
                raw_data = line.split()

                # correcting for cases when the E is dropped from number
                # formatting
                try:
                    raw_data = [str(float(j)) for j in raw_data]
                except:
                    raw_data = correct_Enot(raw_data)
                    raw_data = [str(float(j)) for j in raw_data]

                # get minimum range of x, y, z coordinates
                if firstLine is True:
                    x.append(float(raw_data[10]))
                    y.append(float(raw_data[11]))
                    z.append(float(raw_data[12]))
                # everything inside the following if statement must only be
                # done once for the first timestep values. This assumes that
                # number of nodes and dimensions of mesh are immutable between
                # timesteps.
                if firstStep:
                    if not firstLine:
                        # check to see if we have x, y, z differences
                        xStep = float(lastReadCoords[0])-float(raw_data[10])
                        if xStep != 0.0 and not xStepFound:
                            x.append(xStep)
                            xStepFound = True

                        yStep = float(lastReadCoords[1])-float(raw_data[11])
                        if yStep != 0.0 and not yStepFound:
                            y.append(yStep)
                            yStepFound = True

                        zStep = float(lastReadCoords[2])-float(raw_data[12])
                        if zStep != 0.0 and not zStepFound:
                            z.append(zStep)
                            zStepFound = True

                    # save the position coordinates in case they are the last
                    # ones to be read.  this is useful for getting the range of
                    # x, y, z coordinates
                    lastReadCoords = raw_data[10:13]
                    # write positions to temporary file. since positions
                    # are the same for all timesteps, this only needs to be
                    # done once.  same with number of nodes.
                    disp_position.write(' '.join(raw_data[10:13])+'\n')
                    numNodes += 1

                if firstLine:
                    firstLine = False

                # write displacements to temporary file
                disp_displace.write(' '.join(raw_data[1:4])+'\n')

    # writing last timestep file
    disp_displace.close()

    createVTKFile(args, x, y, z, numNodes, timestep_count)

    sys.stdout.write('\n')
    sys.stdout.flush()

    # time dependence! look at .pvd file structure for instructions on how to
    # create this.  here is an example of the .pvd file format:
    # http://public.kitware.com/pipermail/paraview/2008-August/009062.html
    createPVDFile(args, timestep_values)

    # cleanup. comment the code following this if you would like to look at
    # the temporary position and displacement files for debugging purposes.
    remove('disp_temp.txt')
    remove('pos_temp.txt')


def parse_cli():
    """
    parse command-line interface arguments
    """
    import argparse

    parser = argparse.ArgumentParser(description="Generate disp.dat "
                                     "data from an ls-dyna nodout file.",
                                     formatter_class=
                                     argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--nodout",
                        help="ASCII file containing nodout data",
                        default="nodout")
    parser.add_argument("--vtkout",
                        help="name of the binary displacement output file",
                        default="disp.dat")
    args = parser.parse_args()

    return args


def createVTKFile(args, x, y, z, numNodes, timestep):
    """
    creates .vts file for visualizing the displacement data during a single
    timestep in Paraview.
    """
    from os import path, makedirs
    # quick check to make sure file extension is correct
   fileName = set_filename(args.vtkout)
    # open .vts file for writing)
    if not path.exists(fileName):
        makedirs(fileName)
    vtkout = open(path.join(fileName, fileName+str(timestep)+'.vts'), 'w')

    # writing the VTK file outline
    vtkout.write('<VTKFile type="StructuredGrid" version="0.1" byte_order="LittleEndian">\n')
    numXValues = abs(round((x[2]-x[0])/x[1]))
    numYValues = abs(round((y[2]-y[0])/y[1]))
    numZValues = abs(round((z[2]-z[0])/z[1]))

    vtkout.write('\t<StructuredGrid WholeExtent="0 %d 0 %d 0 %d">\n' % (numXValues, numYValues, numZValues))
    vtkout.write('\t\t<Piece Extent="0 %d 0 %d 0 %d">\n' % (numXValues, numYValues, numZValues))
    vtkout.write('\t\t\t<PointData Scalars="node_id" Vectors="displacement">\n')
    # writing node ids
    vtkout.write('\t\t\t\t<DataArray type="Float32" Name="node_id" format="ascii">\n')
    for i in range(1, numNodes+1):
        vtkout.write('\t\t\t\t\t%.1f\n' % i)
    vtkout.write('\t\t\t\t</DataArray>\n')
    # writing displacement values
    vtkout.write('\t\t\t\t<DataArray NumberOfComponents="3" type="Float32" Name="displacement" format="ascii">\n')

    with open('disp_temp.txt', 'r') as displace_temp:
        for line in displace_temp:
            vtkout.write('\t\t\t\t\t'+line)

    vtkout.write('\t\t\t\t</DataArray>\n')
    vtkout.write('\t\t\t</PointData>\n')
    # writing point position values
    vtkout.write('\t\t\t<Points>\n')
    vtkout.write('\t\t\t\t<DataArray type="Float32" Name="Array" NumberOfComponents="3" format="ascii">\n')

    with open('pos_temp.txt', 'r') as pos_temp:
        for line in pos_temp:
            vtkout.write('\t\t\t\t\t'+line)

    vtkout.write('\t\t\t\t</DataArray>\n')
    vtkout.write('\t\t\t</Points>\n')
    vtkout.write('\t\t</Piece>\n')
    vtkout.write('\t</StructuredGrid>\n')
    vtkout.write('</VTKFile>')

    vtkout.close()


def createPVDFile(args, timestep_values):
    """creates .pvd file that encompasses displacement for all timesteps.
    The .pvd file can be loaded into Paraview, and the timesteps can be scrolled
    through using the time slider bar.
    :param args: CLI input arguments
    :param timestep_values: vector of timesteps to process
    """
    # quick check to make sure file extension is correct
    fileName = set_filename(args.vtkout)
    # open .pvd file for writing)
    if not path.exists(fileName):
        makedirs(fileName)
    vtkout = open(path.join(fileName, fileName+'.pvd'), 'w')
    vtkout.write('<VTKFile type="Collection" version="0.1">\n')
    vtkout.write('\t<Collection>\n')

    timestep = 1
    for i in timestep_values:
        vtkout.write('\t\t<DataSet timestep="{0}" file="{1}"/>\n'.format(i, fileName+str(timestep)+'.vts'))
        timestep += 1
    vtkout.write('\t</Collection>\n')
    vtkout.write('</VTKFile>\n')


def set_filename(vtkout):
    """set filename from args.vtkout
    strip file extension if exists
    :param vtkout: input arg-specified VTK filename
    :return fileName: filename with extension
    """
    if '.' in vtkout:
        fileName = vtkout[:vtkout.find('.')]
    else:
        fileName = vtkout

    return fileName


if __name__ == "__main__":
    main()
