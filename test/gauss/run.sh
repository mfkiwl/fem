python ../../mesh/GenMesh.py --xyz -0.5 0.0 0.0 1.0 -3.0 0.0 --numElem 10 20 60
python ../../mesh/bc.py
python ../../mesh/GaussExc.py --sigma 0.25 0.25 0.75 --center 0.0 0.0 -1.5 
ls-dyna-s ncpu=2 i=gauss.dyn
python ../../post/create_disp_dat.py
python ../../post/create_res_sim_mat.py
