# coding: utf-8

import numpy as np
import time
import matplotlib.pyplot as plt
from scipy.sparse import csr_matrix
from scipy.sparse import lil_matrix

print('Imported MigPreFuncoes now')
def ricker(nps,fr,dt):
    npt = nps*dt
    t = np.arange(-npt/2,npt/2,dt)
    #t = np.linspace(-npt/2,npt/2,nps)
    rick1=(1-t *t * fr**2 *np.pi**2  ) * np.exp(- t**2 * np.pi**2 * fr**2 )
    rick=rick1[int(np.round(nps/2))-(int(np.round(1/fr/dt)))+1:nps]
    l = len(rick)
    if l<nps:
        rick2=np.append(rick,np.zeros([1,nps-1]))
    l=nps
    rick=rick2
    return np.array(rick)

# Equivalente ao sub2ind do Matlab
def sub2ind(array_shape, rows, cols):
    #return rows*array_shape[1] + cols
    return cols*array_shape[0] + rows

def buildL2(L,Z,X,ind,z0,x0,z1,x1):
    [pz,px,j]=lineseg2(z0,x0,z1,x1)
    for i in range(0,j-1):
        l = np.linalg.norm([pz[i+1]-pz[i],px[i+1]-px[i]])
        a = np.floor((pz[i+1]+pz[i])/2)-1
        if a == Z:
            a = Z-1
        elif a==-1:
            a = 0
        b = np.floor((px[i+1]+px[i])/2)-1
        if b == X:
            b = X-1
        elif b == -1:
            b = 0
        L[ind,sub2ind([Z,X],a,b)]=l
    return L


def subs2(sZ,sX):
    z = 2*sZ-1
    x = 2*sX-1
    z1 = z-1
    x1 = x-1
    #dA = csr_matrix(np.zeros([z*x,z1*x1]))
    dA = lil_matrix((z*x,z1*x1))
    for j in range(0,z):
        for i in range(0,x):
            #print(i)
            dA = buildL2(dA,z1,x1,sub2ind([z,x],j,i),sZ,sX,j,i)
    return dA

def lineseg2(z0,x0,z1,x1):
    z1=z1+1
    x1=x1+1
    dz = (z1-z0)
    dx = (x1-x0)
    sgnz = np.sign(dz)
    sgnx = np.sign(dx)
    pz=[]
    px=[]
    pz.append(z0)
    px.append(x0)
    j = 2
    if sgnz!=0:
        zrange = np.arange(z0+sgnz,z1,sgnz)
        for z in zrange:
            pz.append(z)
            px.append(x0 + (z-z0)*dx/dz)
            j = j+1
    if sgnx!=0:
        xrange = np.arange(x0+sgnx,x1,sgnx)
        for x in xrange:
            px.append(x)
            pz.append(z0+(x-x0)*dz/dx)
            j = j+1
            
            
    pz.append(z1)
    px.append(x1)
    px = np.sort(px)
    pz = np.sort(pz)
    if  sgnx==-sgnz:
        px=np.flip(px)
    return [pz,px,j]

def Mray(SW,SP,DX):
    [Z,X]=SW.shape
    ddef = 10000
    delt = np.max(SW.flatten())
    sZ = 7; sX = 7;
    dA = subs2(sZ,sX)
    
    ZZ = Z+2*sZ-1
    XX = X+2*sX-1
    T = np.ones([ZZ,XX])*ddef
    mark = np.ones([ZZ,XX])*ddef
    
    Z2 = Z + 2*sZ - 2
    X2 = X+2*sX - 2
    S = np.ones([Z2,X2])
    
    Z1 = np.arange(sZ-1,Z+sZ)
    X1 = np.arange(sX-1,X+sX)
    mark[np.ix_(Z1.flatten(),X1.flatten())] = 0
    
    Z2 = np.arange(sZ-1,Z+sZ-1)
    X2 = np.arange(sX-1,X+sX-1)
    S[np.ix_(Z2.flatten(),X2.flatten())] = SW
    S[np.ix_([Z+sZ-1],X2.flatten())] = 2*S[np.ix_([Z+sZ-2],X2.flatten())] - S[np.ix_([Z+sZ-3],X2.flatten())]
    S[np.ix_(Z2.flatten(),[X+sX-1])] = 2*S[np.ix_(Z2.flatten(),[X+sX-2])] - S[np.ix_(Z2.flatten(),[X+sX-3])]
    S[np.ix_([Z+sZ-1],[X+sX-1])] = 2*S[np.ix_([Z+sZ-2],[X+sX-2])] - S[np.ix_([Z+sZ-3],[X+sX-3])]
    
    dz = -sZ+1
    dx = -sX+1
    SP = np.array(SP)
    
    
    z = SP[0]
    x = SP[1]
    z = z+sZ-1
    x = x+sX-1
    T[z,x] = 0
    mark[z,x] = ddef
    
    a = 2*sZ-1
    b = 2*sX-1
    aa = np.arange(-sZ+1,sZ)
    bb = np.arange(-sX+1,sX)
    aas = np.arange(-sZ+1,sZ-1)
    bs = np.arange(-sX+1,sX-1)
    
    AS = S[np.ix_((aas+z).flatten(),(bs+x).flatten())]
    aaa = aa + z
    bbb = bb + x
    TT = T[np.ix_(aaa.flatten(),bbb.flatten())]
    
    K = dA*AS.flatten()+T[z,x]
    KK=np.reshape(K,[13,13])
    BB=np.minimum(KK,TT)
    T[np.ix_(aaa.flatten(),bbb.flatten())] = np.minimum(np.reshape(dA*AS.flatten('F')+T[z,x],[a,b]),TT)
    
    
    maxt = np.max(np.max(T[z-1:z+1,x-1:x+1]))
    while 1:
        H = np.argwhere(T + mark <= maxt + delt)
        hz = H[:,0]
        hx = H[:,1]
        hsz = len(hz)
        for ii in range(0,hsz):
            z = hz[ii]
            x = hx[ii]
            maxt = np.max([maxt,T[z,x]])
            mark[z,x] = ddef
            AS = S[np.ix_((aas + z).flatten(), (bs + x).flatten())]
            aaa = aa + z
            bbb = bb + x
            TT = T[np.ix_(aaa.flatten(),bbb.flatten())]
            T[np.ix_(aaa.flatten(),bbb.flatten())] = np.minimum(np.reshape(dA*AS.flatten('F')+T[z,x],[a,b]),TT)
        if mark[np.ix_(Z2.flatten(),X2.flatten())].all():
            break
        Ttable = T[np.ix_(Z2.flatten(),X2.flatten())]*DX
    return Ttable


def raymodel3(SW,dx,nx,filename):
    DX = dx
    traveltimesrc=[]
    sx=np.arange(0,nx)*DX
    
    for ixsrc in range(0,nx):
        SP = [0,ixsrc]
        Ttable = Mray(SW,SP,DX)
        traveltimesrc.append(Ttable[:,:])
        
    with open(filename, 'wb') as f:
        np.save(f, traveltimesrc)
    return traveltimesrc

def migvsp(timer,isx,dt,gather):
    [nt,ntr]=gather.shape
    [ntr2,nz,nx]=timer.shape
    if ntr!=ntr2:
        print('Gather e traveltime table tem numero diferente de traços')
    mig=np.zeros([nz,nx])
    # Loop over each trace of the shot gather at src isx
    for igx in range(0,ntr):
        t = timer[isx,0:nz,0:nx] + timer[igx,0:nz,0:nx]
        t2 = (t<nt)*t #Check how to avoid this... summing amplitudes for t>nt
        trace1=gather.T[np.ix_([igx],t2.flatten().astype(np.int32))]
        trace1=trace1.reshape([nz,nx])
        mig[0:nz,0:nx]=mig[0:nz,0:nx] + trace1
        
    
    return mig
