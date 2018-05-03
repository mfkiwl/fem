fid=fopen('dyna-I-f7.20-F1.3-FD0.020-a0.50.ned');
numNodes=fread(fid, 1, 'int');
intensity=fread(fid, numNodes, 'double');
disp(intensity);
threads=fread(fid, 1, 'int');
soundSpeed=fread(fid, 1, 'int');
samplingFrequency=fread(fid, 1, 'int');
alpha=fread(fid, 1, 'double');
fnum=fread(fid, 1, 'double');
focus.x=fread(fid, 1, 'double');
focus.y=fread(fid, 1, 'double');
focus.z=fread(fid, 1, 'double');
disp(focus);
frequency=fread(fid, 1, 'double');
length=fread(fid, 1, 'int');
temp1=fread(fid, length, 'char');
temp2=char(temp1);
transducer=temp2.';
length=fread(fid, 1, 'int');
temp1=fread(fid, length, 'char');
temp2=char(temp1);
impulse=temp2.';

% have to skip 4 bytes because C pads the nodeEntry struct. could use 'ftell',
% too

for i = 1:numNodes
	pointsAndNodes(i).nodeID = fread(fid, 1, 'int');
    skip = fread(fid, 1, 'int');
	pointsAndNodes(i).x = fread(fid, 1, 'double');
	pointsAndNodes(i).y = fread(fid, 1, 'double');
	pointsAndNodes(i).z = fread(fid, 1, 'double');
end

xdcGetSize=fread(fid, 1, 'int');
ThData=fread(fid, xdcGetSize, 'double');
