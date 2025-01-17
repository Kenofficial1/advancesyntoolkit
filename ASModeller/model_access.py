'''
Functions to read model specification file into a series of 
model objects, and providing interfaces to model.

Date created: 6th August 2018

Authors: Maurice HT Ling

This file is part of AdvanceSynModeller, which is a part of 
AdvanceSynToolKit.

Copyright (c) 2018, AdvanceSyn Private Limited and authors.

Licensed under the Apache License, Version 2.0 (the "License") for 
academic and not-for-profit use only; commercial and/or for profit 
use(s) is/are not licensed under the License and requires a 
separate commercial license from the copyright owner (AdvanceSyn 
Private Limited); you may not use this file except in compliance 
with the License. You may obtain a copy of the License at 
http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

from configparser import ConfigParser
from configparser import BasicInterpolation
from configparser import ExtendedInterpolation
import os

from .model_object import ModelObject

def modelspec_reader(modelfile, mode='extended'):
    '''!
    Function using ConfigParser (in Python Standard Library) to 
    read a AdvanceSyn model specification file.

    @param modelfile String: Relative path to the model specification 
    file.
    @param mode String: Type of interpolation mode for ConfigParser. 
    Default = 'extended'. Allowable values are 'extended' (for 
    extended interpolation) and 'basic' (for basic interpolation).
    @return: ConfigParser object.
    '''
    if mode == 'extended':
        spec = ConfigParser(interpolation=ExtendedInterpolation(),
                            allow_no_value=True,
                            delimiters=('=', ':'),
                            comment_prefixes=('#', ';'),
                            inline_comment_prefixes=('#', ';'),
                            empty_lines_in_values=True,
                            strict=False)
    if mode == 'basic':
        spec = ConfigParser(interpolation=BasicInterpolation(),
                            allow_no_value=True,
                            delimiters=('=', ':'),
                            comment_prefixes=('#', ';'),
                            inline_comment_prefixes=('#', ';'),
                            empty_lines_in_values=True,
                            strict=False)
    spec.optionxform = str
    modelspec = open(modelfile).read()
    spec.read_string(modelspec)
    return spec

def specobj_reader(specobj, mode='extended'):
    '''!
    Function using ConfigParser (in Python Standard Library) to 
    read a AdvanceSyn model specification as a dictionary-type object.

    @param specobj Dictionary: Model specification in a dictionary / 
    dictionary-like format.
    @param mode String: Type of interpolation mode for ConfigParser. 
    Default = 'extended'. Allowable values are 'extended' (for 
    extended interpolation) and 'basic' (for basic interpolation).
    @return: ConfigParser object.
    '''
    if mode == 'extended':
        spec = ConfigParser(interpolation=ExtendedInterpolation(),
                            allow_no_value=True,
                            delimiters=('=', ':'),
                            comment_prefixes=('#', ';'),
                            inline_comment_prefixes=('#', ';'),
                            empty_lines_in_values=True,
                            strict=False)
    if mode == 'basic':
        spec = ConfigParser(interpolation=BasicInterpolation(),
                            allow_no_value=True,
                            delimiters=('=', ':'),
                            comment_prefixes=('#', ';'),
                            inline_comment_prefixes=('#', ';'),
                            empty_lines_in_values=True,
                            strict=False)
    spec.optionxform = str
    spec.read_dict(specobj)
    return spec

def generate_object_list_1(spec):
    '''!
    Function to generate a table (dictionary) of objects, which 
    represents the entities / nodes of the model. This function 
    is used for AdvanceSyn model specification type 1.

    @param spec Object: ConfigParser object containing the processed 
    model - from modelspec_reader() or specobj_reader() functions.
    @return: Dictionary of objects where key is the object name 
    and value is the object.
    '''
    names = [name for name in spec['Objects']]
    descriptions = [spec['Objects'][name] for name in names]
    objectlist = {}
    for i in range(len(names)):
        obj = ModelObject(names[i], descriptions[i])
        objectlist[names[i]] = obj
    return objectlist

def load_initials_1(spec, objlist):
    '''!
    Function to add initial values from model specification into 
    the table of objects. This function is used for AdvanceSyn 
    model specification type 1.

    @param spec Object: ConfigParser object containing the processed 
    model - from modelspec_reader() or specobj_reader() functions.
    @param objlist Dictionary: Table of objects representing the 
    entities / nodes of the model - from generate_object_list_X() 
    function.
    @return: Dictionary of objects where key is the object name 
    and value is the object numbering.
    '''
    for name in objlist:
        if name in spec['Initials']:
            initial_value = spec['Initials'][name]
            objlist[name].value['initial'] = initial_value
        else:
            objlist[name].value['initial'] = 0
    return objlist

def _backup_object_loader_1(names, objlist):
    '''!
    Private function called by load_reactions_1() function to act 
    as backup loader of objects - it does similar job to 
    generate_object_list_1() and load_initials_1() but as a 
    second layer to ensure that all sources and destinations in 
    reactions have a corresponding object, just in case the user 
    missed out in Objects stanza. Only sources and destinations 
    not found in objects table are loaded with 'Inserted by Backup 
    Object Loader' as description and zero initial value.

    @param names List: List of object names to check
    @param objlist Dictionary: Table of objects representing the 
    entities / nodes of the model - from generate_object_list_X() 
    function.
    @return: Dictionary of objects where key is the object name 
    and value is the object numbering.
    '''
    for i in range(len(names)):
        if names[i] not in objlist and names[i] != '':
            obj = ModelObject(names[i], 
                              'Inserted by Backup Object Loader')
            obj.value['initial'] = 0
            objlist[names[i]] = obj
    return objlist

def process_reactions_1(spec):
    '''!
    Function to generate a table (dictionary) of reactions. This 
    function is used for AdvanceSyn model specification type 1.

    @param spec Object: ConfigParser object containing the processed 
    model - from modelspec_reader() or specobj_reader() functions.
    @return: Dictionary of reactions where key is the reaction ID 
    and value is a dictionary of sources, destinations, and rateEq 
    (rate equation) - sources and destinations is a list of source 
    and destination nodes / entities respectively.
    '''
    rlist = [x for x in spec['Reactions']]
    reactions = {}
    for ID in rlist:
        try: 
            rdata = spec['Reactions'][ID]
            rdata = rdata.split('|')
            # print("%s %s" % (ID, rdata))
            movement = rdata[0].strip()
            rateEq = rdata[1].strip()
            movement = movement.split('->')
            sources = movement[0].strip()
            sources = sources.split('+')
            sources = [s.strip() for s in sources]
            sources = [s for s in sources if s != '']
            destinations = movement[1].strip()
            destinations = destinations.split('+')
            destinations = [d.strip() for d in destinations]
            destinations = [d for d in destinations if d != '']
            reactions[ID] = {'sources': sources,
                             'destinations': destinations,
                             'rateEq': rateEq}
        except:
            print("Error in %s" % str(ID))
            print("    sources: %s" % str(sources))
            print("    destinations: %s" % str(destinations))
            print("    rate equation: %s" % str(rateEq))
    return reactions

def load_reactions_1(reactions, objlist):
    '''!
    Function to load the table (dictionary) of reactions into the 
    table of objects. This function is used for AdvanceSyn model 
    specification type 1.

    @param reactions Dictionary: Table of reactions - from 
    process_reactions_X() function.
    @param objlist Dictionary: Table of objects representing the 
    entities / nodes of the model.
    @return: Dictionary of objects where key is the object name 
    and value is the object numbering.
    '''
    for ID in reactions:
        sources = reactions[ID]['sources']
        objlist = _backup_object_loader_1(sources, objlist)
        destinations = reactions[ID]['destinations']
        objlist = _backup_object_loader_1(destinations, objlist)
        rateEq = reactions[ID]['rateEq']
        for s in sources:
            if s != '':
                try:
                    objlist[s].outflux[ID] = rateEq
                except KeyError:
                    stmt = 'Reaction ID: %s | ' % str(ID) 
                    stmt = stmt + \
                        'Source: %s is not found in Objects' % str(s)
                    print(stmt)
        for d in destinations:
            if d != '':
                try:
                    objlist[d].influx[ID] = rateEq
                except KeyError: 
                    stmt = 'Reaction ID: %s | ' % str(ID) 
                    stmt = stmt + \
                        'Source: %s is not found in Objects' % str(s)
                    print(stmt)
    return objlist

def load_asm_objects(spec):
    '''!
    Function to load values and reactions into model objects based 
    on AdvanceSyn model specification type.

    @param spec Object: Model specification in ConfigParser object.
    @return: Dictionary of objects where key is the object name 
    and value is the object numbering.
    '''
    if spec['Specification']['type'] == '1':
        objlist = generate_object_list_1(spec)
        objlist = load_initials_1(spec, objlist)
        reactions = process_reactions_1(spec)
        objlist = load_reactions_1(reactions, objlist)
    return objlist

def process_asm_model(modelfile):
    '''!
    General function to process the AdvanceSyn model specification 
    file into a table of objects (representing the entities) based 
    on the type of model specification file as defined within the 
    file. Hence, this function is the is the function to call to get 
    table of objects from model specification file.

    @param modelfile String: Relative path to the AdvanceSyn model 
    specification file.
    @return: A tuple of (ConfigParser object containing the 
    processed model, Dictionary of objects where key is the object 
    name and value is the object numbering).
    '''
    spec = modelspec_reader(modelfile, 'extended')
    objlist = load_asm_objects(spec)
    return (spec, objlist)
    