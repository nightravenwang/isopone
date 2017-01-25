import numpy as np
from numpy.random import uniform 
from numpy.random import rand, randint
from GeneralFunction import *
from Ship_FCM import *
import matplotlib.pyplot as plt
from matplotlib import animation
from datetime import datetime, timedelta

# INITIATE WEATHER CLASS
weather_info = WeatherInfo("Metdata_NorthAtlantic_2015-01-01-2015-01-31.mat")
# INITIATE SHIP INFORMATION
ship_info = Ship_FCM()
# BATHYMETRIC CLASS
bathymetry = Bathymetry("GEBCO_2014_2D_-75.0_30.0_10.0_55.0.nc")

class state:
    def __init__(self, longi, lati, bearing):
        self.longi = longi
        self.lati = lati
        self.bearing = bearing
        self.time = 0.0
        self.speed = 0.0
        
        
class GA_beta:
    def __init__(self， dep, des, n):
        X,Y = m.gcpoints(dep[0], dep[1], des[0], des[1], n)
        x,y = m(X, Y, inverse = True)
        
        
        
        
def cultime(initial_time, delta_t):
    num = len(delta_t)
    t = []
    t.append(initial_time)
    for i in range(num):
        t.append(initial_time + delta_t[:i+1].sum())
    return np.array(t)

def individual(delta_t):
    '''
    Create a member of population
    '''
    return uniform(-0.5, 1, len(delta_t))
        
def population(count, delta_t):
    '''
    Create a number of individuals
    '''
    return np.array([individual(delta_t) for x in xrange(count)])
    
def fitness(info, initial_time, delta_t, individual, target):
    delta_tn = delta_t + individual
    ti = cultime(initial_time, delta_tn)
    # STATE FOR EACH WAYPOINTS
    stat = np.column_stack((info[:,1], info[:,0], ti[:-1]))
    wind_U = weather_info.u(stat) / 0.5144
    wind_V = weather_info.v(stat) / 0.5144
    Hs = weather_info.hs(stat)
    Tp = weather_info.tp(stat)
    head = weather_info.hdg(stat)
    cu = weather_info.cu(stat)
    cv = weather_info.cv(stat)
    # WATER DEPTH
    depth = np.array([bathymetry.water_depth(p) for p in info[:,:2]]).ravel()
    # SPEED ESTIMATION
    vn = info[:,2] / delta_tn / 1.852
    # FUEL CONSUMPTION; OUTPUT :[PE, PS, FUEL/H, FUEL/NM]
    params = zip(vn, info[:,3], cu, cv, depth, wind_U, wind_V, Hs, Tp, head)
    power = np.array([ship_info.weather2fuel(p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7], p[8], p[9]) for p in params])
    fuelc = sum(info[:,2] / 1.852 * power[:,3])
    
    return abs(fuelc - target)

def grade(info, initial_time, delta_t, pop, target):
    summed = sum([fitness(info, initial_time, delta_t, x, target) for x in pop])
    return summed / (len(pop) * 1.0)
    
    
 
    
def evolve(info, initial_time, delta_t, pop, target, retain = 0.2, random_select = 0.05, mutate = 0.01):
    graded = [(fitness(info, initial_time, delta_t, x, target), x) for x in pop]
    graded = [x[1] for x in sorted(graded, key = lambda tup : tup[0])]
    retain_length = int(len(graded) * retain)
    parents = graded[:retain_length]
    
    # RANDOMLY ADD OTHER INDIVIDUALS TO PROMOTE GENETIC DIVERSITY
    for individual in graded[retain_length:]:
        if random_select > rand():
            parents.append(individual)
    
    
    # MUTATE SOME INDIVIDUALS
    for individual in parents:
        if mutate > rand():
            pos_to_mutate = randint(0, len(individual) - 1)
            individual[pos_to_mutate] = uniform(min(individual), max(individual))
    
    
    # CROSSOVER PARENTS TO CREATE CHILDREN
    parents_length = len(parents)
    desired_length = len(pop) - parents_length
    children = []
    while len(children) < desired_length:
        male = randint(0, parents_length - 1)
        female = randint(0, parents_length - 1)
        if male != female:
            male = parents[male]
            female = parents[female]
            half = len(male) / 2
            child = male[:half].tolist() + female[half:].tolist()
            child = np.array(child)
            children.append(child)
    
    parents.extend(children)
    
    
    return np.array(parents)

## departure
#p_dep = np.array([-5.0, 49.0])
## destination
#p_des = np.array([-65.0, 40.0])
## points in great circle
#X,Y = m.gcpoints(p_dep[0], p_dep[1], p_des[0], p_des[1], 40)
#x, y = m(X,Y, inverse = True)
#dist_bearing = []
#
#for i in range(39):
#    dist_bearing.append(greatcircle_inverse(x[i], y[i], x[i+1], y[i+1]))
#    
#dist_bearing = np.array(dist_bearing)    
#info = np.column_stack((x[:-1], y[:-1], dist_bearing))    
#
#
#
#    
#calm_r = ship_info.weather2fuel(20, 0, 0, 0, -10000, 0, 0, 0.01, 0.01, 0)
#minifuelc = calm_r[3] * greatcircle_inverse(p_dep[0], p_dep[1], p_des[0], p_des[1])[0] / 1.852
#minifuelc = 0
#
#
#
#initial_time = 25
#velocity = 20
#delta_t = []
#for i in range(39):
#    delta_t.append(info[i,2] / velocity / 1.852)
#delta_t = np.array(delta_t)
#
#
#
#
### test
#
#p = population(100, delta_t)
#fitness_history = [grade(info, initial_time, delta_t, p, minifuelc)]
#for i in xrange(20):
#    print i
#    p = evolve(info, initial_time, delta_t, p, minifuelc)
#    fitness_history.append(grade(info, initial_time, delta_t, p, minifuelc))
#
#for datum in fitness_history:
#    print datum






#plt.figure(figsize=(20, 15))
#
#m.drawgreatcircle(p_dep[0], p_dep[1], p_des[0], p_des[1], linewidth=2,color='b')
#m.scatter(X, Y, marker='D',color='g')
#m.drawcoastlines()
#m.fillcontinents()
#m.drawparallels(np.arange(-90.,120.,5.), labels=[1,0,0,0], fontsize=15)
#m.drawmeridians(np.arange(-180.,180.,5.), labels=[0,0,0,1], fontsize=15)
#plt.show()





#delta_tnew = delta_t + p[0]
#speed0 = dist_bearing[:,0] / delta_tnew / 1.852
#
#m = Basemap(
#  projection="merc",
#  resolution='l',
#  area_thresh=0.1,
#  llcrnrlon=-75,
#  llcrnrlat=35,
#  urcrnrlon=10,
#  urcrnrlat=55
#)
#
## animation 
#fig = plt.figure(figsize=(20, 15))
#lon, lat = np.meshgrid(weather_info.lon, weather_info.lat)
#x, y = m(lon, lat)
#
#x1, y1 = m(info[:,0], info[:,1])
#it = cultime(initial_time,delta_tnew)
#wt = np.linspace(0, (124 - 1) * 6, 124)
#ani_ind = int(np.argwhere(wt > max(it))[0])
#anj_ind = int(np.argwhere(wt < min(it))[-1])
#
#
#txt = plt.title('', fontsize = 20)
#
#
#m.drawcoastlines()
#m.fillcontinents()
#m.drawparallels(np.arange(-90.,120.,5.), labels=[1,0,0,0], fontsize=15)
#m.drawmeridians(np.arange(-180.,180.,5.), labels=[0,0,0,1], fontsize=15)
#
#def init():
#    cs = m.pcolormesh(x, y, weather_info.Hs[:,:,0], shading='flat', cmap=plt.cm.jet)
#    md = weather_info.Met['Time'][0][0]
#    pd = datetime.fromordinal(int(md)) + timedelta(days=md%1) - timedelta(days = 366)
#    txt.set_text("GA @ Significant wave height at " + str(pd))
#    cb = plt.colorbar(cs, orientation ='horizontal', fraction=0.1,shrink=.5, pad=0.05)
#    cb.ax.tick_params(labelsize=20) 
#    return [cs]
#
#def animate(i):
#    #
#    if i < anj_ind+1:
#        cs = m.pcolormesh(x, y, weather_info.Hs[:,:,i], shading='flat', cmap=plt.cm.jet)
#        return [cs]
##    if i == 0:
##        cs = m.pcolormesh(x, y, weather_info.Hs[:,:,0], shading='flat', cmap=plt.cm.jet)
##        return [cs]
#    cs = m.pcolormesh(x, y, weather_info.Hs[:,:,i], shading='flat', cmap=plt.cm.jet)
#    index = int(max(np.argwhere(it<wt[i])))
#    m.plot(x1[:index + 1],y1[:index + 1] ,marker='o',markersize = 4, linewidth=3, color='#ff0080')
#    md = weather_info.Met['Time'][i][0]
#    pd = datetime.fromordinal(int(md)) + timedelta(days=md%1) - timedelta(days = 366)
#    txt.set_text("GA @ Significant wave height at " + str(pd))
#    return [cs]
#
#anim = animation.FuncAnimation(fig, animate, init_func=init, frames= ani_ind+1, interval=1000, blit=True)
#mywriter = animation.FFMpegWriter(fps=1)
#
#anim.save('GA.mp4', writer=mywriter)






