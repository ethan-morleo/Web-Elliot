# This is a sample Python script.

# Press Maiusc+F10 to execute it or replace it with your code.
# __variabile__ indica il nome del modulo dove viene chiamata una funzione nel nostro caso l'app
import json
import os

import flask
from flask import Flask, render_template, \
    request, jsonify, \
    send_file, \
    make_response  # import delle funzionalità di flask, render_template serve ad effettuare il rendering di pagine web
from flask_cors import CORS, cross_origin
from controllers.create_config_dict import create_config_dict
from controllers.create_evaluation_config_dict import create_evaluation_config_dict
from controllers.run_marco import run_experiment, run_evaluation
import shutil

app = Flask(
    __name__)  # creo un'istanza dell'applicazione flask con __name__ assegno come argomento il nome del modulo in cui ci troviamo


@app.route("/")  # decoratore che specifica quale percorso poi richiama la def homepage
def homepage():
    return render_template("index.html")


# route di default risponde alle richieste get, in generale noi possiamo definire i metodi mediante un altro argomento nella
# chiamata a funzione che è methods=['POST','GET'] ecc
# grazie a questo render_template vado a cercare direttamente il file di cui specifico il percorso nella cartella templates

@app.route("/contatti")  # decoratore che specifica quale percorso poi richiama la def contatti
def contatti():
    # TODO mettere redirect a pagina di contatto per eventuali contatti a sviluppatori
    return "Contattaci!"


# API usata per il preprocessing del dataset con una richiesta sincrona
# TODO implementare selezione da frontend tra richiesta sincrona/asincrona a seconda delle necessit dell'utente

@app.route("/evaluation")
def evaluation():
    return render_template("evaluation.html")

@app.route("/api/v1/preprocessing", methods=['GET', 'POST'])
def preprocess():
    # request deve essere passato ad una funzione che generi un dizionario contenente le informazioni che ci servono
    if request.method == 'POST':
        print("received a preprocessing request!")  # debug string
        print("trying to create a dataframe with pandas ")
        config = create_config_dict(request)  # creo dizionario di configurazione da cui creare un namespace
        preprocessed_dataset = run_experiment(
            config)  # grazie al dizionario costruirò un namespace che darò al run per ottenere il dataset preprocessato in cambio
        request_no = config['experiment']['splitting']['save_folder'].split('splitted_data/')[1]
        return render_template("results.html", config=config, PP=request_no)


# API usato per effettuare il preprocessing con una richiesta asincrona
@app.route("/api/v1/preprocessing-json", methods=['GET', 'POST'])
def preprocess_json():
    # request deve essere passato ad una funzione che generi un dizionario contenente le informazioni che ci servono
    if request.method == 'POST':
        print("received a preprocessing request!")
        print("trying to create a dataframe with pandas ")
        config = create_config_dict(request)  # creo dizionario di configurazione da cui creare un namespace
        preprocessed_dataset = run_experiment(
            config)  # grazie al dizionario costruirò un namespace che darò al run per ottenere il dataset preprocessato in cambio
        request_no = config['experiment']['splitting']['save_folder'].split('splitted_data/')[1]
        return jsonify(request_no)

@app.route("/api/v1/evaluation", methods=['POST'])
@cross_origin()
def evaluationApi():
    print("richiesta in elaborazione ")
    config, path = create_evaluation_config_dict(request)
    test = run_evaluation(config, path)
    return jsonify({'status':'success', 'result': test, 'path':path}), 201

@app.route("/api/v1/evaluation/download", methods=['GET'])
def download_file():
    path=request.args.get('path')
    output_filename='evaluation_zipped'
    shutil.make_archive(output_filename,'zip',path)
    response = send_file(output_filename + '.zip')
    return response



# API per scaricare il dataset preprocessato
@app.route('/api/v1/preprocessing/download/<request_no>', methods=['GET'])
def send_results(request_no):
    print('received a request of download')
    print(request_no)
    dir_path = 'splitted_data/' + request_no
    output_filename = 'zipped_data/' + request_no
    shutil.make_archive(output_filename, 'zip', dir_path)
    response = send_file(output_filename + '.zip')
    return response



if __name__ == "__main__":
    app.run(debug=True)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
