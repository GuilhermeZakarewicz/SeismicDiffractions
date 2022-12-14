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


def taper(ntr,ns,app,isx,igx):
    
    ar = np.zeros([ns,ntr])
    cmp = int((isx+igx)/2)
    window = np.hanning(2*app)
    
    if (cmp-app)<0: 
        if (cmp+app)>ntr:
            ntr_2 = int(ntr/2)
            lw_2 = int(len(window)/2)            
            ar[:,:] = window[(lw_2 - ntr_2):(lw_2 + ntr_2)]  
        else:
            ar[:,0:(cmp+app)] = window[abs(cmp-app):]   
    elif (cmp+app)>ntr:
        ar[:,(abs(cmp-app)):] = window[0:(ntr - abs(cmp-app))]
    else:
        ar[:,(cmp-app):(cmp+app)] = window 
    
    return ar


def peso(TTh,dt,X,Y,igx,isx):
    """
    Calcula a fun????o peso w(s,x,r)
    Entrada:
    TTh - tabela do tempo de tr??nsito calculada com a fun????o raymodel3
    dt - discretiza????o do tempo (s)
    X - componente X do modelo; X = np.sin(m_theta); X.shape = [nz,nx]
    Y - componente Y do modelo; Y = np.cos(m_theta); Y.shape = [nz,nx]
    igx - posi????o do receptor 
    isx - posi????o da fonte
    Sa??da:
    w - fun????o peso (w.shape=[nz,nx])
    """
    
    timer=np.round(TTh/dt)+1

    gH = np.gradient(timer, axis=2) #gradiente horizontal
    gV = np.gradient(timer, axis=1) #gradiente vertical

    prV = gV[igx,:,:] 
    prH = gH[igx,:,:] 

    psV = gV[isx,:,:] 
    psH = gH[isx,:,:] 

    pH = psH + prH
    pV = psV + prV
    
    norma = np.sqrt(pH**2 + pV**2)

    for idx, x in np.ndenumerate(norma): #avoid nan's
        if x==0:
            norma[idx]=1

    w = (pH/norma * X) + (pV/norma * Y)
    
    return w


def migvsp(timer,isx,dt,gather):
    [nt,ntr]=gather.shape
    [ntr2,nz,nx]=timer.shape
    if ntr!=ntr2:
        print('Gather e traveltime table tem numero diferente de tra??os')
    mig=np.zeros([nz,nx])
    # Loop over each trace of the shot gather at src isx
    for igx in range(0,ntr):
        w = peso(igx,isx)
        t = timer[isx,0:nz,0:nx] + timer[igx,0:nz,0:nx]
        t2 = (t<nt)*t #Check how to avoid this... summing amplitudes for t>nt
        trace1=gather.T[np.ix_([igx],t2.flatten().astype(np.int32))]
        trace1=trace1.reshape([nz,nx])*w
        mig[0:nz,0:nx]=mig[0:nz,0:nx] + trace1
        
    
    return mig

def taper(ntr,ns,app,isx,igx):
    
    ar = np.zeros([ns,ntr])
    cmp = int((isx+igx)/2)
    window = np.hanning(2*app)
    
    if (cmp-app)<0: 
        if (cmp+app)>ntr:
            ntr_2 = int(ntr/2)
            lw_2 = int(len(window)/2)            
            ar[:,:] = window[(lw_2 - ntr_2):(lw_2 + ntr_2)]  
        else:
            ar[:,0:(cmp+app)] = window[abs(cmp-app):]   
    elif (cmp+app)>ntr:
        ar[:,(abs(cmp-app)):] = window[0:(ntr - abs(cmp-app))]
    else:
        ar[:,(cmp-app):(cmp+app)] = window 
    
    return ar




def migvsp_winapp(gather,isx,dx,dz,dt,win,dwin,app,TTh,X,Y):
    """
    Calcula a migra????o para 1 arquivo (1 tiro) com janela (window) e abertura (aperture)
    Considera a fun????o peso w = w(s,r,t)
    
    Entrada:
    gather - dado s??smico (nt,ntr)
    isx - posi????o do tiro
    dx - discretiza????o no eixo x (m)
    dz - discretiza????o no eixo z (m)
    dt - discretiza????o do tempo (s)
    win - (tamanho da janela)/2
    dwin - passo da janela. Preferencialmente, dwin=dt
    app - tamanho da abertura
    TTh - tabela do tempo de tr??nsito calculada com a fun????o raymodel3
    X - componente X do modelo; X = np.sin(m_theta); X.shape = [nz,nx]
    Y - componente Y do modelo; Y = np.cos(m_theta); Y.shape = [nz,nx]
    
    Sa??da:
    mig - imagem migrada com janela e abertura. Formato: matriz [nt,ntr]
    """
    timer=np.round(TTh/dt)+1
    window = np.arange(-win,win,dwin)
    [nt,ntr]=gather.shape
    [ntr2,nz,nx]=timer.shape
    if ntr!=ntr2:
        print('Gather e traveltime table tem numero diferente de tra??os')
        
    mig=np.zeros([nz,nx])
    
    IX = np.arange(0,nx*dx,dx)
    IZ = np.arange(0,nz*dz,dz)
    [IIX,IIZ] = np.meshgrid(IX,IZ)
    # Loop over each trace of the shot gather at src isx
    for igx in range(0,ntr):
        w = peso(TTh,dt,X,Y,igx,isx)
        trace_win = np.zeros([nz,nx])
        R = np.sqrt(IIZ**2 + (IIX-(igx+isx)/2*dx)**2)
        r_mask = (R==0)
        R[r_mask]= dx/1000
        obli = IIZ/R
        trace_app = taper(ntr,nz,app,isx,igx) 
        
        for j in range(len(window)):
            t = timer[isx,0:nz,0:nx] + timer[igx,0:nz,0:nx] #t_{d}
            twin = t + window[j]
            t2 = (twin<nt)*twin 
            trace1=gather.T[np.ix_([igx],t2.flatten().astype(np.int32))] 
            trace1 = trace1.reshape([nz,nx])*(w) 
            trace1 = trace1*trace_app
            trace_win = trace_win+trace1
        
        mig[0:nz,0:nx]=mig[0:nz,0:nx] + trace_win*obli
        
    return mig





def migstack_winapp(files,isx,dx,dz,dt,win,dwin,app,TTh,X,Y):
        
    """
    Calcula a migra????o para v??rios arquivos (todos os tiros ao longo de uma linha s??smica) com janela (window) e abertura (aperture)
    Stack das imagens migradas de cada tiro
    Considera a fun????o peso w = w(s,r,t)
    
    Entrada:
    files - lista (array) com os dados s??smicos. 
    isx - posi????o do tiro
    dx - discretiza????o no eixo x (m)
    dz - discretiza????o no eixo z (m)
    dt - discretiza????o do tempo (s)
    win - (tamanho da janela)/2
    dwin - passo da janela. Preferencialmente, dwin=dt
    app - tamanho da abertura
    TTh - tabela do tempo de tr??nsito calculada com a fun????o raymodel3
    X - componente X do modelo; X = np.sin(m_theta); X.shape = [nz,nx]
    Y - componente Y do modelo; Y = np.cos(m_theta); Y.shape = [nz,nx]
    
    Sa??da:
    mig - imagem migrada com janela e abertura. Formato: matriz [nt,ntr]
    """
    
    timer=np.round(TTh/dt)+1
    migs = []
        
    for count,gather in enumerate(files):
        isx = count
        print(f"shot {isx}")
    
        window = np.arange(-win,win,dwin)
        [nt,ntr]=gather.shape
        [ntr2,nz,nx]=timer.shape
        if ntr!=ntr2:
            print('Gather e traveltime table tem numero diferente de tra??os')

        mig=np.zeros([nz,nx])
        mig_final=np.zeros([nz,nx])

        IX = np.arange(0,nx*dx,dx)
        IZ = np.arange(0,nz*dz,dz)
        [IIX,IIZ] = np.meshgrid(IX,IZ)
        # Loop over each trace of the shot gather at src isx
        for igx in range(0,ntr):
            w = peso(TTh,dt,X,Y,igx,isx)
            trace_win = np.zeros([nz,nx])
            R = np.sqrt(IIZ**2 + (IIX-(igx+isx)/2*dx)**2)
            r_mask = (R==0)
            R[r_mask]= dx/1000
            obli = IIZ/R
            trace_app = taper(ntr,nz,app,isx,igx) 

            for j in range(len(window)):
                t = timer[isx,0:nz,0:nx] + timer[igx,0:nz,0:nx] #t_{d}
                twin = t + window[j]
                t2 = (twin<nt)*twin 
                trace1=gather.T[np.ix_([igx],t2.flatten().astype(np.int32))] 
                trace1 = trace1.reshape([nz,nx])*w #se????o? imshow em um separado
                trace1 = trace1*trace_app
                trace_win = trace_win+trace1

            mig[0:nz,0:nx]=mig[0:nz,0:nx] + trace_win*obli
        
        migs.append(mig)
    
    mig_final = np.add.reduce(migs)
        
    return mig_final






def migvsp_winapp_diff(gather,isx,dx,dz,dt,win,dwin,app,TTh,X,Y):
        
    """
    Calcula a imagem de difra????o para 1 arquivo (1 tiro) com janela (window) e abertura (aperture)
    Considera a fun????o peso w = 1 - w(s,r,t)
    
    Entrada:
    gather - dado s??smico (nt,ntr)
    isx - posi????o do tiro
    dx - discretiza????o no eixo x (m)
    dz - discretiza????o no eixo z (m)
    dt - discretiza????o do tempo (s)
    win - (tamanho da janela)/2
    dwin - passo da janela. Preferencialmente, dwin=dt
    app - tamanho da abertura
    TTh - tabela do tempo de tr??nsito calculada com a fun????o raymodel3
    X - componente X do modelo; X = np.sin(m_theta); X.shape = [nz,nx]
    Y - componente Y do modelo; Y = np.cos(m_theta); Y.shape = [nz,nx]
    
    Sa??da:
    mig - imagem de difra????es a partir de migra????o com janela e abertura. Formato: matriz [nt,ntr]
    """
    
    timer=np.round(TTh/dt)+1
    window = np.arange(-win,win,dwin)
    [nt,ntr]=gather.shape
    [ntr2,nz,nx]=timer.shape
    if ntr!=ntr2:
        print('Gather e traveltime table tem numero diferente de tra??os')
        
    mig=np.zeros([nz,nx])
    
    IX = np.arange(0,nx*dx,dx)
    IZ = np.arange(0,nz*dz,dz)
    [IIX,IIZ] = np.meshgrid(IX,IZ)
    # Loop over each trace of the shot gather at src isx
    for igx in range(0,ntr):
        w = peso(TTh,dt,X,Y,igx,isx)
        trace_win = np.zeros([nz,nx])
        R = np.sqrt(IIZ**2 + (IIX-(igx+isx)/2*dx)**2)
        r_mask = (R==0)
        R[r_mask]= dx/1000
        obli = IIZ/R
        trace_app = taper(ntr,nz,app,isx,igx) 
        
        for j in range(len(window)):
            t = timer[isx,0:nz,0:nx] + timer[igx,0:nz,0:nx] #t_{d}
            twin = t + window[j]
            t2 = (twin<nt)*twin 
            trace1=gather.T[np.ix_([igx],t2.flatten().astype(np.int32))] 
            trace1 = trace1.reshape([nz,nx])*(1-w) 
            trace1 = trace1*trace_app
            trace_win = trace_win+trace1
        
        mig[0:nz,0:nx]=mig[0:nz,0:nx] + trace_win*obli
        
    return mig







def migstack_winapp_diff(files,isx,dx,dz,dt,win,dwin,app,TTh,X,Y):
            
    """
    Calcula a migra????o para v??rios arquivos (todos os tiros ao longo de uma linha s??smica) com janela (window) e abertura (aperture)
    Stack das imagens migradas de cada tiro
    Considera a fun????o peso w = 1 - w(s,r,t)
    
    Entrada:
    files - lista (array) com os dados s??smicos. 
    isx - posi????o do tiro
    dx - discretiza????o no eixo x (m)
    dz - discretiza????o no eixo z (m)
    dt - discretiza????o do tempo (s)
    win - (tamanho da janela)/2
    dwin - passo da janela. Preferencialmente, dwin=dt
    app - tamanho da abertura
    TTh - tabela do tempo de tr??nsito calculada com a fun????o raymodel3
    X - componente X do modelo; X = np.sin(m_theta); X.shape = [nz,nx]
    Y - componente Y do modelo; Y = np.cos(m_theta); Y.shape = [nz,nx]
    
    Sa??da:
    mig - imagem de difra????es a partir de migra????es com janela e abertura. Formato: matriz [nt,ntr]
    """
    
    timer=np.round(TTh/dt)+1
    migs = []
        
    for count,gather in enumerate(files):
        isx = count
        print(f"shot {isx}")
    
        window = np.arange(-win,win,dwin)
        [nt,ntr]=gather.shape
        [ntr2,nz,nx]=timer.shape
        if ntr!=ntr2:
            print('Gather e traveltime table tem numero diferente de tra??os')

        mig=np.zeros([nz,nx])
        mig_final=np.zeros([nz,nx])

        IX = np.arange(0,nx*dx,dx)
        IZ = np.arange(0,nz*dz,dz)
        [IIX,IIZ] = np.meshgrid(IX,IZ)
        # Loop over each trace of the shot gather at src isx
        for igx in range(0,ntr):
            w = peso(TTh,dt,X,Y,igx,isx)
            trace_win = np.zeros([nz,nx])
            R = np.sqrt(IIZ**2 + (IIX-(igx+isx)/2*dx)**2)
            r_mask = (R==0)
            R[r_mask]= dx/1000
            obli = IIZ/R
            trace_app = taper(ntr,nz,app,isx,igx) 

            for j in range(len(window)):
                t = timer[isx,0:nz,0:nx] + timer[igx,0:nz,0:nx] #t_{d}
                twin = t + window[j]
                t2 = (twin<nt)*twin 
                trace1=gather.T[np.ix_([igx],t2.flatten().astype(np.int32))] 
                trace1 = trace1.reshape([nz,nx])*(1-w) #se????o? imshow em um separado
                trace1 = trace1*trace_app
                trace_win = trace_win+trace1

            mig[0:nz,0:nx]=mig[0:nz,0:nx] + trace_win*obli
        
        migs.append(mig)
    
    mig_final = np.add.reduce(migs)
        
    return mig_final
