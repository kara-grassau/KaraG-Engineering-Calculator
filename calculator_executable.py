# This file fills the needed design values and outputs a list of variables.
# It also provides a final check that requirements are met.
from math import sqrt, log10;
from flask import Flask, request, render_template


app = Flask(__name__)

@app.route('/')
def landingform():
    return render_template('landing.html')
    #return render_template('webpage.html')

@app.route('/unit_check', methods=['POST'])
def unit_check():
    unit_system = request.form.get('unit_system')

    if unit_system == 'customary':
        return render_template('webpage_cust.html')
    elif unit_system == 'si':
        return render_template('webpage_si.html')
    else:
        return render_template('landing.html')

@app.route('/calculate_si', methods=['POST'])
def calculate_si():
    try:
        G = float(request.form['G'])  ## USER INPUT Diameter at location of gasket load reactions (mm)
        P = float(request.form['P'])  ## USER INPUT Internal design pressure (bar)
        m = float(request.form['m'])  ## USER INPUT Gasket factor (Table 2-5.1)
        b = float(request.form['b'])  ## USER INPUT Effective gasket or joint-contact-surface seating width (mm)
        Wm1 = ((0.785*(G**2)*P) + (2*b*3.14*G*m*P))/10  ## Min req bolt load for gasket seating 

        y = float(request.form['y'])  ## USER INPUT Gasket or joint-contact-surface unit seating load
        Wm2 = 3.14*b*G*y  ## Min initial bolt load required for seating

        Ab = float(request.form['Ab'])  ## USER INPUT Actual cross sectional area of bolts (mm)
        Sa = float(request.form['Sa'])  ## USER INPUT Allowable bolt stress at atmospheric temperature (N/mm^2)
        Sb = float(request.form['Sb'])  ## USER INPUT Allowable bolt stress at design temperature (N/mm^2)
        Am1 = Wm1/Sb
        Am2 = Wm2/Sa
        if Am1 > Am2:
            Am = Am1
        else:
            Am = Am2

        a = float(request.form['a'])  ## USER INPUT Nominal bolt diameter (mm)
        t = float(request.form['t'])  ## USER INPUT Flange thickness (mm)
        Bs_max = (2*a)+((6*t)/(m+0.5))  ## Maximum bolt spacing (mm)

        C = float(request.form['C'])  ## USER INPUT Bolt circle diameter (mm)
        n = float(request.form['n'])  ## USER INPUT Num bolts
        Bs = 3.14 * (C/n)  ## Bolt spacing (mm)

        if ((2*a)+t) < Bs:
            Bsc = sqrt(Bs / ((2*a)+t))  ## Bolt spacing correction factor

        Wo = Wm1  ## Bolt load used in flange design for operating conditions
        Wg = (Am + Ab) * (Sa/2)  ## Bolt load used in flange design for gasket seating

        B = float(request.form['B'])  ## USER INPUT Inside diameter of flange (mm)
        H_D = 0.785*(B**2)*P*(1/10)  ## Hydrostatic end force on area inside of flange (N)
        h_D = float(request.form['h_D'])  ## USER INPUT Radial distance from the bolt circle on which H_D acts (mm)
        M_D = H_D * h_D * 0.001 ## Moment due to H_D (J)

        H = 0.785*(G**2)*(P)*(1/10)  ## Hydrostatic end force (N)
        H_P = 2*b*3.14*G*m*P*(1/10)  ## Joint-contact surface compression load (N)

        H_T = H - H_D  ## (N)
        h_T = float(request.form['h_T'])  ## USER INPUT Radial distance (mm)
        M_T = H_T * h_T * 0.001 ## Moment due to H_T (J)

        H_G = Wm1 - H  ## Gasket load (N)
        h_G = (C-G)*(1/2)  ## Radial distance from gasket to circle (mm)
        M_G = H_G * h_G * 0.001 ## Moment due to gasket load (J)

        Moo = M_D + M_G + M_T  ## Total moment operating (J)
        Mog = Wg*(C-G)*(1/2)*0.001 ## Total moment gasket (J)

        F = float(request.form['F'])  ## USER INPUT Factor (Fig 2-7.2)
        g0 = float(request.form['g0'])  ## USER INPUT Small hub thickness (mm)

        h0 = sqrt(B*g0)  ## Factor (mm)
        e = F/h0  ## Factor (1/mm)

        A = float(request.form['A'])  ## USER INPUT Outside diameter of flange (mm)
        K = A/B  ## Ratio of outside to inside diameter

        T = ((K**2)*(1 + (8.55246*log10(K))) - 1) / ((1.04720 + (1.9448*(K**2)))*(K-1))  ## Factor (Fig 2-7.1)
        U = ((K**2)*(1 + (8.55246*log10(K))) - 1) / ((1.36136)*(K**2 - 1)*(K-1))  ## Factor (Fig 2-7.1)
        V = float(request.form['V']) ## USER INPUT Factor (Fig 2-7.3)
        d = (U/V) * h0 * (g0**2)  ## Factor (mm)
        L = (((t*e)+1)/T) + (t**3/d)  ## Factor

        g1 = float(request.form['g1'])  ## USER INPUT Large hub thickness at back of flange (mm)
        f = float(request.form['f'])  ## USER INPUT Stress correction factor (Fig 2-7.6)

        S_Ho = (f*Moo*1000) / (L*(g1**2)*B)  ## Long hub stress at operating (N/mm^2)
        S_Hg = (f*Mog*1000) / (L*(g1**2)*B)  ## Long hub stress at gasket seating (N/mm^2)

        S_Ro = ((1.33*t*e + 1)*Moo*1000) / (L*(t**2)*B)  ## Radial flange stress at operating (N/mm^2)
        S_Rg = ((1.33*t*e + 1)*Mog*1000) / (L*(t**2)*B)  ## Radial flange stress at gasket seating (N/mm^2)

        Z = (K**2 + 1) / (K**2 - 1)  ## Factor (Fig 2-7.1)
        Y = (1/(K-1)) * (0.66845 + (5.71690*((K**2 * log10(K)) / (K**2 - 1))))  ## Factor (Fig 2-7.1)

        S_To = ((Y*Moo*1000) / ((t**2)*B)) - (Z*S_Ro)  ## Tangential flange stress at operating (N/mm^2)
        S_Tg = ((Y*Mog*1000) / ((t**2)*B)) - (Z*S_Rg)  ## Tangential flange stress at gasket seating (N/mm^2)

        Sfo = float(request.form['Sfo'])  ## USER INPUT Allowable design stress at operating conditions for material (UG-23) (N/mm^2)
        Sfg = float(request.form['Sfg'])  ## USER INPUT Allowable design stress at gasket seating for material (UG-23) (N/mm^2)

        return f'''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Flange Design Calculator</title>
            </head>
            <body>
                <h1>Flange Design Calculator</h1>
                <p>Minimum required bolt load for gasket seating (Wm1) = {Wm1} N</p>
                <p>Minimum initial bolt load for gasket seating (Wm2) = {Wm2} N</p>
                <p>Current cross-sectional area of bolts (Ab) = {Ab} mm</p>
                <p>Total required cross-sectional area of bolts (Am) = {Am} mm^2</p>
                <p>{'APPROVED: ' if Ab > Am else 'FAILED: '} The cross-sectional area of the bolts is {'greater than' if Ab > Am else 'NOT greater than'} the minimum required.</p>
                <p>Maximum bolt spacing (Bs_max) = {Bs_max} mm</p>
                <p>Current bolt spacing (Bs) = {Bs} mm</p>
                <p>Bolt spacing required correction factor (Bsc) = {Bsc} </p>
                <p>{'APPROVED: ' if Bs < Bs_max else 'FAILED: '} The bolt spacing is {'less than' if Bs < Bs_max else 'greater than'} the maximum allowable.</p>
                <p>Bolt load used in flange design for operating conditions (Wo) = {Wo} N</p>
                <p>Bolt load used in flange design for gasket seating (Wg) = {Wg} N</p>
                <p>Total moment acting on flange for operating conditions (Moo) = {Moo} J</p>
                <p>Total moment acting on flange for gasket seating (Mog) = {Mog} J</p>
                <p>Longitudinal hub stress at operating conditions (S_Ho) = {S_Ho} N/mm^2</p>
                <p>{'APPROVED: ' if S_Ho < (1.5*Sfo) else 'FAILED: '} Longitudinal hub stress at operating conditions is {'less than' if S_Ho < (1.5*Sfo) else 'greater than'} the maximum allowable.</p>
                <p>Longitudinal hub stress at gasket seating (S_Hg) = {S_Hg} N/mm^2</p>
                <p>{'APPROVED: ' if S_Hg < (1.5*Sfg) else 'FAILED: '} Longitudinal hub stress at gasket seating is {'less than' if S_Hg < (1.5*Sfg) else 'greater than'} the maximum allowable.</p>
                <p>Raidal flange stress at operating conditions (S_Ro) = {S_Ro} N/mm^2</p>
                <p>{'APPROVED: ' if S_Ro < Sfo else 'FAILED: '} Radial flange stress at operating conditions is {'less than' if S_Ro < Sfo else 'greater than'} the maximum allowable.</p>
                <p>Radial flange stress at gasket seating (S_Rg) = {S_Rg} N/mm^2</p>
                <p>{'APPROVED: ' if S_Rg < Sfg else 'FAILED: '} Radial flange stress at gasket seating is {'less than' if S_Rg < Sfg else 'greater than'} the maximum allowable.</p>
                <p>Tangential flange stress at operating conditions (S_To) = {S_To} N/mm^2</p>
                <p>{'APPROVED: ' if S_To < Sfo else 'FAILED: '} Tangential flange stress at operating conditions is {'less than' if S_To < Sfo else 'greater than'} the maximum allowable.</p>
                <p>Tangential flange stress at gasket seating (S_Tg) = {S_Tg} N/mm^2</p>
                <p>{'APPROVED: ' if S_Tg < Sfg else 'FAILED: '} Tangential flange stress at gasket seating is {'less than' if S_Tg < Sfg else 'greater than'} the maximum allowable.</p>
                <p>{'APPROVED: ' if ((S_Ho+S_Ro)/2 < Sfo) else 'FAILED: '} The average of longitudinal and radial flange stresses at operating conditions is {'less than' if ((S_Ho+S_Ro)/2 < Sfo) else 'greater than'} the maximum allowable.</p>
                <p>{'APPROVED: ' if ((S_Hg+S_Rg)/2 < Sfg) else 'FAILED: '} The average of longitudinal and radial flange stresses at gasket seating is {'less than' if ((S_Hg+S_Rg)/2 < Sfg) else 'greater than'} the maximum allowable.</p>
                <p>{'APPROVED: ' if ((S_Ho+S_To)/2 < Sfo) else 'FAILED: '} The average of longitudinal and tangential flange stresses at operating conditions is {'less than' if ((S_Ho+S_To)/2 < Sfo) else 'greater than'} the maximum allowable.</p>
                <p>{'APPROVED: ' if ((S_Hg+S_Tg)/2 < Sfg) else 'FAILED: '} The average of longitudinal and tangential flange stresses at gasket seating is {'less than' if ((S_Hg+S_Tg)/2 < Sfg) else 'greater than'} the maximum allowable.</p>
            </body>
            </html>
        '''
    except Exception as e:
        return f'''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Flange Design Calculator</title>
            </head>
            <body>
                <h1>Flange Design Calculator</h1>
                <p>There was an error during the execution. Please check your input.</p>
            </body>
            </html>


        '''
    
@app.route('/calculate_customary', methods=['POST'])
def calculate_customary():
    try:
        G = float(request.form['G'])  ## USER INPUT Diameter at location of gasket load reactions (in)
        P = float(request.form['P'])  ## USER INPUT Internal design pressure (psi)
        m = float(request.form['m'])  ## USER INPUT Gasket factor (Table 2-5.1)
        b = float(request.form['b'])  ## USER INPUT Effective gasket or joint-contact-surface seating width (in)
        Wm1 = ((0.785*(G**2)*P) + (2*b*3.14*G*m*P))  ## Min req bolt load for gasket seating 

        y = float(request.form['y'])  ## USER INPUT Gasket or joint-contact-surface unit seating load
        Wm2 = 3.14*b*G*y  ## Min initial bolt load required for seating

        Ab = float(request.form['Ab'])  ## USER INPUT Actual cross sectional area of bolts (in)
        Sa = float(request.form['Sa'])  ## USER INPUT Allowable bolt stress at atmospheric temperature (psi)
        Sb = float(request.form['Sb'])  ## USER INPUT Allowable bolt stress at design temperature (psi)
        Am1 = Wm1/Sb
        Am2 = Wm2/Sa
        if Am1 > Am2:
            Am = Am1
        else:
            Am = Am2

        a = float(request.form['a'])  ## USER INPUT Nominal bolt diameter (in)
        t = float(request.form['t'])  ## USER INPUT Flange thickness (in)
        Bs_max = (2*a)+((6*t)/(m+0.5))  ## Maximum bolt spacing (in)

        C = float(request.form['C'])  ## USER INPUT Bolt circle diameter (in)
        n = float(request.form['n'])  ## USER INPUT Num bolts
        Bs = 3.14 * (C/n)  ## Bolt spacing (in)

        if ((2*a)+t) < Bs:
            Bsc = sqrt(Bs / ((2*a)+t))  ## Bolt spacing correction factor

        Wo = Wm1  ## Bolt load used in flange design for operating conditions
        Wg = (Am + Ab) * (Sa/2)  ## Bolt load used in flange design for gasket seating

        B = float(request.form['B'])  ## USER INPUT Inside diameter of flange (in)
        H_D = 0.785*(B**2)*P  ## Hydrostatic end force on area inside of flange (lb)
        h_D = float(request.form['h_D'])  ## USER INPUT Radial distance from the bolt circle on which H_D acts (in)
        M_D = H_D * h_D * (1/12) ## Moment due to H_D (ft-lb)

        H = 0.785*(G**2)*(P)  ## Hydrostatic end force (lb)
        H_P = 2*b*3.14*G*m*P  ## Joint-contact surface compression load (lb)

        H_T = H - H_D  ## (lb)
        h_T = float(request.form['h_T'])  ## USER INPUT Radial distance (in)
        M_T = H_T * h_T * (1/12) ## Moment due to H_T (ft-lb)

        H_G = Wm1 - H  ## Gasket load (lb)
        h_G = (C-G)*(1/2)  ## Radial distance from gasket to circle (in)
        M_G = H_G * h_G * (1/12) ## Moment due to gasket load (ft-lb)

        Moo = M_D + M_G + M_T  ## Total moment operating (ft-lb)
        Mog = Wg*(C-G)*(1/2)*(1/12) ## Total moment gasket (ft-lb)

        F = float(request.form['F'])  ## USER INPUT Factor (Fig 2-7.2)
        g0 = float(request.form['g0'])  ## USER INPUT Small hub thickness (in)

        h0 = sqrt(B*g0)  ## Factor (in)
        e = F/h0  ## Factor (1/in)

        A = float(request.form['A'])  ## USER INPUT Outside diameter of flange (in)
        K = A/B  ## Ratio of outside to inside diameter

        T = ((K**2)*(1 + (8.55246*log10(K))) - 1) / ((1.04720 + (1.9448*(K**2)))*(K-1))  ## Factor (Fig 2-7.1)
        U = ((K**2)*(1 + (8.55246*log10(K))) - 1) / ((1.36136)*(K**2 - 1)*(K-1))  ## Factor (Fig 2-7.1)
        V = float(request.form['V']) ## USER INPUT Factor (Fig 2-7.3)
        d = (U/V) * h0 * (g0**2)  ## Factor (in)
        L = (((t*e)+1)/T) + (t**3/d)  ## Factor

        g1 = float(request.form['g1'])  ## USER INPUT Large hub thickness at back of flange (in)
        f = float(request.form['f'])  ## USER INPUT Stress correction factor (Fig 2-7.6)

        S_Ho = (f*Moo*12) / (L*(g1**2)*B)  ## Long hub stress at operating (psi)
        S_Hg = (f*Mog*12) / (L*(g1**2)*B)  ## Long hub stress at gasket seating (psi)

        S_Ro = ((1.33*t*e + 1)*Moo*12) / (L*(t**2)*B)  ## Radial flange stress at operating (psi)
        S_Rg = ((1.33*t*e + 1)*Mog*12) / (L*(t**2)*B)  ## Radial flange stress at gasket seating (psi)

        Z = (K**2 + 1) / (K**2 - 1)  ## Factor (Fig 2-7.1)
        Y = (1/(K-1)) * (0.66845 + (5.71690*((K**2 * log10(K)) / (K**2 - 1))))  ## Factor (Fig 2-7.1)

        S_To = ((Y*Moo*12) / ((t**2)*B)) - (Z*S_Ro)  ## Tangential flange stress at operating (psi)
        S_Tg = ((Y*Mog*12) / ((t**2)*B)) - (Z*S_Rg)  ## Tangential flange stress at gasket seating (psi)

        Sfo = float(request.form['Sfo'])  ## USER INPUT Allowable design stress at operating conditions for material (UG-23) (psi)
        Sfg = float(request.form['Sfg'])  ## USER INPUT Allowable design stress at gasket seating for material (UG-23) (psi)

        return f'''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Flange Design Calculator</title>
            </head>
            <body>
                <h1>Flange Design Calculator</h1>
                <p>Minimum required bolt load for gasket seating (Wm1) = {Wm1} lbf</p>
                <p>Minimum initial bolt load for gasket seating (Wm2) = {Wm2} lbf</p>
                <p>Current cross-sectional area of bolts (Ab) = {Ab} in</p>
                <p>Total required cross-sectional area of bolts (Am) = {Am} in^2</p>
                <p>{'APPROVED: ' if Ab > Am else 'FAILED: '} The cross-sectional area of the bolts is {'greater than' if Ab > Am else 'NOT greater than'} the minimum required.</p>
                <p>Maximum bolt spacing (Bs_max) = {Bs_max} in</p>
                <p>Current bolt spacing (Bs) = {Bs} in</p>
                <p>Bolt spacing required correction factor (Bsc) = {Bsc} </p>
                <p>{'APPROVED: ' if Bs < Bs_max else 'FAILED: '} The bolt spacing is {'less than' if Bs < Bs_max else 'greater than'} the maximum allowable.</p>
                <p>Bolt load used in flange design for operating conditions (Wo) = {Wo} lbf</p>
                <p>Bolt load used in flange design for gasket seating (Wg) = {Wg} lbf</p>
                <p>Total moment acting on flange for operating conditions (Moo) = {Moo} ft-lbf</p>
                <p>Total moment acting on flange for gasket seating (Mog) = {Mog} ft-lbf</p>
                <p>Longitudinal hub stress at operating conditions (S_Ho) = {S_Ho} psi</p>
                <p>{'APPROVED: ' if S_Ho < (1.5*Sfo) else 'FAILED: '} Longitudinal hub stress at operating conditions is {'less than' if S_Ho < (1.5*Sfo) else 'greater than'} the maximum allowable.</p>
                <p>Longitudinal hub stress at gasket seating (S_Hg) = {S_Hg} psi</p>
                <p>{'APPROVED: ' if S_Hg < (1.5*Sfg) else 'FAILED: '} Longitudinal hub stress at gasket seating is {'less than' if S_Hg < (1.5*Sfg) else 'greater than'} the maximum allowable.</p>
                <p>Raidal flange stress at operating conditions (S_Ro) = {S_Ro} psi</p>
                <p>{'APPROVED: ' if S_Ro < Sfo else 'FAILED: '} Radial flange stress at operating conditions is {'less than' if S_Ro < Sfo else 'greater than'} the maximum allowable.</p>
                <p>Radial flange stress at gasket seating (S_Rg) = {S_Rg} psi</p>
                <p>{'APPROVED: ' if S_Rg < Sfg else 'FAILED: '} Radial flange stress at gasket seating is {'less than' if S_Rg < Sfg else 'greater than'} the maximum allowable.</p>
                <p>Tangential flange stress at operating conditions (S_To) = {S_To} psi</p>
                <p>{'APPROVED: ' if S_To < Sfo else 'FAILED: '} Tangential flange stress at operating conditions is {'less than' if S_To < Sfo else 'greater than'} the maximum allowable.</p>
                <p>Tangential flange stress at gasket seating (S_Tg) = {S_Tg} psi</p>
                <p>{'APPROVED: ' if S_Tg < Sfg else 'FAILED: '} Tangential flange stress at gasket seating is {'less than' if S_Tg < Sfg else 'greater than'} the maximum allowable.</p>
                <p>{'APPROVED: ' if ((S_Ho+S_Ro)/2 < Sfo) else 'FAILED: '} The average of longitudinal and radial flange stresses at operating conditions is {'less than' if ((S_Ho+S_Ro)/2 < Sfo) else 'greater than'} the maximum allowable.</p>
                <p>{'APPROVED: ' if ((S_Hg+S_Rg)/2 < Sfg) else 'FAILED: '} The average of longitudinal and radial flange stresses at gasket seating is {'less than' if ((S_Hg+S_Rg)/2 < Sfg) else 'greater than'} the maximum allowable.</p>
                <p>{'APPROVED: ' if ((S_Ho+S_To)/2 < Sfo) else 'FAILED: '} The average of longitudinal and tangential flange stresses at operating conditions is {'less than' if ((S_Ho+S_To)/2 < Sfo) else 'greater than'} the maximum allowable.</p>
                <p>{'APPROVED: ' if ((S_Hg+S_Tg)/2 < Sfg) else 'FAILED: '} The average of longitudinal and tangential flange stresses at gasket seating is {'less than' if ((S_Hg+S_Tg)/2 < Sfg) else 'greater than'} the maximum allowable.</p>
            </body>
            </html>
        '''
    except Exception as e:
        return f'''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Flange Design Calculator</title>
            </head>
            <body>
                <h1>Flange Design Calculator</h1>
                <p>There was an error during the execution. Please check your input.</p>
            </body>
            </html>


        '''


if __name__ == "__main__":
    app.run()
