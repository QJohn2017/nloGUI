import numpy as np
import matplotlib.pyplot as plt
from pynlo.interactions.FourWaveMixing import SSFM
from pynlo.media.fibers import fiber
from pynlo.light.DerivedPulses import SechPulse
from scipy.interpolate import griddata

from matplotlib.widgets import Button, TextBox
import time


# def reinterpolate(x,y,Z,nx=500,ny=500):
#     # x and y are 1D arrays.
#     # z is a 2D array
#     # nx and ny are the number of points in the output image
#
#     print 'Reinterpolating....'
#     X,Y = np.meshgrid(x,y) # make 2D arrays
#
#     x_even = np.linspace(np.min(x),np.max(x),nx)
#     y_even = np.linspace(np.min(y),np.max(y),ny)
#     grid_x, grid_y = np.meshgrid(x_even,y_even)
#
#     grid_z = griddata((X.ravel(),Y.ravel()), Z.ravel(), (grid_x, grid_y), method='nearest')
#
#     return grid_z
#

def drawnow():
    plt.draw()
    plt.pause(0.00001)

def dB(num):
    return 10*np.log10(np.abs(num)**2)
    
    
fig = plt.figure(figsize=(15,9))

axL1 = plt.subplot2grid((3,4), (2,0))
axL2 = plt.subplot2grid((3,4), (2,1),sharex=axL1)

ax1 = plt.subplot2grid((3,4), (0,2),sharex=axL1)
ax2 = plt.subplot2grid((3,4), (0,3))

ax3 = plt.subplot2grid((3,4), (1,2),rowspan=2,sharex=axL1)
ax4 = plt.subplot2grid((3,4), (1,3),rowspan=2,sharey=ax3,sharex=ax2)

for label in ax4.get_yticklabels():
    label.set_visible(False)


plt.subplots_adjust(left=0.05,bottom=0.09,right=0.96,top=0.96,wspace=0.3,hspace=0.29)


axRun = plt.axes([0.4,0.90,0.09,0.04])
bRun = Button(axRun, 'Run Simulation')

axCalc = plt.axes([0.4,0.35,0.09,0.04])
bCalc = Button(axCalc, 'Calc Dispersion')




###Parameter axes###
sl = 0.13
sw = 0.1
sh = 0.04
sv = 0.97 #start vertical
ss = -0.045 #spacing

ax01 = plt.axes([sl, sv+1*ss, sw, sh])
ax02 = plt.axes([sl, sv+2*ss, sw, sh])
ax03 = plt.axes([sl, sv+3*ss, sw, sh])

ax04 = plt.axes([sl, sv+5*ss, sw, sh])
ax05 = plt.axes([sl, sv+6*ss, sw, sh])
ax06 = plt.axes([sl, sv+7*ss, sw, sh])

ax07 = plt.axes([sl, sv+9* ss, sw, sh])
ax08 = plt.axes([sl, sv+10*ss, sw, sh])
ax09 = plt.axes([sl, sv+11*ss, sw, sh])
ax10 = plt.axes([sl, sv+12*ss, sw, sh])
ax11 = plt.axes([sl, sv+13*ss, sw, sh])


bPulse = TextBox(ax01,'Pulse duration (ps)',   initial='0.0284')
bWave  = TextBox(ax02,'Center wavelength (nm)',initial='835')
bPower = TextBox(ax03,'Pulse peak power (kW)', initial='10') # should change to pulse energy

bWindow= TextBox(ax04,'Time window (ps)',  initial='10.0') 
bSteps = TextBox(ax05,'Steps',             initial='50') 
bPoints= TextBox(ax06,'Simulation points', initial='2**13')

bLength= TextBox(ax07,'Fiber length (mm)', initial='15')
bGamma = TextBox(ax08,'Gamma (1/(W km))',  initial='11') 
bBeta2 = TextBox(ax09,'Beta_2 (ps^2/km)',  initial='-7.7') 
bBeta3 = TextBox(ax10,'Beta_3 (ps^3/km)',  initial='0.05') 
bFibWL = TextBox(ax11,'Center WL (nm)',    initial='1000')

buttons = (bPulse, bWave, bPower, bWindow, bSteps, bPoints, bLength, bGamma, bBeta2, bBeta3, bFibWL)


axL1.set_xlabel('Frequency (THz)')
axL1.set_ylabel('D (ps/nm/km)')
axL2.set_xlabel('Frequency (THz)')
axL2.set_ylabel(r'$\beta_2$ (ps$^2$/km)')

ax1.set_xlabel('Frequency (THz)')
ax1.set_ylabel('Intensity (dB)')
ax2.set_xlabel('Time (ps)')



lineL1, = axL1.plot(0,0) # make some dummy lines to hold future data
lineL2, = axL2.plot(0,0)

line1a, = ax1.plot(0,0,color='b') 
line1b, = ax1.plot(0,0,color='r') 

line2a, = ax2.plot(0,0,color='b') 
line2b, = ax2.plot(0,0,color='r') 
###########

# add in some vertical lines that represent the laser wavelength and the central wavelenght of the beta expansion
# update these lines in the L1 and L2 plots whenever they are updated

##########
axL1.axhline(0,alpha=0.5,color='k')
axL2.axhline(0,alpha=0.5,color='k')



def run_simulation(caller=None,prop=False):
    bRun.label.set_text('Setting up...'); drawnow()
    
    # Grab the parameters from the text boxes: 
    pump_pulse_length = float(bPulse.text)
    centerwl          = float(bWave.text) # in nm
    pump_power        = float(bPower.text) * 1e3
    
    window  = float(bWindow.text)
    steps   = int(bSteps.text)
    npoints = int(eval(bPoints.text))
    
    fiber_length = float(bLength.text) * 1e-3
    gamma = float(bGamma.text)
    beta2 = float(bBeta2.text)
    beta3 = float(bBeta3.text)
    fibWL = float(bFibWL.text)
    
    
    
    # set up the pulse parameters
    pulse = SechPulse(pump_power, pump_pulse_length, centerwl, time_window=window,
                        GDD=0, TOD=0.0, NPTS=npoints, frep_MHz=100, power_is_avg=False)

    fiber1 = fiber.FiberInstance() 
    fiber1.generate_fiber(fiber_length,center_wl_nm=fibWL,betas=(beta2*1e-3,beta3*1e-3),gamma_W_m=gamma*1e-3,gvd_units='ps^n/m')
    
    # fiber1.load_from_db(fiber_length, 'dudley')
    
    print 'Parameters\n------------------'
    print '--Pulse--'
    print 'Duration (ps)  %f'%pump_pulse_length
    print 'Center wl (nm) %g'%centerwl
    print 'Pump power (W) %g'%pump_power
    print '  Energy (nJ)  %f'%(pulse.calc_epp()*1e9)
    print '--Simulation--'
    print 'Window (ps)    %f'%window
    print 'Steps          %i'%steps
    print 'Time points    %i'%npoints
    print '--Fiber--'
    print 'Length (mm)     %f'%(fiber_length*1e3)
    print 'Gamma (W-1km-1) %f'%(gamma)
    print 'Beta2 (ps^2/km) %f'%(beta2)
    print 'Beta3 (ps^3/km) %f'%(beta3)
    print 'FiberWL (nm)    %f'%(fibWL)
    
    
    

    W = pulse.W_mks
    T = pulse.T_ps
    xW = W[W>0]
    
    
    D = fiber1.Beta2_to_D(pulse)
    beta = fiber1.Beta2(pulse)
    
    WL = 3e8/W

    # Plot the dispersion in the left plots
    lineL1.set_data(WL[W>0],D[W>0])
    lineL2.set_data(W[W>0],beta[W>0])
    
    # plot the pulse in the top plots
    line1a.set_data(W[W>0],dB(pulse.AW[W>0]))
    line2a.set_data(T,dB(pulse.AT))
    
    if prop==False: 
        bRun.label.set_text('Run simulation'); drawnow()
        return # stop here unless we've actually pressed the "Run" button
    
   
    ######################## Propagation
    t = time.time()
    bRun.label.set_text('Running...'); drawnow()
    
    # set up the propagation parameters
    evol = SSFM.SSFM(local_error=0.001, USE_SIMPLE_RAMAN=True)
    
    # propagate the pulse!
    y, AW, AT, pulse1 = evol.propagate(pulse_in=pulse, fiber=fiber1, n_steps=steps)
          
    zW_in = np.transpose(AW)[:,(W>0)]
    zT_in = np.transpose(AT)
    zW = dB(zW_in)
    zT = dB(zT_in)

    bRun.label.set_text('Drawing plots...'); drawnow()
    
    line1b.set_data(xW,zW[-1])
    line2b.set_data(T,zT[-1])
    
    
    for ax in (ax3,ax4):
        ax.clear()
    
    extent = (np.min(xW),np.max(xW),np.min(y),np.max(y[:-1]))
    ax3.imshow(zW, extent=extent, vmin = np.max(zW) - 40.0, vmax = np.max(zW),aspect='auto',origin='lower')
    ax3.set_xlabel('Frequency (THz)')
    ax3.set_ylabel('Distance (m)')
    
    
    extent = (np.min(T),np.max(T),np.min(y),np.max(y[:-1]))
    ax4.imshow(zT, extent=extent, vmin = np.max(zT) - 40.0, vmax = np.max(zT),aspect='auto',origin='lower')
    ax4.set_xlabel('Delay (ps)')
    
    
    print 'Total time: %.2f sec'%(time.time()-t)
    bRun.label.set_text('Run simulation'); drawnow()




    
def reset_plots(caller=None):
    for ax in (axL1,axL2,ax1,ax2): # rescale the x and ylims
        ax.relim(); ax.autoscale_view()
    
    ax1.set_ylim(-40,10)
    ax2.set_ylim(0,50)
    
     
     


def run_simulation_full(caller=None):
    run_simulation(prop=True)


# for box in buttons:
#     box.on_submit(run_simulation)

bCalc.on_clicked(run_simulation)
bRun.on_clicked(run_simulation_full)

run_simulation(prop=False)

reset_plots()


drawnow()




plt.show()