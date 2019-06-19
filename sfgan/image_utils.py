import numpy as np
import sys
import cv2
import os
import re
import uuid
from scipy import misc
from PIL import Image

def writePFM(file, image, scale=1):
        
    file = open(file, 'wb')

    color = None

    if image.dtype.name != 'float32':
        raise Exception('Image dtype must be float32.')
    
    image = np.flipud(image)  

    if len(image.shape) == 3 and image.shape[2] == 3: # color image
        color = True
    elif len(image.shape) == 2 or len(image.shape) == 3 and image.shape[2] == 1: # greyscale
        color = False
    else:
        raise Exception('Image must have H x W x 3, H x W x 1 or H x W dimensions.')

    file.write('PF\n' if color else 'Pf\n')
    file.write('%d %d\n' % (image.shape[1], image.shape[0]))

    endian = image.dtype.byteorder

    if endian == '<' or endian == '=' and sys.byteorder == 'little':
        scale = -scale

    file.write('%f\n' % scale)

    image.tofile(file)


def readPFM(file):
    file = open(file, 'rb')

    color = None
    width = None
    height = None
    scale = None
    endian = None

    header = file.readline().rstrip()
    if header == 'PF':
        color = True
    elif header == 'Pf':
        color = False
    else:
        raise Exception('Not a PFM file.')

    dim_match = re.match(r'^(\d+)\s(\d+)\s$', file.readline())
    if dim_match:
        width, height = map(int, dim_match.groups())
    else:
        raise Exception('Malformed PFM header.')

    scale = float(file.readline().rstrip())
    if scale < 0: # little-endian
        endian = '<'
        scale = -scale
    else:
        endian = '>' # big-endian

    data = np.fromfile(file, endian + 'f')
    shape = (height, width, 3) if color else (height, width)

    data = np.reshape(data, shape)
    data = np.flipud(data)
    return data

def sceneflowconstruct(of, dt0, dt1):
    #of = DataRead().readPFM('of.pfm') # optical flow at between t and t+1
    #dt0 = DataRead().readPFM('dt0.pfm') # disparity at t
    #dt1 = DataRead().readPFM('dt1.pfm') # disparity at t+1

    # Calculate depth using stereo baseline
    # Use camera matrix to get coordinates in the world frame
    # Use disparity change for sce flow
    # Plot three dimensional motion vectors 
    focal_length = 1050.0
    baseline = 1.0

    # Scene flow as 4D vector
    sf = np.dstack((of[:,:,0:2], dt0, dt1))

    row = np.arange(540)
    px  = np.transpose(np.matlib.repmat(row,960,1))

    column = np.ax = range(960)
    py = np.matlib.repmat(column,540, 1)

    px_offset = 479.5
    py_offset = 269.5
    u = of[:,:,0] # Optical flow in horizontal direction
    v = of[:,:,1] # optical flow in vertical direction

    z0 = (focal_length*baseline)/dt0
    x0 = np.multiply((px-px_offset),z0)/focal_length
    y0 = np.multiply((py-py_offset),z0)/focal_length

    #print np.float32(x0).dtype

    z1 = (focal_length*baseline)/dt1
    x1 = np.multiply((px+u-px_offset),z1)/focal_length
    y1 = np.multiply((py+v-py_offset),z1)/focal_length


    # Scene flow vectors

    dX = np.float32(x1 - x0)
    dY = np.float32(y1 - y0)
    dZ = np.float32(z1 - z0)

    scene_flow = np.dstack((dX, dY, dZ))

    return scene_flow


def preprocess(img):

    img = cv2.resize(img, (512,384))
    return img

'''
def overlay(image1, image2, alpha):            
	newImage = cv2.addWeighted(image1, alpha, image2, 1-alpha, 0)
    newImage = cv2.cvtColor(newImage,cv2.COLOR_BGR2RGB)
	return newImage
'''

# Normalize the  image
def normalize(x):
    """
    argument
    - x: input image data in numpy array [32, 32, 3]
    return
    - normalized x 
    """
    min_val = np.min(x)
    max_val = np.max(x)
    x = (x-min_val) / (max_val-min_val)
    return x


def overlay(image1, image2, alpha):
    
    newImage = cv2.addWeighted(image1, alpha, image2, 1-alpha, 0)
    newImage = cv2.cvtColor(newImage, cv2.COLOR_BGR2RGB)
    return newImage

''' Write Disparity in KITTI format'''
def kitti_disp_write(disp, filename):

    im = disp*256
    im[disp==0] = 1
    im[im<0] = 0
    im[im<65535] = 0
    im = np.uint16(im)
    cv2.imwrite(filename, im)

#  To Do 
# def kitti_flow_write(flow, filename):

# KITTI Optical Flow
def kitti_flow_read():
    """
    Read optical flow from KITTI .png file
    :param flow_file: name of the flow file
    :return: optical flow data in matrix
    """
    flow_object = png.Reader(filename=flow_file)
    flow_direct = flow_object.asDirect()
    flow_data = list(flow_direct[2])
    (w, h) = flow_direct[3]['size']
    planes = flow_direct[3]['planes']
    flow = np.zeros((h, w, planes), dtype=np.float64)
    custom = planes==2
    for i in range(len(flow_data)):
        flow[i, :, 0] = flow_data[i][0::planes]
        flow[i, :, 1] = flow_data[i][1::planes]
        if not custom:
            flow[i, :, 2] = flow_data[i][2::planes]

    flow[:, :, 0:2] = (flow[:, :, 0:2] - 2 ** 15) / precision
    if not custom:
        invalid_idx = (flow[:, :, 2] == 0)
        flow[invalid_idx, 0] = 0
        flow[invalid_idx, 1] = 0
    return flow

def kitti_flow_Write():
    """
    Write KITTI optical flow.
    """
    if not has_png:
        print('Error. Please install the PyPNG library')
        return


    if valid==None:
        valid_ = np.ones(u.shape,dtype='uint16')
    else:
        valid_ = valid.astype('uint16')


    u = u.astype('float64')
    v = v.astype('float64')

    u_ = ((u*64.0)+2**15).astype('uint16')
    v_ = ((v*64.0)+2**15).astype('uint16')

    I = np.dstack((u_,v_,valid_))

    W = png.Writer(width=u.shape[1],
                   height=u.shape[0],
                   bitdepth=16,
                   planes=3)

    with open(fpath,'wb') as fil:
        W.write(fil,I.reshape((-1,3*u.shape[1])))

# KITTI Disparity 
def kitti_disp_read():
       
    

    


###### IO Routines from University of Freiburg ################
###### https://lmb.informatik.uni-freiburg.de/resources/datasets/SceneFlowDatasets.en.html

def read(file):
    if file.endswith('.float3'): return readFloat(file)
    elif file.endswith('.flo'): return readFlow(file)
    elif file.endswith('.ppm'): return readImage(file)
    elif file.endswith('.pgm'): return readImage(file)
    elif file.endswith('.png'): return readImage(file)
    elif file.endswith('.jpg'): return readImage(file)
    elif file.endswith('.pfm'): return readPFM(file)[0]
    else: raise Exception('don\'t know how to read %s' % file)

def write(file, data):
    if file.endswith('.float3'): return writeFloat(file, data)
    elif file.endswith('.flo'): return writeFlow(file, data)
    elif file.endswith('.ppm'): return writeImage(file, data)
    elif file.endswith('.pgm'): return writeImage(file, data)
    elif file.endswith('.png'): return writeImage(file, data)
    elif file.endswith('.jpg'): return writeImage(file, data)
    elif file.endswith('.pfm'): return writePFM(file, data)
    else: raise Exception('don\'t know how to write %s' % file)

def readFlow(name):
    if name.endswith('.pfm') or name.endswith('.PFM'):
        return readPFM(name)[0][:,:,0:2]

    f = open(name, 'rb')

    header = f.read(4)
    if header.decode("utf-8") != 'PIEH':
        raise Exception('Flow file header does not contain PIEH')

    width = np.fromfile(f, np.int32, 1).squeeze()
    height = np.fromfile(f, np.int32, 1).squeeze()

    flow = np.fromfile(f, np.float32, width * height * 2).reshape((height, width, 2))

    return flow.astype(np.float32)

def readImage(name):
    if name.endswith('.pfm') or name.endswith('.PFM'):
        data = readPFM(name)[0]
        if len(data.shape)==3:
            return data[:,:,0:3]
        else:
            return data

    return misc.imread(name)

def writeImage(name, data):
    if name.endswith('.pfm') or name.endswith('.PFM'):
        return writePFM(name, data, 1)

    return misc.imsave(name, data)

def writeFlow(name, flow):
    f = open(name, 'wb')
    f.write('PIEH'.encode('utf-8'))
    np.array([flow.shape[1], flow.shape[0]], dtype=np.int32).tofile(f)
    flow = flow.astype(np.float32)
    flow.tofile(f)

def readFloat(name):
    f = open(name, 'rb')

    if(f.readline().decode("utf-8"))  != 'float\n':
        raise Exception('float file %s did not contain <float> keyword' % name)

    dim = int(f.readline())

    dims = []
    count = 1
    for i in range(0, dim):
        d = int(f.readline())
        dims.append(d)
        count *= d

    dims = list(reversed(dims))

    data = np.fromfile(f, np.float32, count).reshape(dims)
    if dim > 2:
        data = np.transpose(data, (2, 1, 0))
        data = np.transpose(data, (1, 0, 2))

    return data

def writeFloat(name, data):
    f = open(name, 'wb')

    dim=len(data.shape)
    if dim>3:
        raise Exception('bad float file dimension: %d' % dim)

    f.write(('float\n').encode('ascii'))
    f.write(('%d\n' % dim).encode('ascii'))

    if dim == 1:
        f.write(('%d\n' % data.shape[0]).encode('ascii'))
    else:
        f.write(('%d\n' % data.shape[1]).encode('ascii'))
        f.write(('%d\n' % data.shape[0]).encode('ascii'))
        for i in range(2, dim):
            f.write(('%d\n' % data.shape[i]).encode('ascii'))

    data = data.astype(np.float32)
    if dim==2:
        data.tofile(f)

    else:
        np.transpose(data, (2, 0, 1)).tofile(f)
