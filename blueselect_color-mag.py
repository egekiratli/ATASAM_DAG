from pylab import * # import everything in the module
import numpy as np # import the module and use a shorter namespace
import pyfits # to be able to handle fits files
import csv # to be able to handle csv files
import math
import collections
import os
import time
import matplotlib.pyplot as plt
from matplotlib import rc
rc('text', usetex=True)

#================================================================
# SECTION 1: Creating variables, files and folders will be needed
#================================================================
#data to use. You must give the full path!
fits_file = '/home/osa/Dropbox/PhD/Work/201305-New_colours/int3-8eso2.fits'
system = sys.argv[1]
colour = sys.argv[2]
binning= sys.argv[3]
#colour = raw_input('colour? : ')
#system = raw_input('AB or Vega? : ')
#binning = raw_input('binning1 or binning2? : ')
# Magnitude names must be identical to column name in the fits file
if system == 'AB':
    if colour == 'uming':
        plane = 'g-uming_ab' # just for naming folder and files
        colour = 'uming_ab'
        mag_1 = 'gab' #must be same with mag in the "plane"
        mag_2 = 'uab' #the other magnitude
        err_1 = 'gaberr'
        err_2 = 'uaberr'
    elif colour == 'gminr':
        plane = 'g-gminr_ab' # just for naming folder and files
        colour = 'gminr_ab'
        mag_1 = 'gab' #must be same with mag in the "plane"
        mag_2 = 'rab' #the other magnitude
        err_1 = 'gaberr'
        err_2 = 'raberr'
    else:
        sys.exit('Wrong color!!!!')

elif system == 'Vega':
    if colour == 'Uming':
        plane = 'g-Uming' # just for naming folder and files
        colour = 'Uming'
        mag_1 = 'g' #must be same with mag in the "plane"
        mag_2 = 'U' #the other magnitude
        err_1 = 'gerr'
        err_2 = 'Uerr'
    elif colour == 'gminr':
        plane = 'g-gminr' # just for naming folder and files
        colour = 'gminr'
        mag_1 = 'g' #must be same with mag in the "plane"
        mag_2 = 'r' #the other magnitude
        err_1 = 'gerr'
        err_2 = 'rerr'
    else:
        sys.exit('Wrong color!!!!')
else:
    sys.exit("type exactly 'AB' or 'Vega' (without quotes, of course)!")


n_bins = 15 #total number of bins in a field

print(
'Main ingredients are:'
'fits_file = %s '
'plane = %s'
'colour = %s'
'mag_1 = %s'
'mag_2 = %s'
'err_1 = %s'
'err_2 = %s'
'binning = %s'
) % (fits_file, plane, colour, mag_1, mag_2, err_1, err_2, binning)
#sort the fits file according to mag_1 before using it.
#make a copy, use it (and at the end delete it)
# stilts, command line version of TOPCAT should be installed
if not os.path.exists('sorted-%s-%s.fits' %(plane,binning)):
    os.system("stilts tpipe cmd='sort %s' %s out=sorted-%s-%s.fits"
    %(mag_1,fits_file,plane,binning))


## Read the data and columns
fitspointer = pyfits.open('sorted-%s-%s.fits' %(plane,binning))
data = fitspointer[1].data
#to see what's going on
print(number of run=%s) % len(data.field('RUN'))
print(number of %s=%s) % (mag_1,len(data.field(mag_1)))
print(=*15) #cosmetic
print() #empty line
#create a folder to put the output files
os.system("mkdir -p ./%s" %(plane))
os.system("mkdir -p ./%s/%s" %(plane,binning))
path_folder = "./%s/%s" %(plane,binning)
#to see what's going on
print(%s has been created) % path_folder

print " " #empty line
print "="*15 #cosmetic
print " " #empty line
####_________________________________________________________
# Create a csv file to write the name of the files that are empty
# which means there is no blue object in that particular field.
# To be able to write a row from any field in any run to
# this file, I need to create the file before the run loop.
#define your file and give details of it:
#name and path
name_empty = '0_noblue_fields_%s.csv' %plane
path_empty = '%s/%s' %(path_folder,name_empty)
#open your file
empty_files = open(path_empty,'wb')
#name your writer
empty_writer = csv.writer(empty_files)
#write a row which is the header
empty_writer.writerow(['RUN','FIELD','Reason','Plane','Mag_sys','Binning'])
#flush the file to write the changes to disk.
empty_files.flush()
#to see what's going on
print "%s has been created in %s" %(name_empty,path_folder)
print " " #empty line
print "="*15 #cosmetic
print " " #empty line
####____________________________________________________________
#### Create a csv file to write all the data of blue ones.
#define your file and give details of it:
#name and path
name_all = '0_all_blues_%s.csv' %plane

path_all = '%s/%s' %(path_folder,name_all)
#open your file
all_blues = open(path_all,'wb')
#name your writer
blue_writer = csv.writer(all_blues)
#write a row which is the header
blue_header = []
for t in fitspointer[1].columns.names:
blue_header.append(t)
blue_header.extend(['Plane','Mag_sys','Binning','bin_no','median','sigma'])
blue_writer.writerow(blue_header)
#flush it babe!
all_blues.flush()
#to see what's going on
print "%s has been created in %s" %(name_all,path_folder)
print " " #empty line
print "="*15 #cosmetic
print " " #empty line
####_________________________________________________________
if binning == 'binning1':
name_skipped = '0_skipped_bins_%s.csv' %plane
path_skipped = '%s/%s' %(path_folder,name_skipped)
#open your file
skipped_bins = open(path_skipped,'wb')
#name your writer
writer_skipped = csv.writer(skipped_bins)
#write a row which is the header
writer_skipped.writerow(['RUN','FIELD','bin','bin_bright',\
'bin_faint','n_stars', 'Plane',\
'Mag_sys','Binning'])

#flush the file to write the changes to disk.
skipped_bins.flush()
#to see what's going on
print "%s has been created in %s" %(name_skipped,path_folder)
print " " #empty line
print "="*15 #cosmetic
print " " #empty line
# The End of SECTION 1
#============================================================
#============================================================
# SECTION 2: Preparing the data to selection process
## Remove objects has no magnitude or colour information.
## Just keep the ones that have both.
full = logical_and( logical_not(isnan(data.field(colour))),
logical_not(isnan(data.field(mag_1))))
# notice mag_1 and colour are both string
# there are some cells that are not empty but not usefull either.
# for example umag = -50.0 :s
# we need to remove those as well
# notice mag_1 and mag_2 are both string
good = full & (data.field(mag_1) > 10)
& (data.field(mag_1) < 25)
& (data.field(mag_2) > 10)
& (data.field(mag_2) < 25)
& (data.field(colour) > -3)
& (data.field(colour) < 4)
# this number (10) should be
# as greater as possible to remove all nonsense datapoint.
# 10 is good enough. There is no star brighter than ~14 magnitude in
# our data, so we don't exclude any object.

#to see what's going on
print "="*15 #cosmetic
print " " #empty
print "Does 'good' has False?"
print list(set(good))
print " "
good_data = data.field('RUN')[good]
print "%s out of %s star has colour and magnitude."
% (len(good_data),len(data.field('RUN')))
print " "
###select data points that satisfies the condition e.g. "good" ones
g_data = data[good]
#to see what's going on
print "="*15 #cosmetic
print " " #empty line
print "number of good_run = %s" % len(g_data.field('RUN'))
print "number of good_field = %s" % len(g_data.field('FIELD'))
print " "
#============================================================
# SECTION 3: Selection process.
# Apply the selection to all runs,
## one-by-one, separately, not all at once...
## you: OK, I got it!!
## me : Oh, sorry :)
##========================================
run_list = list(set(data.field('RUN')))
# set() shows the unique values in a list,
# and list() writes them in a list.
run_list.sort()
# Example:
# >>> a = [1,1,2,2,2,3,4,5,5,6,6,7]

# >>> set(a)
# set([1, 2, 3, 4, 5, 6, 7])
# >>> list(set(a))
# [1, 2, 3, 4, 5, 6, 7]
#to see what's going on
print "="*15 #cosmetic
print " " #empty line
print "There are %s runs in this FITS file." % len(run_list)
print "which are:"
print run_list
#In run_list we have field numbers. So, to apply selection
#method to each run, we only need a for loop.
for r in run_list:
#to see what's going on
print " "
print "="*50
print " "
print "This is run %s." % r # r is the run number
print " "
print "lenght of run_list = %s" % len(run_list)
print run_list
#condition for being in this run
run_to_use = (g_data.field('RUN') == r)
#to see what's going on
print "number of run_to_use=%s" % len(run_to_use)
count_of_false = collections.Counter(run_to_use)
print count_of_false
#select data points that satisfies the condition,
#that is observed in this run, and rename them.
# !!!rename is necessary!!!
r_data = g_data[run_to_use]
# If there is no data

if len(r_data) == 0:
print "There is NO data in this run :("
print " "
print "="*50
print " "
empty_writer.writerow([r, 'ALL','No good data',
plane,system,binning])
empty_files.flush()
continue #skip this run and go to the next one
#to see what's going on
print "="*50
print " "
print r_data.field('RUN')
print "number of r_run=%s" % (len(r_data.field('RUN')))
if len(list(set(r_data.field('RUN')))) == 1:
print "all r_runs equal to %s"
% (list(set(r_data.field('RUN'))))[0]
else:
print """there is at least one different run here,
which is a problem.
see below:
"""
forbidden_runs = list(set(r_data.field('RUN')))
sys.exit("\n\n\n\n\n\n\n###################### \
\n\n\n\n\n\n\n\n\n\n there is at least one different run here,\
which is a problem.\n see below: \
\n %s\n\n\n\n\n\n\n\n ######################"
%(forbidden_runs))
print "number of r_%s=%s" % (mag_1,len(r_data.field(mag_1)))
print "number of r_field=%s" % len(r_data.field('FIELD'))
print "="*50
print " "
##==============================================================
## Apply the selection to all fields,
## one-by-one, separately, not all at once

## you: I said, I got it!!
## me : Oh, sorry, again:)
##========================================
field_list = list(set(r_data.field('FIELD')))
#to see what's going on
print "There are %s fields in this run." % len(field_list)
print "which are:"
print field_list
# In field_list we have field numbers
# So, to apply selection method to each field,
# we just need a for loop, yahooo :)
for f in field_list:
print " "
print "="*50
print " "
print "This is run%s field%s." % (r,f) # r is the run number
# f is the field number
print " "
#to see what's going on
print "number of field_list = %s" % len(field_list)
print field_list
#condition for being in this run
field_to_use = (r_data.field('FIELD') == f)
#to see what's going on
print "number of field_to_use=%s" % len(field_to_use)
count_of_false = collections.Counter(field_to_use)
print count_of_false
#select data points that satisfies the condition,
#that is observed in this field, and rename them.
# !!!rename is necessary!!!
f_data = r_data[field_to_use]

if len(f_data) < 20*n_bins:
print '''There are only
%s
data-points
in this field!!!
''' %len(f_data)
empty_writer.writerow([r,f,'too less data in the field',\
plane, system, binning])
empty_files.flush()
continue
#to see what's going on
print "="*50
print " "
print "f_run is:"
print "="*15
print " "
print f_data.field('RUN')
print "number of f_run=%s" % (len(f_data.field('RUN')))
print "all f_runs equal to %s" % (list(set(f_data.field('RUN'))))[0]
print "number of f_%s=%s" % (mag_1,len(f_data.field(mag_1)))
print "number of f_field=%s" % len(f_data.field('FIELD'))
print "="*50
print " "
#========Create a ".csv" file to write "blue" ones==========
# In order to write data coming from all bins in a particular
# field into one single file, we need to create this file
# outside of(before) the binning loop and in the field loop.
#define your file and give details of it:
#____________________________________________________________
#Funny thing below (if and elif chain) is just for fun:
#To have filenames like 'r01f03.csv' instead of 'r1f3.csv'
#Those zeros are important for me, I love them :)
#If you don't need those zeros, you can use only the last 

#'field_file = open(...)...' part by deleting between "from here"
#and "till here"!
#Best regards :)
#____________________________________________________________
# "from here"
if (f_data.field('RUN')[0] < 10)
& (f_data.field('FIELD')[0] < 10):
name_field_file = 'r0%s_f0%s' %(r,f)
elif (f_data.field('RUN')[0] >= 10)
& (f_data.field('FIELD')[0] < 10):
name_field_file = 'r%s_f0%s' %(r,f)
elif (f_data.field('RUN')[0] < 10)
& (f_data.field('FIELD')[0] >= 10):
name_field_file = 'r0%s_f%s' %(r,f)
elif (f_data.field('RUN')[0] >= 10)
& (f_data.field('FIELD')[0] >= 10):
# "till here"
# and of course you need to de-indent part below if you delete above.
name_field_file = 'r%s_f%s' %(r,f)
path_field_file = '%s/%s.csv' %(path_folder,name_field_file)
field_file = open(path_field_file,'wb')
#name your writer
fbyf_writer = csv.writer(field_file)
#write headers(column names) to the file
fbyf_header = []
for h in fitspointer[1].columns.names:
fbyf_header.append(h)
fbyf_header.extend(['Plane','Mag_sys',\
'Binning',"bin_no",\
'median','sigma'])
fbyf_writer.writerow(fbyf_header)
field_file.flush()

#'field_file = open(...)...' part by deleting between "from here"
#and "till here"!
#Best regards :)
#____________________________________________________________
# "from here"
if (f_data.field('RUN')[0] < 10)
& (f_data.field('FIELD')[0] < 10):
name_field_file = 'r0%s_f0%s' %(r,f)
elif (f_data.field('RUN')[0] >= 10)
& (f_data.field('FIELD')[0] < 10):
name_field_file = 'r%s_f0%s' %(r,f)
elif (f_data.field('RUN')[0] < 10)
& (f_data.field('FIELD')[0] >= 10):
name_field_file = 'r0%s_f%s' %(r,f)
elif (f_data.field('RUN')[0] >= 10)
& (f_data.field('FIELD')[0] >= 10):
# "till here"
# and of course you need to de-indent part below if you delete above.
name_field_file = 'r%s_f%s' %(r,f)
path_field_file = '%s/%s.csv' %(path_folder,name_field_file)
field_file = open(path_field_file,'wb')
#name your writer
fbyf_writer = csv.writer(field_file)
#write headers(column names) to the file
fbyf_header = []
for h in fitspointer[1].columns.names:
fbyf_header.append(h)
fbyf_header.extend(['Plane','Mag_sys',\
'Binning',"bin_no",\
'median','sigma'])
fbyf_writer.writerow(fbyf_header)
field_file.flush()

print "="*15
print " "
#borders of a bin
bin_bright = brightest_mag + i*w_bin #bright border
bin_faint = brightest_mag + (i+1)*w_bin #faint border
#for last bin:
# I want that star at the end :p
# I don't want to lose it because of rounding.
if i == n_bins - 1:
bin_faint = faintest_mag
print " "
print "="*15
print "This is bin15"
print "="*15
print " "
bin_no = i+1 #bin number
#to see what's going on
print "bin_no = %.0f" % bin_no
print "bin_bright= %.2f" % bin_bright
print "bin_faint = %.2f" % bin_faint
print "w_bin = %.2f" % w_bin
print " "
the_bin = ((f_data.field(mag_1)) >= bin_bright)
& ((f_data.field(mag_1)) < bin_faint)
# Stretching the border makes sense now, doesn't it? :)
# Check out the second part of the condition.
#select data points that satisfies the condition,
#that is being in this bin, and rename them.
# !!!rename is necessary!!!
bin_data = f_data[the_bin]
#info about bin

print "There are %s stars in this bin" % len(bin_data)
print " "
# If there are too less star in a bin, just skip it!
if len(bin_data) < 20:
print """
There are too less object in this bin.
So just skipping it...
======================================
"""
writer_skipped.writerow([r, f, bin_no, bin_bright,
bin_faint, len(bin_data),
plane, system, binning])
skipped_bins.flush()
if 'skipped bin' in given_labels:
plt.plot(bin_data.field(colour),
bin_data.field(mag_1),
'o', color='0.5', markersize=5)
else:
plt.plot(bin_data.field(colour),
bin_data.field(mag_1),
'o', color='0.5', markersize=5,
label='skipped bin')
given_labels.append('skipped bin')
continue
#=====================================================
# ============ Actual Selection Part!!! =============
#=====================================================
#find the median in colour axis
med = median(bin_data.field(colour))
print "Median =%f" % med

print " "
#condition for being on left(blue)-side of the median
left = bin_data.field(colour) < med
#values of blue-siders:
#select data points that satisfies the condition,
#that is being on blue-side, and rename them.
# !!!rename is necessary!!!
left_data = bin_data[left]
#information
print "There are %s stars on the blue side of median"
%len(left_data)
print " "
#sigma calculation
residuals = left_data.field(colour) - med
sigma = sqrt(sum(residuals**2)/len(residuals))
print "Sigma =%f" % sigma
print " "
#3sigma-cutting
sigma_cut = med - 3*sigma
#condition for being blue!
#Distance To Sigma Cut
distance = abs(left_data.field(colour) - sigma_cut)
blue = (left_data.field(colour) < sigma_cut)
& ((left_data.field(err_1)*3) < distance)
& ((left_data.field(err_2)*3) < distance)
#select data points that satisfies the condition,
#that is being blue, and rename them.
# !!!rename is necessary!!!
blue_data = left_data[blue]

#If there is no blue one:
if len(blue_data) == 0:
print """There is NO "blue" object in this bin:("""
print " "
print "="*50
print " "
if 'no blue' in given_labels:
plt.plot(bin_data.field(colour),
bin_data.field(mag_1),
'yo', markersize=5)
else:
plt.plot(bin_data.field(colour),
bin_data.field(mag_1),
'yo', markersize=5, label='no blue')
given_labels.append('no blue')
if 'median' in given_labels:
plt.plot([med,med],
[min(bin_data.field(mag_1)),
max(bin_data.field(mag_1))],
'g-', linewidth=2.0)
else:
plt.plot([med,med],
[min(bin_data.field(mag_1)),
max(bin_data.field(mag_1))],
'g-', linewidth=2.0, label='median')
given_labels.append('median')
if '3sigma' in given_labels:
plt.plot([sigma_cut,sigma_cut],
[min(bin_data.field(mag_1)),
max(bin_data.field(mag_1))],
'k-', linewidth=2.0)
else:
plt.plot([sigma_cut,sigma_cut],
[min(bin_data.field(mag_1)),
max(bin_data.field(mag_1))],
'k-', linewidth=2.0, label='3sigma')

given_labels.append('3sigma')
continue
#going to the next bin
#if this is the last bin in this field, moving forward.
#If there are some:
print """There are %s "blue" stars in this bin."""
% len(blue_data)
print " "
#==============================================================
# ============ Write the blue objects to the file ============
#==============================================================
print '''
Writing data to both files,
field-specific csv file and the big file...
'''
#write data: mind the order of headers!!!
for i in blue_data:
satir = list(i)
satir.extend([plane,system,binning,bin_no,med,sigma])
fbyf_writer.writerow(satir)
blue_writer.writerow(satir)
print '''
Data of blue objects from Bin %s has been added
to the both files.
''' % bin_no
print "="*30
print " "
field_file.flush()
all_blues.flush()
if 'blue ones' in given_labels:

plt.plot(blue_data.field(colour),
blue_data.field(mag_1),
'bo', markersize=5)
else:
plt.plot(blue_data.field(colour),
blue_data.field(mag_1),
'bo', markersize=5, label='blue ones')
given_labels.append('blue ones')
if 'median' in given_labels:
plt.plot([med,med],
[min(bin_data.field(mag_1)),
max(bin_data.field(mag_1))],
'g-', linewidth=2.0)
else:
plt.plot([med,med],
[min(bin_data.field(mag_1)),
max(bin_data.field(mag_1))],
'g-', linewidth=2.0, label='median')
given_labels.append('median')
if '3sigma' in given_labels:
plt.plot([sigma_cut,sigma_cut],
[min(bin_data.field(mag_1)),
max(bin_data.field(mag_1))],
'k-', linewidth=2.0)
else:
plt.plot([sigma_cut,sigma_cut],
[min(bin_data.field(mag_1)),
max(bin_data.field(mag_1))],
'k-', linewidth=2.0, label='3sigma')
given_labels.append('3sigma')
#going back to do the same thing for next bin
#if this is the last bin in this field, moving forward.
elif binning == 'binning2':
#defining some variables

#n_bins, number of bins, is defined at the beginning
N_star=len(f_data) #total number of stars in the field
n_star=N_star/n_bins #number of stars in every bin
print "There are %s bins in every field" %n_bins
print "There are %s stars in this field" % N_star
print "There should be %s stars in every bin" %n_star
print "="*15
print " "
#============ Actual binning part! ============
for i in range(n_bins):
bin_no = i+1
print "This is Bin %s" % bin_no
#define new arrays that contains data only for this bin
# !!!rename is necessary!!!
if i < n_bins-1:
bin_data = f_data[n_star*i:n_star*(i+1)]
elif i == n_bins-1:
bin_data = f_data[n_star*i:]
else:
print """
Yok artik Ali Sami!!!
"""
#info about bin
print "There are %s stars in this bin" % len(bin_data)
print " "
#=====================================================
# ============ Actual Selection Part!!! =============
#=====================================================

#find the median in colour axis
med = median(bin_data.field(colour))
print "Median =%f" % med
print " "
#condition for being on left(blue)-side of the median
left = bin_data.field(colour) < med
#values of blue-siders:
#select data points that satisfies the condition,
#that is being on blue-side, and rename them.
# !!!rename is necessary!!!
left_data = bin_data[left]
#information
print "There are %s stars on the blue side of median"
%len(left_data.field('RUN'))
print " "
#sigma calculation
residuals = left_data.field(colour) - med
sigma = sqrt(sum(residuals**2)/len(residuals))
print "Sigma =%f" % sigma
print " "
#3sigma-cutting
sigma_cut = med - 3*sigma
#condition for being blue!
#Distance To Sigma Cut
distance = abs(left_data.field(colour) - sigma_cut)
blue = (left_data.field(colour) < sigma_cut)
& ((left_data.field(err_1)*3) < distance)
& ((left_data.field(err_2)*3) < distance)
#select data points that satisfies the condition,
that is being blue, and rename them.
# !!!rename is necessary!!!
blue_data = left_data[blue]
#If there is no blue one:
if len(blue_data) == 0:
print """There is NO "blue" object in this bin:("""
print " "
print "="*50
print " "
if 'no blue' in given_labels:
plt.plot(bin_data.field(colour),
bin_data.field(mag_1),
'yo', markersize=5)
else:
plt.plot(bin_data.field(colour), b
in_data.field(mag_1),
'yo', markersize=5, label='no blue')
given_labels.append('no blue')
if 'median' in given_labels:
plt.plot([med,med],
[min(bin_data.field(mag_1)),
max(bin_data.field(mag_1))],
'g-', linewidth=2.0)
else:
plt.plot([med,med],
[min(bin_data.field(mag_1)),
max(bin_data.field(mag_1))],
'g-', linewidth=2.0, label='median')
given_labels.append('median')
if '3sigma' in given_labels:
plt.plot([sigma_cut,sigma_cut],
[min(bin_data.field(mag_1)),
max(bin_data.field(mag_1))],
'k-', linewidth=2.0)
else:

plt.plot([sigma_cut,sigma_cut],
[min(bin_data.field(mag_1)),
max(bin_data.field(mag_1))],
'k-', linewidth=2.0, label='3sigma')
given_labels.append('3sigma')
continue
#If there are some:
print """There are %s "blue" stars in this bin.
""" % len(blue_data)
#====================================================
# ============ Write the blue objects to the file ===
#====================================================
print '''
Writing data to both files, field-specific csv file
and the big file...
'''
#write data: mind the order of headers!!!
for i in range(len(blue_data)):
satir = list(blue_data[i])
satir.extend([plane,system,binning,bin_no,med,sigma])
fbyf_writer.writerow(satir)
blue_writer.writerow(satir)
print '''
Data of blue objects from Bin %s has been added
to the both files.
''' % bin_no
print "="*30
print " "
field_file.flush()
all_blues.flush()
xerrp = [max(left_data.field(err_1)[i],
             
left_data.field(err_2)[i])
for i in range(len(left_data.field(err_1)))]
xerrn = zeros(len(left_data.field(err_1)))
yerrp = zeros(len(left_data.field(err_1)))
yerrn = zeros(len(left_data.field(err_1)))
if 'blue ones' in given_labels:
plt.plot(blue_data.field(colour),
blue_data.field(mag_1),
'bo', markersize=5)
else:
plt.plot(blue_data.field(colour),
blue_data.field(mag_1),
'bo', markersize=5, label='blue ones')
given_labels.append('blue ones')
if 'median' in given_labels:
plt.plot([med,med],
[min(bin_data.field(mag_1)),
max(bin_data.field(mag_1))],
'g-', linewidth=2.0)
else:
plt.plot([med,med],
[min(bin_data.field(mag_1)),
max(bin_data.field(mag_1))],
'g-', linewidth=2.0, label='median')
given_labels.append('median')
if '3sigma' in given_labels:
plt.plot([sigma_cut,sigma_cut],
[min(bin_data.field(mag_1)),
max(bin_data.field(mag_1))],
'k-', linewidth=2.0)
else:
plt.plot([sigma_cut,sigma_cut],
[min(bin_data.field(mag_1)),
max(bin_data.field(mag_1))],
'k-', linewidth=2.0, label='3sigma')
given_labels.append('3sigma')

#going back to do the same thing for next bin
#if this is the last bin in this field, moving forward.
else:
sys.exit("Type exactly 'binning1' or 'binning2'\
(without quotes, of course)")
#close the file
field_file.close()
#If there is no blue in this field and csv file consists of only
# headers, I would like to delete it.
# read the file in...
read_to_count = csv.reader(open(path_field_file, 'rb'))
#count the rows!
row_count = sum(1 for row in read_to_count)
print '''
there are %s blue objects in the run %s field %s'''
%(row_count-1,r,f)
# delete it if it is empty
if row_count == 1: #1 row means only header
print "There is NO 'blue' object in this field :("
print "So, deleting the empty csv file..."
print " "
print " "
#Before removing it, I would like to note its name.
empty_writer.writerow([r, f, 'no blue',plane,system,binning])
print "Name of empty file has been added to the list."
empty_files.flush()
#remove it
os.system("rm %s" %(path_field_file))
print " "

print "="*50
plt.close() # otherwise, you'll see refugee plots from this field
# on the next field's plot
continue
#get rid of 'nan's
os.system("sed 's/nan//g' %s > tmp && mv tmp %s"
%(path_field_file,path_field_file))
#last touches to the graph and then save it.
plt.xlabel(colour)
plt.ylabel(mag_1)
plt.legend(prop={'size':10}, fancybox=True)
plt.title('Run %s Field %s \n --- Blue Ones ---' %(r,f))
plt.axis([-3,4,26,12])
plt.savefig('%s/%s_blues.png' %(path_folder,name_field_file))
print '%s/%s_blues.png has been saved! Yayy! :)'
%(path_folder,name_field_file)
plt.close()
#going to do the same thing for next field.
#if this is last field in this run, moving forward.
#going to do the same thing for next run.
#if this is last run, moving forward to end process.
empty_files.close()
print "empty_files is closed"
all_blues.close()
print "all_blues is closed"
#delete the sorted fits file
os.system('rm sorted-%s-%s.fits' %(plane,binning))
#get rid of 'nan's

os.system("sed 's/nan//g' %s > tmp && mv tmp %s" %(path_all,path_all))
print " "
print "All png files are being combined into a pdf file..."
os.system("/usr/bin/convert %s/*.png %s/all_fields.pdf"
%(path_folder,path_folder))
print " "
print "%s/all_fields.pdf is created!" %(path_folder)