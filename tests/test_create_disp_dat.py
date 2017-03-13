import sys
import os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(myPath, '/../post/'))


def test_parse_nodoutR61():
    """correctly parse data from R6.1 nodout files
    """
    from create_disp_dat import parse_line

    nodout = open("tests/nodout", "r")
    n = nodout.readlines()
    line = n[8]
    raw_data = parse_line(line)

    assert raw_data[0] == 6
    assert raw_data[1] == 0.0
    assert raw_data[3] == -1.5


def test_parse_nodoutR8():
    """correctly parse data from R8 nodout files
    """
    from create_disp_dat import parse_line

    nodout = open("tests/nodout", "r")
    n = nodout.readlines()
    line = n[10]
    raw_data = parse_line(line)

    assert raw_data[0] == 8
    assert raw_data[1] == 0.0
    assert raw_data[3] == -1.5


def test_correct_Enot():
    """test fix -??? -> E-100
    """
    from create_disp_dat import parse_line

    nodout = open("tests/nodout", "r")
    n = nodout.readlines()
    line = n[9]

    raw_data = parse_line(line)

    assert raw_data[3] == 0.0


def test_count_timesteps():
    """test counting time steps in nodout
    """
    from create_disp_dat import count_timesteps

    ts_count = count_timesteps("tests/nodout")

    assert ts_count == 2


def test_write_header(tmpdir):
    """test writing disp.dat header
    """
    from create_disp_dat import open_dispout
    from create_disp_dat import write_headers
    import struct

    header = {'numnodes': 4,
              'numdims': 3,
              'numtimesteps': 2
              }

    fname = tmpdir.join('testheader.dat')
    dispout = open_dispout(fname.strpath)
    write_headers(dispout, header)
    dispout.close()

    with open(fname, 'rb') as dispout:
        h = struct.unpack('fff', dispout.read(4 * 3))

    assert h[0] == 4.0
    assert h[1] == 3.0
    assert h[2] == 2.0


def test_write_data(tmpdir):
    """test writing data to disp.dat
    """
    from create_disp_dat import open_dispout
    from create_disp_dat import process_timestep_data
    import struct
    from pytest import approx

    fname = tmpdir.join('testdata.dat')
    dispout = open_dispout(fname.strpath)
    data = []
    data.append([float(0.0), float(0.1), float(0.2), float(0.3)])
    data.append([float(1.0), float(1.1), float(1.2), float(1.3)])
    process_timestep_data(data, dispout, writenode=True)
    dispout.close()

    with open(fname, 'rb') as f:
        d = struct.unpack(8 * 'f', f.read(4 * 8))

    assert d[0] == 0.0
    assert d[1] == 1.0
    assert d[2] == approx(0.1)
    assert d[3] == approx(1.1)
    assert d[7] == approx(1.3)
