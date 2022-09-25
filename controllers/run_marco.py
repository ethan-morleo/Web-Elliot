"""
Module description:

"""

__version__ = '0.3.1'
__author__ = 'Vito Walter Anelli, Claudio Pomo'
__email__ = 'vitowalter.anelli@poliba.it, claudio.pomo@poliba.it'

import importlib
import json
import os
from os import path

import numpy as np
import sys

from elliot.namespace.namespace_model_builder import NameSpaceBuilder
from elliot.result_handler.result_handler import ResultHandler, HyperParameterStudy, StatTest
from hyperopt import Trials, fmin
from elliot.utils import logging as logging_project
import elliot.hyperoptimization as ho

_rstate = np.random.RandomState(42)
here = path.abspath(path.dirname(__file__) + '/../')

print(u'''
__/\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\___/\\\\\\\\\\\\______/\\\\\\\\\\\\_________________________________________        
 _\\/\\\\\\///////////___\\////\\\\\\_____\\////\\\\\\_________________________________________       
  _\\/\\\\\\_________________\\/\\\\\\________\\/\\\\\\______/\\\\\\_____________________/\\\\\\______      
   _\\/\\\\\\\\\\\\\\\\\\\\\\_________\\/\\\\\\________\\/\\\\\\_____\\///_______/\\\\\\\\\\______/\\\\\\\\\\\\\\\\\\\\\\_     
    _\\/\\\\\\///////__________\\/\\\\\\________\\/\\\\\\______/\\\\\\____/\\\\\\///\\\\\\___\\////\\\\\\////__    
     _\\/\\\\\\_________________\\/\\\\\\________\\/\\\\\\_____\\/\\\\\\___/\\\\\\__\\//\\\\\\_____\\/\\\\\\______   
      _\\/\\\\\\_________________\\/\\\\\\________\\/\\\\\\_____\\/\\\\\\__\\//\\\\\\__/\\\\\\______\\/\\\\\\_/\\\\__  
       _\\/\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\___/\\\\\\\\\\\\\\\\\\___/\\\\\\\\\\\\\\\\\\__\\/\\\\\\___\\///\\\\\\\\\\/_______\\//\\\\\\\\\\___ 
        _\\///////////////___\\/////////___\\/////////___\\///______\\/////__________\\/////____''')

print(f'Version Number: {__version__}')


def run_experiment(config_dict):

    builder = NameSpaceBuilder(config_dict, here, here) #modifica rispetto alla versione tradizionale di elliot
    base = builder.base

    dataloader_class = getattr(importlib.import_module("elliot.dataset"),
                               "DataSetLoader")
    # la funzione import_module importa il modulo di cui specifichiamo il path, nello specifico di tale modulo vogliamo l'attributo
    # DataSetLoader
    dataloader = dataloader_class(
        base.base_namespace)   #Passare il namespace di configurazione costruito a partire dal dizionario config
    data_test_list = dataloader.generate_dataobjects() #i nostri risultati

    return data_test_list

def run_evaluation(config_dict, path):
    builder = NameSpaceBuilder(config_dict, here, here)
    base = builder.base_evaluation
    logging_project.init(base.base_namespace.path_logger_config, base.base_namespace.path_log_folder)

    base.base_namespace.evaluation.relevance_threshold = getattr(base.base_namespace.evaluation, "relevance_threshold",
                                                                 0)
    res_handler = ResultHandler(rel_threshold=base.base_namespace.evaluation.relevance_threshold)
    hyper_handler = HyperParameterStudy(rel_threshold=base.base_namespace.evaluation.relevance_threshold)
    dataloader_class = getattr(importlib.import_module("elliot.dataset"),
                               "DataSetLoader")
    dataloader = dataloader_class(
        base.base_namespace)  # Passare il namespace di configurazione costruito a partire dal dizionario config

    data_test_list = dataloader.generate_dataobjects()
    key, model_base= builder.proxy_recommender()
    test_results = []
    test_trials = []
    data_test = data_test_list[0]

    logging_project.prepare_logger(key, base.base_namespace.path_log_folder)

    model_class = getattr(importlib.import_module("elliot.recommender"), key)

    model_placeholder = ho.ModelCoordinator(data_test, base.base_namespace, model_base, model_class,
                                            0)

    print(f"Training begun for {model_class.__name__}\\n")
    single = model_placeholder.single()

    return single['test_results']





