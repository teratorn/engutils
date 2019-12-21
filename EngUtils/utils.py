# coding=utf-8
from __future__ import division  # this causes interger division to return a floating point (decimal)
                                 # number instead of throwing away the remainder, if any.

from EngUtils.common import CalculatorApp, NotebookPage, CalculatorPage, EntryLine
from EngUtils.common import EntryTable, OutputLine, PROGRAM_VERSION

import os.path

from math import pi, sin, cos, tan, atan, asin, acos


#some constants, there are more at the bottom of this file
class U(object):  #these class attributes are common unit strings for use below
    Inches = "(in)"
    Feet = "(feet)"
    SqFt = "(sq.ft)"
    SqIn = "(sq.in)"
    Acres = "(acres)"
    FtSec = "(ft/sec)"
    FtLinFt = "(ft/lin.ft)"
    InLbs = "(in-lbs)"
    GPM = "(gallons/min)"
    CuFtSec = "(cu.ft/sec)"
    PSI = "(psi)"
    Mins = "(minutes)"
    Percent = "%"
    InHrs = "(in/hrs)"
    DegMinSec = "(ex. 10d20'30\")"
    Degrees = "°"
    Radians = "(Radians)"

pvc_factor = 150

app = CalculatorApp("Engineering Utilities %s" % (PROGRAM_VERSION,))

# ----- Begin Conc. Beam definition -----

# ----- Create ConcBeam calculator function
#called when the Calculate button is clicked, takes a number of arguments
#equal to the number of entry objects defined below
def concBeamCalc(width, dist, bars, dia, moment):
    Asteel = pi * bars * (dia / 2)**2
    Aceq = Asteel * 15
    p = Asteel / width / dist
    k = ( (2 * p * 15) + (p * 15)**2 )**0.5 - (p * 15)
    j = 1 - (k / 3)
    fc = (2 * moment) / (k * j * width * (dist**2))
    fs = moment / (Asteel * j * dist)
    return fc, fs, k*dist, Aceq/dia

# ----- Create the ConcBeam page -----
# General Parameters for the CalculatorPage constructor:
# 1) parent, the notebook widget to attach to
# 2) name, text to display on the tab for this page
# 3) caption, text to display centered at the top of the page
# 4) calculator_function, the function to call when the Calculate button is clicked, it must take a number of parameters
#    equal to the number of entry boxes defined, and it should return a number of parameters equal to the number of output boxes defined.
# 4) entries - variable number of Entry objects
# 5) outputs - variable number of Output objects

CalculatorPage(app.top,
               "ConcBeam",
               "This program calculates the stresses in both the concrete\nand the steel of reinforced concrete beams and footings.",
                concBeamCalc,
                EntryLine("Width of beam:", U.Inches),
                EntryLine("Distance between the top surface of \nbeam and the center of the bottom steel:", U.Inches),
                EntryLine("Number of rebars on the tension side:"),
                EntryLine("Diameter of tension side rebars:", U.Inches),
                EntryLine("Bending moment in the beam or footing:", U.InLbs),

                OutputLine("Maximum compressive stress in concrete:", U.PSI),
                OutputLine("Maximum tensile stress in steel: ", U.PSI),
                OutputLine("Height of concrete above neutral axis: ", U.Inches),
                OutputLine("Width of equivelent concrete,\nw/ the height equal:", U.Inches)
                )
# ----- End Conc. Beam definition -----

nb = NotebookPage(app.top, "PVC Pipes")
def pressureDropCalc(dia, flow, length):
    dia = dia / 12  #convert to feet for calculations
    flow = flow / 7.48052 / 60  #convert to cubic feet per second for calculations
    hf = ((4.727 / (dia**4.87)) * length) * ((flow / pvc_factor)**1.85)
    psi = hf / 2.3114  #based on water density of 62.3 lb./cubic foot @ 70 degrees farenheit
    return psi, hf
CalculatorPage(nb,
               "Pressure Drop",
               "This program calculates the pressure drop in a single run of pipe.\nBased on water density of 62.3 lb./cubic foot @ 70 degrees farenheit.",
                pressureDropCalc,
                EntryLine("Inside pipe diameter:", U.Inches),
                EntryLine("Flow:", U.GPM),
                EntryLine("Length of the pipe:", U.Feet),

                OutputLine("Pressure drop:", U.PSI),
                OutputLine("Head loss:", U.Feet)
                )

def pipeFlowCalc(dia, head_loss, length):
    dia = dia / 12  #convert to feet for calculations
    s = head_loss / length #head loss per foot of pipe
    Q = 0.432 * pvc_factor * (dia ** 2.63) * (s ** 0.54)  #flow in cubic feet per second
    gpm = Q * 7.48052 * 60  #convert flow to gallons per minute
    return gpm
CalculatorPage(nb,
               "Flow",
               "This program calculates the flow in a single run of pipe.",
                pipeFlowCalc,
                EntryLine("Inside pipe diameter:", U.Inches),
                EntryLine("Total head loss in the pipe:", U.Feet),
                EntryLine("Length of the pipe:", U.Feet),

                OutputLine("Flow:", U.GPM)
                )


def pipeDiaCalc(flow, head_loss, length):
    Q = flow / 7.48052 / 60  #change to cubic feet per second
    s = head_loss / length  #head loss per foot of pipe
    dia = (1.376 / (s ** 0.205)) * ((Q / pvc_factor) ** 0.38)
    dia = dia * 12
    return dia
CalculatorPage(nb,
               "Pipe Diameter",
               "This program calculates the diameter of a single run of pipe",
                pipeDiaCalc,
                EntryLine("Total flow:", U.GPM),
                EntryLine("Total head loss in the pipe:", U.Feet),
                EntryLine("Length of the pipe:", U.Feet),

                OutputLine("Inside pipe diameter:", U.Inches)
                )


def drainCalc(K, b, drain_area, runoff_c, runoff_time, drain_length, elev_d, slope, n):
    toriginal = runoff_time
    drain_area = 43560 * drain_area

    while 1:
        #rainfall intensity in in./hour

        I = K / (runoff_time + b)
        #calc. the angle of the stream bank from the slope
        theta = atan(slope / 100)
        #calc. the average width of the drainage area in ft.
        w = drain_area / drain_length
        #calc. the slope "S" of the energy grade line, ft.drop/linear foot of stream
        S = elev_d / drain_length
        #set the value of the sum of the avg. stream velocities to zero
        Vsum = 0
        tsum = 0

        x = 20

        for j in range(x+1)[1:]:
            #calculate the flow at each of 20 points along the stream in order to
            #get an average stream velocity use the eqn. Q=CIA, Std. Hdbk. for Civil Eng.

            Q = (((j / x) * drain_length * w) / 43560) * I * runoff_c

            #calc. the right side of the Manning equation, See Pg.21-47, Std. Hdbk. for Civil Eng., Eqn. 21-83
            right = (Q * n) / (1.486 * (S ** .5))

            #calc. the left side of the Manning equation, See Pg.21-47, Std. Hdbk. for Civil Eng., Eqn. 21-83
            length = 1  #first guess for length
            add = 0.1

            while 1:
                left = ((length ** 2) * sin(theta) * cos(theta)) * (((length / 2) * sin(theta) * cos(theta)) ** (2 / 3))
                tryme = right - left
                if tryme <= 0: break
                length += add

            #calculate the hydraulic radius, R
            R = (length / 2) * sin(theta) * cos(theta)
            #calculate the avg. stream velocity at the current point along the stream
            Vpoint = (1.486 / n) * (R ** (2 / 3)) * (S ** (1 / 2))
            #add Vpoint to the previous values of Vpoint

            Vavgpoint = (Vsum + Vpoint) / 2
            tpoint = (drain_length / 20) / Vavgpoint
            Vsum = Vpoint
            tsum = tsum + tpoint



        if abs(runoff_time - (tsum / 60)) <= .001: break
        runoff_time = tsum / 60


    #calculate the average stream velocity for the entire stream length
    V = drain_length / tsum

    return V, tsum/60, I, K/((tsum/60)+b), I, K, runoff_time, sin(theta)*cos(theta), w, S, Q, right, left, length, R, Vpoint


CalculatorPage(app.top,
               "Drainage",
"""SEE STD. HDBK. FOR CIVIL ENGINEERS, PG.21-9O FOR VALUES OF K & b. We live in Region 2,
but Region 1 is not too far east of us, see the above reference for the appropriate Region.
                               Region 1:           Region 2:                                          Region 1:           Region 2:
For 2 yr storm:    K=206, b=30      K=140, b=21  |  For 25 yr storm:    K=327, b=33      K=260, b=32
For 4 yr storm:    K=247, b=29      K=190, b=25  |  For 50 yr storm:    K=315, b=28      K=350, b=38
For 10 yr storm:  K=300, b=36      K=230, b=29  |  For 100 yr storm:  K=367, b=33      K=375, b=36
""",
                drainCalc,
                EntryLine("Value of K for the appropriate storm frequency:"),
                EntryLine("Value of b for the appropriate storm frequency:"),
                EntryLine("Drainage area:", U.Acres),
                EntryLine("Runoff coefficient:"),
                EntryLine("Estimated runoff time:", U.Mins),
                EntryLine("Length of the drainage area:", U.Feet),
                EntryLine("Elevation difference at ends of the stream:", U.Feet),
                EntryLine("Average side slope of the stream banks:", U.Percent),
                EntryLine("Roughness coefficient for Manning eqn., n:"),

                OutputLine("Average overall stream velocity:", U.FtSec),
                OutputLine("Runoff time:", U.Mins),
                OutputLine("Assumed rainfall intensity:", U.InHrs),
                OutputLine("Rainfall intensity:", U.InHrs),
                OutputLine("I ="),
                OutputLine("K ="),
                OutputLine("t ="),
                OutputLine("sin cos ="),
                OutputLine("w ="),
                OutputLine("S ="),
                OutputLine("Q ="),
                OutputLine("right ="),
                OutputLine("left ="),
                OutputLine("length ="),
                OutputLine("R ="),
                OutputLine("Vpoint =")
                )

nb = NotebookPage(app.top, "Flow Depth")
def flowDepthCalcVchannel(flow, rough_c, grade_line_slope, left_slope, right_slope):

    #calculate the right side of the Manning eqn.
    right = (flow * rough_c) / (1.486 * (grade_line_slope ** .5))

    #calc. angle of left & right stream banks respectively
    theta1 = atan(left_slope / 100)
    theta2 = atan(right_slope / 100)

    d = .001  #first guess for depth
    add = .001

    tryme = 1
    #calc. true length of left and right stream banks respectively
    while tryme > 0:
        d = d + add

        L1 = d / sin(theta1)
        L2 = d / sin(theta2)
        #calc. width of left and right streams respectively
        h1 = d / tan(theta1)
        h2 = d / tan(theta2)
        Atotal = (d / 2) * (h1 + h2)    #total area of stream
        Length = L1 + L2                #total wetted perimeter
        R = Atotal / Length             #hydraulic radius
        #calc. the left side of the Manning eqn., AR^2/3
        left = Atotal * (R ** (2 / 3))

        tryme = right - left

    return right, left, Atotal, flow/Atotal, d, h1, h2


CalculatorPage(nb,
               "V Channel",
               "This program calculates stream-depth among other things.",
                flowDepthCalcVchannel,
                EntryLine("Total flow, Q:", U.CuFtSec),
                EntryLine("Roughness coefficient, n:"),
                EntryLine("Slope of the energy grade line, S:", U.FtLinFt),
                EntryLine("Slope of the left stream bank lkg. upstream:", U.Percent),
                EntryLine("Slope of the right stream bank lkg. upstream:", U.Percent),

                OutputLine("right:"),
                OutputLine("left:"),
                OutputLine("Total stream area:", U.SqFt),
                OutputLine("Average stream velocity:", U.FtSec),
                OutputLine("Total stream depth:", U.Feet),
                OutputLine("Width of the left side of\nthe stream looking upstream:", U.Feet),
                OutputLine("Width of the right side of\nthe stream looking upstream:", U.Feet)
                )

def flowDepthCalcSqchannel(flow, rough_c, grade_line_slope, width):

    #calculate the right side of the Manning eqn.
    right = (flow * rough_c) / (1.486 * (grade_line_slope ** .5))

    d = .001  #first guess for depth
    add = .001

    tryme = 1
    #calculate the area and wetted length for the hydraulic radius
    while tryme > 0:
        d = d + add

        Area = d * width
        Length = (2 * d) + width

        R = Area / Length             #hydraulic radius
        #calc. the left side of the Manning eqn., AR^2/3
        left = Area * (R ** (2 / 3))

        tryme = right - left

    return Area, flow/Area, d

CalculatorPage(nb,
               "Square Channel",
               "This program calculates stream-depth among other things.",
                flowDepthCalcSqchannel,
                EntryLine("Total flow, Q:", U.CuFtSec),
                EntryLine("Roughness coefficient, n:"),
                EntryLine("Slope of the energy grade line, S:", U.FtLinFt),
                EntryLine("Width of channel:", U.Feet),



                OutputLine("Total stream area:", U.SqFt),
                OutputLine("Average stream velocity:", U.FtSec),
                OutputLine("Total stream depth:", U.Feet),
                )

def flowDepthCalcTrapchannel(flow, rough_c, grade_line_slope, left_slope, right_slope, width):

    #calculate the right side of the Manning eqn.
    right = (flow * rough_c) / (1.486 * (grade_line_slope ** .5))

    #calc. angle of left & right stream banks respectively
    theta1 = atan(left_slope / 100)
    theta2 = atan(right_slope / 100)

    d = .001  #first guess for depth
    add = .001

    tryme = 1
    #calc. true length of left and right stream banks respectively
    while tryme > 0:
        d = d + add

        L1 = d / sin(theta1)
        L2 = d / sin(theta2)
        #calc. width of left and right streams respectively
        h1 = d / tan(theta1)
        h2 = d / tan(theta2)
        Atotal = ((d / 2) * (h1 + h2)) + (d * width)    #total area of stream
        Length = L1 + L2 + width                        #total wetted perimeter
        R = Atotal / Length                             #hydraulic radius
        #calc. the left side of the Manning eqn., AR^2/3
        left = Atotal * (R ** (2 / 3))
        ChannelWidthTotal = width + h1 + h2

        tryme = right - left

    return Atotal, flow/Atotal, d, h1, h2, ChannelWidthTotal


CalculatorPage(nb,
               "Trapezoidal Channel",
               "This program calculates stream-depth among other things.",
                flowDepthCalcTrapchannel,
                EntryLine("Total flow, Q:", U.CuFtSec),
                EntryLine("Roughness coefficient, n:"),
                EntryLine("Slope of the energy grade line, S:", U.FtLinFt),
                EntryLine("Slope of the left stream bank lkg. upstream:", U.Percent),
                EntryLine("Slope of the right stream bank lkg. upstream:", U.Percent),
                EntryLine("Width of flat channel bottom:", U.Feet),


                OutputLine("Total stream area:", U.SqFt),
                OutputLine("Average stream velocity:", U.FtSec),
                OutputLine("Total stream depth:", U.Feet),
                OutputLine("Width of the left sloped side of\nthe stream looking upstream:", U.Feet),
                OutputLine("Width of the right sloped side of\nthe stream looking upstream:", U.Feet),
                OutputLine("Total channel width:", U.Feet)
                )


def flowDepthCalcCurbedStreet(Q, n, s, cg, w, ch):


    #This page calculates the depth of flow down a typical curbed street. The street is assumed to be symmetrical about its
    #centerline with an equal amount of flow on each side of center. Street is assumed to have a linear slope downward from the
    #crown to the curb.
    #Q is the total flow, cfs
    #n is the manning roughness coefficient, dimensionless
    #s is the slope of the energy grade line, ft./ft.
    #cg is the grade of the curb in cross-section, %
    #w is the width of the street between curbs, ft.
    #ch is the crown height at the street centerline, ft.
    #The equation to be used is: Q = 1.486 x A x R^2/3 x s^1/2 / n
    #The depth "d" will be increased by 0.001 ft. per try until the right side of the equation balances with "Q"

    d = .001    #first guess for depth
    add = .001  #step value for each try

    tryme = 1   # set initial value

    while tryme > 0:

        d = d + add

        sg = 100 * (ch / (w / 2))                      #street grade from crown to curb in %
        a = 100 * d / cg                               #horizontal projected length of wetted curb on one side of the street
        wct = 2 * (((d ** 2) + (a ** 2)) ** (1 / 2))   #calculaction of the total wetted curb on both sides of street

        if d <= ch:
            b = 100 * d / sg                               #horizontal projected length of wetted street on one side of the street
            wst = 2 * (((d ** 2) + (b ** 2)) ** (1 / 2))   #calculation of the total wetted street on both sides of street when d <= ch
            A = (d * a) + (d * b)                          #calculation of total cross-sectional area of flow when d <= ch

        else:
            wst = 2 * (((ch ** 2) + ((w / 2) ** 2)) ** (1 / 2))   #calculation of the total wetted street on both sides of street when d > ch
            A = (d * a) + (w * (d - (ch / 2)))                    #calculation of total cross-sectional area of flow when d > ch

        wpt = wct + wst    #total wetted perimeter, curbs and street
        R = A / wpt        #calculation of hydraulic radius
        right = (1.486 * A) * (R ** (2 / 3)) * (s ** (1 / 2)) / n   #calculation of right side of equation for Q shown in the explanation above
        V = Q / A                                                   #calculation of average stream velocity

        tryme = Q - right

    return d, A, V

CalculatorPage(nb,
               "Curbed Street",
               "This program assumes a linear street slope from crown to curb.",
               flowDepthCalcCurbedStreet,
               EntryLine("Total flow, Q:", U.CuFtSec),
               EntryLine("Roughness coefficient, n:"),
               EntryLine("Slope of the energy grade line, S:", U.FtLinFt),
               EntryLine("Grade of curbs:", U.Percent),
               EntryLine("Width of street between curbs:", U.Feet),
               EntryLine("Street crown height:", U.Feet),


               OutputLine("Total stream depth:", U.Feet),
               OutputLine("Total stream area:", U.SqFt),
               OutputLine("Average stream velocity:", U.FtSec)
               )



def flowDepthCalcUchannel(Q, n, s, rad):

    #This page calculates the flow depth of a "U" shaped channel.  The channel cross-section has a
    #semicircular bottom and vertical side walls.
    #Q is the total flow, cfs.
    #n is the manning roughness coefficient, dimensionless
    #s is the slope of the energy grade line, ft./ft.
    #rad is the radius of the hemispherical bottom of the channel cross-section, ft.
    # The equation to be used is: Q = 1.486 x A x R^2/3 x s^1/2 / n

    d = .001
    add = .001
    tryme = 1

    while tryme > 0:

        d = d + add

        if d <= rad:
            theta = acos((rad - d) / rad)
            asec = theta * (rad ** 2)
            at = (rad * sin(theta)) * (rad - d)
            A = asec - at                                #Total flow area if water depth is <= radius of channel bottom
            wpt = 2 * theta * rad                      # Total wetted perimeter if water depth is <= radius of channel bottom

        else:
            A = ((pi * (rad ** 2)) / 2) + ((d - rad) * (2 * rad))     #Total flow area if water depth > radius of channel bottom
            wpt = (pi * rad) + (2 * (d - rad))                        #Total wetted perimeter if water depth > radius of channel bottom

        R = A / wpt
        right = (1.486 * A) * (R ** (2 / 3)) * (s ** (1 / 2)) / n    # calculation of right side of equation for Q shown in the explanation above
        V = Q / A                                                    # calculation of average stream velocity
        tryme = Q - right

    return d, A, V

CalculatorPage(nb,
               "U Shaped Channel",
               "For a channel with a semicircular bottom and vertical side walls",
               flowDepthCalcUchannel,
               EntryLine("Total flow, Q:", U.CuFtSec),
               EntryLine("Roughness coefficient, n:"),
               EntryLine("Slope of the energy grade line, S:", U.FtLinFt),
               EntryLine("Radius of channel bottom:", U.Feet),


               OutputLine("Total stream depth:", U.Feet),
               OutputLine("Total stream area:", U.SqFt),
               OutputLine("Average stream velocity:", U.FtSec)
               )


def flowDepthCalcCircularChan(Q, n, s, rad):

    #This page calculates the flow depth for a circular closed channel flowing partially full.
    # Q is the total flow, cfs.
    # n is the manning roughness coefficient, dimensionless
    # s is the slope of the energy grade line, ft./ft.
    # rad is the inside radius of the channel cross-section, ft.
    # The equation to be used is: Q = 1.486 x A x R^2/3 x s^1/2 / n

    theta = 0.0001
    add = 0.00001
    tryme = 1

    while tryme > 0:

        theta = theta + add

        if theta > 3.141592654:
            raise ValueError("Depth of water exceeds diameter of channel")

        A = (rad ** 2) * (theta - (sin(theta) * cos(theta)))

        d = rad * (1 - cos(theta))
        wpt = 2 * theta * rad
        R = A / wpt
        V = Q / A
        right = (1.486 * A) * (R ** (2 / 3)) * (s ** (1 / 2)) / n
        tryme = Q - right

    return d, A, V

CalculatorPage(nb,
               "Circular Channel",
               "For channel with circular cross-section.\nResults not valid if depth exceeds channel diameter",
               flowDepthCalcCircularChan,
               EntryLine("Total flow, Q:", U.CuFtSec),
               EntryLine("Roughness coefficient, n:"),
               EntryLine("Slope of the energy grade line, S:", U.FtLinFt),
               EntryLine("Inside radius of channel:", U.Feet),


               OutputLine("Total stream depth:", U.Feet),
               OutputLine("Total stream area:", U.SqFt),
               OutputLine("Average stream velocity:", U.FtSec)
               )



def latLonCalc(lat1, lon1, lat2, lon2):

    lataverage = (lat1 + lat2) / 2

    longradius = 20925722.4 * cos((pi / 180) * lataverage)

    latdist = 2 * (20855551.2 * sin(((lat2 - lat1) * (pi / 180)) / 2))
    longdist = 2 * (longradius * sin(((lon1 - lon2) * (pi / 180)) / 2))

    distance = ((latdist ** 2) + (longdist ** 2)) ** 0.5

    if latdist == 0 and longdist == 0:
        bearing = 0
    elif longdist == 0 and latdist > 0:
        bearing = 0
    elif latdist == 0 and longdist > 0:
        bearing = 90
    elif longdist == 0 and latdist < 0:
        bearing = 180
    elif latdist == 0 and longdist < 0:
        bearing = 270
    else:
        angle = (180 * atan(abs(latdist) / abs(longdist))) / pi

        if latdist > 0 and longdist > 0:
            bearing = 90 - angle
        if latdist < 0 and longdist > 0:
            bearing = 90 + angle
        if latdist < 0 and longdist < 0:
            bearing = 270 - angle
        if latdist > 0 and longdist < 0:
            bearing = 270 + angle

    return distance, bearing

CalculatorPage(app.top,
               "Lat / Lon",
               "This program calculates the distance and direction between two GPS points.",
                latLonCalc,
                EntryLine("Latitude of the Origin site:", U.DegMinSec),
                EntryLine("Longitued of the Origin site:", U.DegMinSec),
                EntryLine("Latitude of the Destination site:", U.DegMinSec),
                EntryLine("Longitude of the Destination site:", U.DegMinSec),

                OutputLine("The distance between points:", U.Feet),
                OutputLine("The bearing from origin to destination:", U.Degrees)
                )



nb = NotebookPage(app.top, "Inertia")

def rectPlateCalc(entry_table):
    Io = a = ay = ay2 = 0
    for y, width, height in entry_table:
        a = a + (width * height)
        ay = ay + ((width * height) * y)
        ay2 = ay2 + ((width * height) * (y ** 2))
        Io = Io + ((width * (height ** 3)) / 12)

    Ybar = ay / a
    Ix = ay2 + Io - (a * (Ybar ** 2))

    return a,Ybar,Ix
CalculatorPage(nb,
               "Rectangular",
               "Rectangular plate elements, all horizontal & vertical",
               rectPlateCalc,
               EntryTable("Enter the Elements. One for each row.", "Y", "width", "height"),

               OutputLine("Area = "),
               OutputLine("Ybar = "),
               OutputLine("Ix = ")
               )

def irregElemCalc(entry_table):
    ay = a = ay2 = Io = Io1 = 0
    for y, area, Io1 in entry_table:

        ay = ay + (area * y)
        a = a + area
        ay2 = ay2 + (area * (y ** 2))
        Io = Io + Io1

    Ybar = ay / a
    Ix = ay2 + Io - (a * (Ybar ** 2))
    return a, Ybar, Ix
CalculatorPage(nb,
               "Irregular",
               "Irregular elements including plates at an angle",
               irregElemCalc,
               EntryTable("Enter the Elements. One for each row.", "Y", "area", "Io"),

               OutputLine("Area = "),
               OutputLine("Ybar = "),
               OutputLine("Ix = ")
               )

def angledPlateCalc(thick, len, angle):
    angle = 0.01745 * angle
    Io = ((thick * (len ** 3) * (sin(angle) ** 2)) / 12) + (((thick ** 3) * len * (cos(angle) ** 2)) / 12)
    if angle == 0:
        y = thick / 2
    # TODO XXX FIXME - comparing floats like this doesn't work
    elif angle == 1.5705:
        y = len / 2
    else:
        y = ((len / 2) + ((thick / 2) / (tan(angle)))) * sin(angle)

    return thick*len, y, Io

CalculatorPage(nb,
               "Angled",
               "Calculator for angled plate elements",
               angledPlateCalc,
               EntryLine("Thickness of the element: "),
               EntryLine("Length of the element: "),
               EntryLine("Angle between the centerline\nof the element and horizontal: ", U.Degrees),

               OutputLine("Area = "),
               OutputLine("Y from the lowest corner\nof the angled plate = "),
               OutputLine("Using Io = "),
               )



nb_known = NotebookPage(nb, "Known Shapes")


def iBeamCalc(height, u_width, u_thick, l_width, l_thick, web_thick):


    a1 = [ height - (u_thick / 2), ((height - u_thick - l_thick) / 2) + l_thick, l_thick / 2 ]
    a2 = [ u_width, web_thick, l_width ]
    a3 = [ u_thick, height - u_thick - l_thick, l_thick ]

    a = ay = ay2 = Io = Ybar = Ix = 0

    for i in range(3):
        a = a + ( a2[i] * a3[i] )
        ay = ay + ( ( a2[i] * a3[i] ) * a1[i] )
        ay2 = ay2 + ( ( a2[i] * a3[i] ) * ( a1[i] ** 2 ) )
        Io = Io + ( ( a2[i] * ( a3[i] ** 3 )) / 12)


    Ybar = ay / a
    Ix = ay2 + Io - (a * (Ybar ** 2))

    return a, Ybar, Ix


CalculatorPage(nb_known,
               "I-Beam Sect.",
               "",
               iBeamCalc,
               EntryLine("Overall height of the section:"),
               EntryLine("Width of upper flange:"),
               EntryLine("Thickness of upper flange:"),
               EntryLine("Width of lower flange:"),
               EntryLine("Thickness of lower flange:"),
               EntryLine("Thickness of web:"),

               OutputLine("Area = "),
               OutputLine("Ybar = "),
               OutputLine("Ix = ")
               )


def cSectionCalc(height, u_width, u_thick, l_width, l_thick, web_thick):

    a1 = [ height - (u_thick / 2), ((height - u_thick - l_thick) / 2) + l_thick, l_thick / 2 ]
    a2 = [ u_width, web_thick, l_width ]
    a3 = [ u_thick, height - u_thick - l_thick, l_thick ]

    a = ay = ay2 = Io = Ybar = Ix = 0

    for i in range(3):
        a = a + ( a2[i] * a3[i] )
        ay = ay + ( ( a2[i] * a3[i] ) * a1[i] )
        ay2 = ay2 + ( ( a2[i] * a3[i] ) * ( a1[i] ** 2 ) )
        Io = Io + ( ( a2[i] * ( a3[i] ** 3 )) / 12)


    Ybar = ay / a
    Ix = ay2 + Io - (a * (Ybar ** 2))

    return a, Ybar, Ix


CalculatorPage(nb_known,
               "C Sect.",
               "",
               cSectionCalc,
               EntryLine("Overall height of the section:"),
               EntryLine("Width of upper flange:"),
               EntryLine("Thickness of upper flange:"),
               EntryLine("Width of lower flange:"),
               EntryLine("Thickness of lower flange:"),
               EntryLine("Thickness of web:"),

               OutputLine("Area = "),
               OutputLine("Ybar = "),
               OutputLine("Ix = ")
               )


def angledSectionCalc(v_length, v_thick, h_length, h_thick):

    a = ay = ay2 = Io = Ybar = Ix = 0

    a1 = [ v_length / 2, h_thick / 2 ]
    a2 = [ v_thick, h_length - v_thick ]
    a3 = [ v_length, h_thick ]

    for i in range(2):
        a = a + ( a2[i] * a3[i] )
        ay = ay + (( a2[i] * a3[i] ) * a1[i] )
        ay2 = ay2 + (( a2[i] * a3[i] ) * ( a1[i] ** 2 ))
        Io = Io + (( a2[i] * ( a3[i] ** 3 )) / 12)

    Ybar = ay / a
    Ix = ay2 + Io - (a * (Ybar ** 2))

    return a, Ybar, Ix

CalculatorPage(nb_known,
               "Angle Sect.",
               "",
               angledSectionCalc,
               EntryLine("Overall length of vertical flange:"),
               EntryLine("Thickness of vertical flange:"),
               EntryLine("Overall length of horizontal flange:"),
               EntryLine("Thickness of horizontal flange:"),

               OutputLine("Area = "),
               OutputLine("Ybar = "),
               OutputLine("Ix = ")
               )


def rectTubeCalc(height, width, thick):

    a1 = [ height - (thick / 2), height/2, height/2, thick/2 ]
    a2 = [ width - (2 * thick), thick, thick, width - (2 * thick) ]
    a3 = [ thick, height, height, thick ]

    a = ay = ay2 = Io = Ybar = Ix = 0

    for i in range(4):
        a = a + ( a2[i] * a3[i] )
        ay = ay + (( a2[i] * a3[i] ) * a1[i] )
        ay2 = ay2 + (( a2[i] * a3[i] ) * ( a1[i] ** 2))
        Io = Io + (( a2[i] * ( a3[i] ** 3)) / 12)

    Ybar = ay / a
    Ix = ay2 + Io - (a * (Ybar ** 2))

    return a, Ybar, Ix


CalculatorPage(nb_known,
               "Rect. Tube",
               "",
               rectTubeCalc,
               EntryLine("Overall height of the tube:"),
               EntryLine("Overall width of the tube:"),
               EntryLine("Wall thickness of the tube:"),

               OutputLine("Area = "),
               OutputLine("Ybar = "),
               OutputLine("Ix = ")
               )


def roundTubeCalc(dout, thick):
    a = Ybar = Ix = 0
    din = dout - (2 * thick)
    ro = dout / 2
    ri = din / 2
    a = pi * ((ro ** 2) - (ri ** 2))
    Ybar = dout / 2
    Ix = (pi / 64) * ((dout ** 4) - (din ** 4))

    return a, Ybar, Ix

CalculatorPage(nb_known,
               "Round Tube",
               "",
               roundTubeCalc,
               EntryLine("Outside diameter of the tube:"),
               EntryLine("Wall thickness of the tube:"),

               OutputLine("Area = "),
               OutputLine("Ybar = "),
               OutputLine("Ix = ")
               )


def roundBarCalc(dia):
    a = Ybar = Ix = 0
    r = dia / 2
    a = pi * (r ** 2)
    Ybar = dia / 2
    Ix = (pi / 64) * (dia ** 4)

    return a, Ybar, Ix

CalculatorPage(nb_known,
               "Round Bar",
               "",
               roundBarCalc,
               EntryLine("Diameter of the round bar:"),

               OutputLine("Area = "),
               OutputLine("Ybar = "),
               OutputLine("Ix = ")
               )


def bendingCalc(moment, dist, Ix):
    return (moment * dist) / Ix

CalculatorPage(nb,
               "Bending",
               "Calculate Bending",
               bendingCalc,
               EntryLine("Bending moment:"),
               EntryLine("Distance from N.A.\nto extreme fiber:"),
               EntryLine("Ix = "),

               OutputLine("fb = ", U.PSI)
               )


#called when the Calculate button is clicked, takes a number of arguments
#equal to the number of entry objects defined below
def circularCulvertCalc(a, b, c):
    return a+b+c, 50



# General Parameters for the CalculatorPage constructor:
# 1) parent, the notebook widget to attach to
# 2) name, text to display on the tab for this page
# 3) caption, text to display centered at the top of the page
# 4) calculator_function, the function to call when the Calculate button is clicked, it must take a number of parameters
#    equal to the number of entry boxes defined, and it should return a number of parameters equal to the number of output boxes defined.
# 4) entries - variable number of Entry objects
# 5) outputs - variable number of Output objects

CalculatorPage(app.top,
               "Culvert",
               "blah blah blah",
                circularCulvertCalc,
                EntryLine("a", "a units"),
                EntryLine("b", U.Inches),
                EntryLine("c"),

                OutputLine("d"),
                OutputLine("e")
                )
# ----- End Conc. Beam definition -----


def run():
    app.exec_() # this function never returns until the program is terminated

