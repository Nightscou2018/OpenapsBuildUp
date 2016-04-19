# The following heavily commented pseudocode is not actually runnable: is an amalgam of syntax
# from multiple programming languages, references a number of functions that are not defined,
# and has not been debugged.
# It is only useful for educational purposes: in particular, to more precisely describe
# the closed loop algorithm proposed in the OpenAPS reference design.

def getProfile():
    profile = {
        'dia': dia, # Duration of Insulin Action (hours)
        'isf': isf, # Insulin Sensitivity Factor (mg/dL/U)
        'bgTargetMin': bgTargetMin, # low end of BG Target range
        'bgTargetMax': bgTargetMax, # high end of BG Target range
        'bgSuspend': (bgTargetMin - 30), # temp to 0 if dropping below this BG
        'maxBasal': maxBasal, # pump's maximum basal setting
        'ic': ic, # Insulin to Carb Ratio (g/U)
        'csf': (isf / ic), # Carb Sensitivity Factor (mg/dL/g)
        'basals': basals # Basal Schedule (array of [start time of day, rate (U/hr)])
        }

    return profile 

def basalLookup(timeOfDay):
    #Return basal rate (U/hr) at the provided timeOfDay
    return basalRateCurrent

def maxBasalLookup():
    #Return maximum daily basal rate (U/hr) from profile.basals
    return maxDailyBasalRate

def getNetIOB(iob, tempBasalHistory):
    for each tempBasal in tempBasalHistory
        normalBasal = basalLookup(tempbasal.time)
        netInsulin = (tempBasal.rate - normalBasal) * tempBasal.duration # How much insulin (+/-)
        hoursAgo = now – basal.time # hours since basal was started
        
        if (hoursAgo > profile[dia]): # getBasalHistory shouldn’t pass any old basals, but ignore them if it does
            iobContrib = 0
        else:
            pass 
            
        iobContrib = netInsulin * (profile[dia] - hoursAgo) / profile[dia] # simple straight-line IOB decay.
        # For manual/mental calculation, iobContrib can be approximated by using round-number math.
        
        iob = iob + iobContrib; # (add/subtract each basal’s net impact to the pump’s IOB number)
    return iob

def getSnoozeFactor():
    # Hours to snooze after each 1U bolus
    # By default, 1U = 30m; 6U = 3h
    return 0.5

def bolusSnooze(bolusHistory, snoozeFactor):
        snoozeUntil = now;
        for each bolus in bolusHistory:
            # extend the snooze time if appropriate based on IOB after each bolus
            snoozeHours = min(profile.dia, getIOB(bolus.time) * snoozeFactor); # don't snooze more than dia hours
            snoozeUntil = max(snoozeUntil, bolus.time + snoozeHours); # extend snooze if appropriate
        return snoozeUntil;

def calcCurrentTempBasal(tempBasalHistory):  # current temp basal rate, or null
    #TODO: NOT SURE WHERE TO PULL TEMPBASALHISTORY FROM
    return currentTempBasal 

def setTempBasal(rate,duration):
    maxSafeBasal = min(profile[maxBasal], 2 * maxBasalLookup, 4 * basalLookup(now))
    
    if (rate < 0):
        rate = 0    # you can't give less than 0 U/hr
    elif (rate > maxSafeBasal):
        rate = maxSafeBasal    # don't give more than maxSafeBasal    
    # issue rate U/hr temp for duration minutes
    system("temp-basal.py --rate rate --duration duration")
    #TODO: HAVE TO FIGURE OUT HOW/IF I COULD ENTER THIS TEMP BASAL RATE INSIDE PYTHON?

def onStartup():
    # Collect profile info at startup:
    profile = getProfile(); # collect profile info from pump
    basalRateCurrent = basalLookup(timeOfDay)
    maxDailyBasalRate = maxBasalLookup

def everyFewMinutes():
    
    #TODO: UPLOAD HISTORY AT THE START OF THE LOOP, PER CALABRESE ON GITTER

    #Collect real-time info every few minutes:
    bg = getBG(now); # Current BG from fingerstick or CGM
    delta = getBGDelta(now); # Current change in BG / BG trend (+ / - / 0)
    iob = getIOB(now); # Current IOB, reported by (or calculated from) pump
    tempBasalHistory = getTempBasalHistory(); # time, duration (hours), and rate (U/hr) of any temp basals
                                              # not included in IOB (limited to last dia hours)
    bolusHistory = getBolusHistory(); # time and size (U) of boluses for last dia hours
    netIOB = getNetIOB(iob, tempBasalHistory); # Calculate net IOB, taking into account temp basals

    #Perform intermediate calculations based on latest BG and insulin history
    
    # When the user does a manual bolus, we assume they know what they're doing, and try to avoid counteracting it.
    # To do so, we snooze OpenAPS to avoid low-temps for a certain number of hours for each 1U bolused.
    snoozeFactor = getSnoozeFactor()

    snoozeUntil = bolusSnooze(bolusHistory, snoozeFactor)
    
    if (snoozeUntil > now):
        return 0 # no action

    eventualBG = bg - (netIOB * profile[isf]) ; # BG expected after dia hours, once all net IOB takes effect

    #TODO: SHOULD THE LINE BELOW NOT BE COMMENTED, AS IT WAS IN THE PSEUDOCODE?
    # If bg < profile.bgSuspend and BG is not rising, temp to zero
    currentTempBasal = calcCurrentTempBasal(tempBasalHistory); # current temp basal rate, or null

    #TODO: NEED TO UNDERSTAND WHAT IS HAPPENING BELOW AND IN SETTEMPBASAL() FUNCTION
    if (bg < profile[bgSuspend]):
        if (delta > 0):   # if BG is rising
            if (currentTempBasal > basalLookup(now)):   # if a high-temp is running
                setTempBasal(0,0)    # cancel temp
        else:   # (delta <= 0), BG is not yet rising
            setTempBasal(0,30)

    # if BG is rising but eventual BG is below target, or BG is falling but eventual BG is above target,
    # then cancel any temp basals.
    if ((delta > 0) and (eventualBG < bgTargetMin)) or ((delta < 0) and (eventualBG > bgTargetMax)): 
        
        #TODO: not sure at all if line above is correct
        if currentTempBasal is not null:  # if there is currently any temp basal running
            setTempBasal(0, 0) # cancel temp
        
    elif (eventualBG < bgTargetMin):  # if eventual BG is below target
        # calculate 30m low-temp required to get projected BG up to target
        insulinReq = (bgTargetMin - eventualBG) / profile[isf]  # negative insulin required to get up to min
        rate = currentTempBasal - (2 * insulinRequired)  # rate required to deliver insulinReq less insulin over 30m
        # rate in insulin per hour, so use 2* the required to make it happen in 30 minutes
        
        if (rate < currentTempBasal):  # if required temp < existing basal
            setTempBasal(rate, 30)     # issue the new temp basal
            # if >30m @ 0 required, zero temp will be extended to 30m instead
    
    elif (eventualBG > bgTargetMax):  # if eventual BG is above target
        # calculate 30m high-temp required to get projected BG down to target
        insulinReq = (bgTargetMax - eventualBG) / profile[isf] # negative insulin required to get down to max
        rate = currentTempBasal - (2 * insulinRequired) # rate required to deliver insulinReq more insulin over 30m
        
        if (rate > currentTempBasal):  # if required temp > existing basal
            setTempBasal(rate, 30)  # issue the new temp basal
            # if new temp basal > max temp basal, max temp will be extended to 30m instead

#-----------------------------------------------------------------------------------------------------------------
# MAIN

onStartup()

while True:
    everyFewMinutes()
    time.sleep(180)

 


'''
function everyFewMinutes() {
    #Collect real-time info every few minutes:
    bg = getBG(now); # Current BG from fingerstick or CGM
    delta = getBGDelta(now); # Current change in BG / BG trend (+ / - / 0)
    iob = getIOB(now); # Current IOB, reported by (or calculated from) pump
    tempBasalHistory = getTempBasalHistory(); # time, duration (hours), and rate (U/hr) of any temp basals
                                              # not included in IOB (limited to last dia hours)
    bolusHistory = getBolusHistory(); # time and size (U) of boluses for last dia hours
    netIOB = getNetIOB(iob, tempBasalHistory); # Calculate net IOB, taking into account temp basals

    function getNetIOB(iob, tempBasalHistory) {
        foreach tempBasal in tempBasalHistory {
            normalBasal = basalLookup(tempbasal.time);
            netInsulin = (tempBasal.rate - normalBasal) * tempBasal.duration; # How much insulin (+/-)
            hoursAgo = now – basal.time; # hours since basal was started
            if(hoursAgo > profile.dia) { iobContrib = 0; next; } # getBasalHistory shouldn’t pass any old basals,
                                                                 # but ignore them if it does
                iobContrib = netInsulin * (profile.dia - hoursAgo) / profile.dia # simple straight-line IOB decay.
                # For manual/mental calculation, iobContrib can be approximated by using round-number math.
                iob = iob + iobContrib; # (add/subtract each basal’s net impact to the pump’s IOB number)
        }
        return(iob);
    }; # end function getNetIOB(iob, tempBasalHistory)


    #Perform intermediate calculations based on latest BG and insulin history

    # When the user does a manual bolus, we assume they know what they're doing, and try to avoid counteracting it.
    # To do so, we snooze OpenAPS to avoid low-temps for a certain number of hours for each 1U bolused.
    snoozeFactor = getSnoozeFactor(); # Hours to snooze after each 1U bolus
    getSnoozeFactor(){ return 0.5; } # By default, 1U = 30m; 6U = 3h

    function bolusSnooze(bolusHistory, snoozeFactor) {
        snoozeUntil = now;
        foreach bolus in bolusHistory {
            # extend the snooze time if appropriate based on IOB after each bolus
            snoozeHours = min(profile.dia, getIOB(bolus.time) * snoozeFactor)); # don't snooze more than dia hours
            snoozeUntil = max(snoozeUntil, bolus.time + snoozeHours); # extend snooze if appropriate
        }
        return snoozeUntil;
    }; # end function bolusSnooze(bolusHistory, snoozeFactor)
    snoozeUntil = bolusSnooze(bolusHistory, snoozeFactor);
    if (snoozeUntil > now) {
        return 0; # no action
    }

    eventualBG = bg - (netIOB * profile.isf) ; # BG expected after dia hours, once all net IOB takes effect

    # If bg < profile.bgSuspend and BG is not rising, temp to zero
    currentTempBasal = calcCurrentTempBasal(tempBasalHistory); # current temp basal rate, or null

    function setTempBasal(rate, duration) {
        maxSafeBasal = min(profile.maxBasal, 2 * maxBasalLookup, 4 * basalLookup(now));
        if (rate < 0) { rate = 0; } # you can't give less than 0 U/hr
        elseif (rate > maxSafeBasal) { rate = maxSafeBasal; } # don't give more than maxSafeBasal
        # issue rate U/hr temp for duration minutes
        system("temp-basal.py --rate rate --duration duration");
    }; # end function setTempBasal(rate)

    if (bg < profile.bgSuspend) {
        if (delta > 0) { # if BG is rising
            if (currentTempBasal > basalLookup(now)) { # if a high-temp is running
                setTempBasal(0, 0); # cancel temp
            }
        }
        else { # (delta <= 0), BG is not yet rising
            setTempBasal(0, 30);
        }
    }
    # if BG is rising but eventual BG is below target, or BG is falling but eventual BG is above target,
    # then cancel any temp basals.
    if ((delta > 0 && eventualBG < bgTargetMin) || (delta < 0 && eventualBG > bgTargetMax)) {
        if (currentTempBasal) { # if there is currently any temp basal running
            setTempBasal(0, 0); # cancel temp
        }
    } elseif (eventualBG < bgTargetMin) { # if eventual BG is below target:
        # calculate 30m low-temp required to get projected BG up to target
        insulinReq = (bgTargetMin - eventualBG) / isf; # negative insulin required to get up to min
        rate = currentTempBasal - 2 * insulinRequired; # rate required to deliver insulinReq less insulin over 30m
        if (rate < currentTempBasal) { # if required temp < existing basal
            setTempBasal(rate, 30); # issue the new temp basal
        } # if >30m @ 0 required, zero temp will be extended to 30m instead
    } elseif (eventualBG > bgTargetMax) { # if eventual BG is above target:
        # calculate 30m high-temp required to get projected BG down to target
        insulinReq = (bgTargetMax - eventualBG) / isf; # negative insulin required to get down to max
        rate = currentTempBasal - 2 * insulinRequired; # rate required to deliver insulinReq more insulin over 30m
        if (rate > currentTempBasal) { # if required temp > existing basal
            setTempBasal(rate, 30); # issue the new temp basal
        } # if new temp basal > max temp basal, max temp will be extended to 30m instead
    }
}; # end funciton everyFewMinutes()
'''

# NOTES TO USE LATER:

'''
#If you are working with files instead of strings, you can alternatively 
use json.dump() and json.load() to encode and decode JSON data. 

For example:

import json

# Writing JSON data
with open('data.json', 'w') as f:
     json.dump(data, f)

# Reading data back
with open('data.json', 'r') as f:
     data = json.load(f)
'''

#TODO: 
# - UPLOAD STATUS TO NIGHTSCOUT, PER CALABRESE ON GITTER
# - figure out how to keep log file continually up-to-date on Git
# - figure out how to ssh into raspi and get logs

'''
From docs: (gitbook)

Components of that system that you might need to add and invoke would be recent glucose data, 
recent pump history, the time, battery status, pump settings, carb ratios, the current basal 
profile, insulin sensitivities, blood glucose targets, and the status of the pump.

Are there groupings of these reports that you imagine would be called at the same time? For
example, in a closed-loop setup, the pump settings, blood glucose targets, insulin
sensitivities, the basal profile, and carb ratios would not need to be checked as often as the
current pump status, battery status, clock, recent blood sugars, and recent pump history.

--- Reports:

-- occasionally:
pump settings
blood glucose targets
insulin sensitivities
basal profile
carb ratios

-- regularly
current pump status
battery status
clock time
recent glucose data 
recent pump history



'''