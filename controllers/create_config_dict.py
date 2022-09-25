import os
import shutil
from datetime import datetime
import hashlib  # se proprio dopo vogliamo farla con hash il nome del dataset
from flask import Flask, request
import zipfile  # per gestire lo zip inviato nella strategia hierarchy

# questa funzione viene utilizzata per creare un dizionario di configurazione a partire dall'oggetto richiesta proveniente dal client
#TODO sistemare il bug con il fixed timestamp
#TODO sistemare il bug nel temporal hold out
def create_config_dict(request):
    config = dict()
    config['experiment'] = dict()
    config['experiment']['data_config'] = dict()
    # salvataggio dei file in un path a seconda della situazione da gestire
    config['experiment']['data_config']['strategy'] = request.form[
        'loading_strategy']  # no valore di default perché almeno una strategia la deve scegliere
    timestamp = datetime.now()
    timestamp_string = timestamp.strftime("%d-%m-%Y-%H-%M-%S")  # timestamp con cui salvare il dataset utilizzato
    if request.form['loading_strategy'] == 'dataset':

        print('Selected dataset strategy')
        # datasetPath = 'data/' + md5(timestamp_string) + '/' + 'dataset.tsv'
        cript = hashlib.md5((timestamp_string + 'request/').encode('utf-8'))
        _path = 'data/' + cript.hexdigest()
        os.makedirs(_path, exist_ok=False)
        dataset_path = _path + '/dataset.tsv'
        request.files.get('dataset_file').save(dataset_path)  # dataset salvato in dataset path
        config['experiment']['data_config']['dataset_path'] = dataset_path

        config['experiment']['splitting'] = dict()
        config['experiment']['splitting']['test_splitting'] = dict();
        config['experiment']['splitting']['test_splitting']['strategy'] = request.form.get('test_splitting_strategy',
                                                                                           None)

        # gestione prefiltering
        # prefiltering_strategies = dict() //non dovrebbe servire più, se dà errori rimetterlo
        prefiltering_strategies = {k: v for k, v in request.form.lists()}.get('prefiltering_strategy', None)

        config['experiment']['prefiltering'] = []
        # è una lista di dizionari, creaimo un nuovo dizionario e lo aggiungiamo in coda alla lista (usa metodo append)
        # gestione delle strategie di prefiltering
        if prefiltering_strategies:
            if ('global_threshold' in prefiltering_strategies):
                print('Selected global_threshold as prefiltering strategy')
                d1 = dict()
                d1['strategy'] = 'global_threshold'
                d1['threshold'] = int(request.form.get('global_threshold_threshold', None))  # come metto average
                config['experiment']['prefiltering'].append(d1)
            if ('user_average' in prefiltering_strategies):
                print('Selected user_average as prefiltering strategy')
                d2 = dict()
                d2['strategy'] = 'user_average'
                config['experiment']['prefiltering'].append(d2)
            if ('user_k_core' in prefiltering_strategies):
                print('Selected item_k_core as prefiltering strategy')
                d3 = dict()
                d3['strategy'] = 'user_k_core'
                d3['core'] = int(request.form.get('user_k_core_core', None))
                config['experiment']['prefiltering'].append(d3)
            if ('item_k_core' in prefiltering_strategies):
                print('Selected item_k_core as prefiltering strategy')
                d4 = dict()
                d4['strategy'] = 'item_k_core'
                d4['core'] = int(request.form.get('item_k_core_core', None))
                config['experiment']['prefiltering'].append(d4)
            if ('iterative_k_core' in prefiltering_strategies):
                print('Selected iterative_k_core as prefiltering strategy')
                d5 = dict()
                d5['strategy'] = 'iterative_k_core'
                d5['core'] = int(request.form.get('iterative_k_core_core', None))
                config['experiment']['prefiltering'].append(d5)
            if ('n_rounds_k_core' in prefiltering_strategies):
                print('Selected n_rounds_k_core as prefiltering strategy')
                d6 = dict()
                d6['strategy'] = 'n_rounds_k_core'
                d6['core'] = int(request.form.get('n_rounds_k_core_core', None))
                d6['rounds'] = int(request.form.get('n_rounds_k_core_rounds', None))
                config['experiment']['prefiltering'].append(d6)
            if ('cold_users' in prefiltering_strategies):
                print('Selected cold_users as prefiltering strategy')
                d7 = dict()
                d7['strategy'] = 'cold_users'
                d7['threshold'] = int(request.form.get('cold_users_threshold', None))
                config['experiment']['prefiltering'].append(d7)

        # gestione test data splitting
        config['experiment']['splitting'] = dict()
        config['experiment']['splitting']['test_splitting'] = dict()
        config['experiment']['splitting']['test_splitting']['strategy'] = request.form.get('test_splitting_strategy',
                                                                                           None)
        if request.form['test_splitting_strategy']:  # deve attivarsi sempre perché è obbligatorio
            if request.form.get('test_splitting_strategy') == 'fixed_timestamp':
                # gestione test_fixed_timestamp
                print('Selected a fixed timestamp test splitting strategy ')
                if request.form.get('test_fixed_timestamp_value') == 'best':
                    config['experiment']['splitting']['test_splitting']['timestamp'] = request.form.get(
                        'test_fixed_timestamp_value')
                else:
                    config['experiment']['splitting']['test_splitting']['timestamp'] = int(request.form.get(
                        'test_fixed_timestamp_value',
                        None))
            elif request.form.get('test_splitting_strategy') == 'temporal_hold_out':
                print('Selected a temporal hold out test splitting strategy ')
                if request.form.get('test_temporal_hold_out_test_ratio'):
                    config['experiment']['splitting']['test_splitting']['test_ratio'] = float(request.form.get(
                        'test_temporal_hold_out_test_ratio', None))
                else:
                    config['experiment']['splitting']['test_splitting']['leave_n_out'] = int(request.form.get(
                        'test_temporal_hold_out_test_leave_n_out', None))
            elif request.form.get('test_splitting_strategy') == 'random_subsampling':
                print('Selected a random subsampling test splitting strategy ')
                if request.form.get('test_random_subsampling_test_ratio'):
                    config['experiment']['splitting']['test_splitting']['test_ratio'] = float(request.form.get(
                        'test_random_subsampling_test_ratio', None))
                else:
                    config['experiment']['splitting']['test_splitting']['leave_n_out'] = int(request.form.get(
                        'test_random_subsampling_leave_n_out', None))
                if request.form.get('test_random_subsampling_folds'):
                    config['experiment']['splitting']['test_splitting']['folds'] = int(request.form.get(
                        'test_random_subsampling_folds', 1))

            elif request.form.get('test_splitting_strategy') == 'random_cross_validation':
                print('Selected a random cross validation test splitting strategy ')
                config['experiment']['splitting']['test_splitting']['folds'] = int(request.form.get(
                    'test_random_cross_validation_folds', 1))

        # gestione validation data splitting

        if request.form.get('validation_splitting_strategy'):
            config['experiment']['splitting']['validation_splitting'] = dict()
            config['experiment']['splitting']['validation_splitting']['strategy'] = request.form.get(
                'validation_splitting_strategy', None)
            if request.form.get('validation_splitting_strategy') == 'fixed_timestamp':
                # gestione validation_fixed_timestamp
                print('Selected a fixed timestamp validation splitting strategy ')
                if request.form.get('test_splitting_strategy') == 'best':
                    config['experiment']['splitting']['test_splitting']['timestamp'] = request.form.get(
                        'test_splitting_strategy')
                else:
                    config['experiment']['splitting']['test_splitting']['timestamp'] = int(request.form.get(
                        'test_splitting_timestamp_value',
                        None))
            elif request.form.get('validation_splitting_strategy') == 'temporal_hold_out':
                print('Selected a temporal hold out validation splitting strategy ')
                if request.form.get('validation_temporal_hold_out_test_ratio'):
                    config['experiment']['splitting']['validation_splitting']['test_ratio'] = float(request.form.get(
                        'validation_temporal_hold_out_test_ratio', None))
                else:
                    config['experiment']['splitting']['validation_splitting']['leave_n_out'] = int(request.form.get(
                        'validation_temporal_hold_out_test_leave_n_out', None))
            elif request.form.get('validation_splitting_strategy') == 'random_subsampling':
                print('Selected a random subsampling validation splitting strategy ')
                if request.form.get('validation_random_subsampling_test_ratio'):
                    config['experiment']['splitting']['validation_splitting']['test_ratio'] = float(request.form.get(
                        'validation_random_subsampling_test_ratio', None))
                else:
                    config['experiment']['splitting']['validation_splitting']['leave_n_out'] = int(request.form.get(
                        'validation_random_subsampling_leave_n_out', None))
                config['experiment']['splitting']['validation_splitting']['folds'] = int(request.form.get(
                    'validation_random_subsampling_folds', 1))
            elif request.form.get('validation_splitting_strategy') == 'random_cross_validation':
                print('Selected a random cross validation splitting strategy ')
                config['experiment']['splitting']['validation_splitting']['folds'] = int(request.form.get(
                    'validation_random_cross_validation_folds', 1))

    elif request.form['loading_strategy'] == 'fixed':

        print('selected fixed strategy')
        _path = '../data/' + hashlib.md5((timestamp_string + '_request/').encode('utf-8'))
        os.makedirs(_path, exist_ok=False)
        train_path = _path + 'test_dataset.tsv'
        test_path = _path + 'test_dataset.tsv'
        request.files.get('train_file').save(train_path)
        request.files.get('test_file').save(test_path)
        config['experiment']['data_config']['train_path'] = train_path
        config['experiment']['data_config']['test_path'] = test_path
        if request.files.get('validation_file'):
            validation_path = _path + 'validation_dataset.tsv'
            request.files.get('validation_file').save(validation_path)
            config['experiment']['data_config']['validation_path'] = validation_path


    elif request.form['loading_strategy'] == 'hierarchy':

        print('selected hierarchy strategy')
        root_folder = '../data/' + hashlib.md5((timestamp_string + '_request/').encode('utf-8'))
        temp_path = '../data/temp/' + timestamp_string + 'zip_dataset'
        request.files['dataset_folder'].save(temp_path)
        with zipfile.ZipFile(temp_path, 'r') as zip_ref:
            zip_ref.extractall(root_folder)
        shutil.rmtree(temp_path)  # pulire la cartella di files temporanei
        config['experiment']['data_config']['root_folder'] = root_folder

    config['experiment']['dataset'] = request.files['dataset_file'].filename
    # così ho preso il nome del dataset passato dall'utente (caso strategia dataset)
    # vedi come funziona con hierarchy e fixed poi

    # gestione salvataggio dati splittati (scegliamo lato backend di salvarli, non sceglie l'utente)
    save_folder = 'splitted_data/' + cript.hexdigest()
    config['experiment']['splitting']['save_on_disk'] = True
    config['experiment']['splitting']['save_folder'] = save_folder

    # selezione del seed random
    if request.form.get('random_seed'):
        config['experiment']['random_seed'] = int(request.form.get('random_seed'))
    # gestione binarize
    config['experiment']['binarize'] = bool(request.form.get('binarize', False))
    # valutare se inserire accelerazione GPU
    return config
