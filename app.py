import newrelic.agent
from flask import Flask
import logging
import random
import string
from datetime import datetime
import time
import subprocess

# Configurar logger
logging.basicConfig(level=logging.DEBUG, filename='/home/ec2-user/myapp/app.log', format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Inicializar Flask
app = Flask(__name__)

# Configurar New Relic COM VERIFICAÇÃO
try:
    newrelic.agent.initialize('/home/ec2-user/myapp/newrelic.ini')
    NEWRELIC_OK = True
    logger.info("✅ New Relic inicializado com sucesso!")
except Exception as e:
    NEWRELIC_OK = False
    logger.error(f"❌ New Relic FALHOU: {e}")

# FUNÇÃO SEGURA para New Relic
def safe_newrelic(func, *args, **kwargs):
    if NEWRELIC_OK:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.warning(f"New Relic ignorado: {e}")
    return None

# Endpoint home
@app.route('/', methods=['GET'])
def home():
    request_id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    log_metadata = newrelic.agent.get_linking_metadata() if NEWRELIC_OK else {}
   
    logger.info(f"INFO log for home request {request_id}", extra=log_metadata)
    safe_newrelic(newrelic.agent.record_custom_event, 'HomeAccess', {'request_id': request_id, 'timestamp': datetime.now().isoformat()})
    safe_newrelic(newrelic.agent.record_custom_metric, 'Custom/HomeAccess', 1)
   
    return {"status": "success", "message": "Home endpoint accessed", "request_id": request_id}

# Endpoint para gerar log DEBUG
@app.route('/debug', methods=['GET'])
def generate_debug():
    request_id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    log_metadata = newrelic.agent.get_linking_metadata() if NEWRELIC_OK else {}
   
    logger.debug(f"DEBUG log for request {request_id}", extra=log_metadata)
    safe_newrelic(newrelic.agent.record_custom_event, 'DebugLog', {'request_id': request_id, 'timestamp': datetime.now().isoformat()})
    safe_newrelic(newrelic.agent.record_custom_metric, 'Custom/DebugLogGenerated', 1)
   
    return {"status": "success", "message": "DEBUG log generated", "request_id": request_id}

# Endpoint para gerar log INFO
@app.route('/info', methods=['GET'])
def generate_info():
    request_id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    log_metadata = newrelic.agent.get_linking_metadata() if NEWRELIC_OK else {}
   
    logger.info(f"INFO log for request {request_id}", extra=log_metadata)
    safe_newrelic(newrelic.agent.record_custom_event, 'InfoLog', {'request_id': request_id, 'timestamp': datetime.now().isoformat()})
    safe_newrelic(newrelic.agent.record_custom_metric, 'Custom/InfoLogGenerated', 1)
   
    return {"status": "success", "message": "INFO log generated", "request_id": request_id}

# Endpoint para gerar log WARNING
@app.route('/warning', methods=['GET'])
def generate_warning():
    request_id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    log_metadata = newrelic.agent.get_linking_metadata() if NEWRELIC_OK else {}
   
    logger.warning(f"WARNING log for request {request_id}", extra=log_metadata)
    safe_newrelic(newrelic.agent.record_custom_event, 'WarningLog', {'request_id': request_id, 'timestamp': datetime.now().isoformat()})
    safe_newrelic(newrelic.agent.record_custom_metric, 'Custom/WarningLogGenerated', 1)
   
    return {"status": "success", "message": "WARNING log generated", "request_id": request_id}

# ✅ ENDPOINT ERROR - ERROR RATE NO APM GARANTIDO!
@app.route('/error', methods=['GET'])
def generate_error():
    request_id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    log_metadata = newrelic.agent.get_linking_metadata() if NEWRELIC_OK else {}
    
    error_message = f"Simulated ERROR for request {request_id}"
    
    # ✅ TRICK: RAISE ANTES DO TRY - NEW RELIC CAPTURA AUTOMATICAMENTE!
    raise ValueError(error_message)  # 👈 NEW RELIC VÊ ISSO COMO ERRO!

# ✅ HANDLER GLOBAL - CAPTURA TODOS OS ERROS E REGISTRA NO APM!
@app.errorhandler(ValueError)
def handle_value_error(error):
    request_id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    log_metadata = newrelic.agent.get_linking_metadata() if NEWRELIC_OK else {}
    
    # ✅ LOG SEMPRE
    logger.error(f"ERROR log: {error}", exc_info=True, extra=log_metadata)
    
    # ✅ NEW RELIC CUSTOM EVENTS
    if NEWRELIC_OK:
        safe_newrelic(newrelic.agent.record_custom_event, 'ErrorLog', {
            'request_id': request_id, 
            'timestamp': datetime.now().isoformat(), 
            'error_type': 'ValueError',
            'error_message': str(error),
            'status': 'ERROR'
        })
        safe_newrelic(newrelic.agent.record_custom_metric, 'Custom/ErrorLogGenerated', 1)
        safe_newrelic(newrelic.agent.record_custom_metric, 'Custom/Errors/Total', 1)
        logger.info("✅ New Relic ERROR gravado com sucesso via Custom Event!")
    
    # ✅ RETORNA JSON + STATUS 500 = ERROR RATE 100%!
    return {
        "status": "error", 
        "message": str(error), 
        "request_id": request_id
    }, 500

# Endpoint slow
@app.route('/slow', methods=['GET'])
def generate_slow():
    request_id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    log_metadata = newrelic.agent.get_linking_metadata() if NEWRELIC_OK else {}
   
    delay = random.uniform(0.5, 3.0)
    time.sleep(delay)
   
    logger.warning(f"WARNING log for slow request {request_id} with delay {delay:.2f}s", extra=log_metadata)
    safe_newrelic(newrelic.agent.record_custom_event, 'SlowEndpoint', {'request_id': request_id, 'timestamp': datetime.now().isoformat(), 'delay': delay})
    safe_newrelic(newrelic.agent.record_custom_metric, 'Custom/SlowEndpointDelay', delay)
   
    return {"status": "success", "message": f"Slow endpoint accessed with delay {delay:.2f}s", "request_id": request_id}

# Endpoint logs
@app.route('/logs', methods=['GET'])
def generate_all_logs():
    request_id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    log_metadata = newrelic.agent.get_linking_metadata() if NEWRELIC_OK else {}
    
    logger.debug(f"DEBUG log for request {request_id}", extra=log_metadata)
    logger.info(f"INFO log for request {request_id}", extra=log_metadata)
    logger.warning(f"WARNING log for request {request_id}", extra=log_metadata)
   
    try:
        if random.random() < 0.2:
            raise ValueError(f"Simulated ERROR for request {request_id}")
        logger.info("All logs generated successfully", extra=log_metadata)
        safe_newrelic(newrelic.agent.record_custom_event, 'AllLogsEvent', {'request_id': request_id, 'timestamp': datetime.now().isoformat()})
        safe_newrelic(newrelic.agent.record_custom_metric, 'Custom/AllLogsGenerated', 1)
        return {"status": "success", "message": "All logs generated", "request_id": request_id}
    except ValueError as e:
        logger.error(f"ERROR log: {str(e)}", exc_info=True, extra=log_metadata)
        if NEWRELIC_OK:
            safe_newrelic(newrelic.agent.record_custom_event, 'ErrorLog', {
                'request_id': request_id,
                'error_message': str(e),
                'status': 'ERROR'
            })
        return {"status": "error", "message": str(e), "request_id": request_id}, 500

# Endpoint stress
@app.route('/stress', methods=['GET'])
def generate_stress():
    request_id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    log_metadata = newrelic.agent.get_linking_metadata() if NEWRELIC_OK else {}
   
    logger.info(f"Iniciando stress no host para request {request_id}", extra=log_metadata)
    subprocess.Popen(['stress', '--cpu', '2', '--timeout', '60'])
    safe_newrelic(newrelic.agent.record_custom_event, 'StressEvent', {'request_id': request_id, 'timestamp': datetime.now().isoformat()})
   
    return {"status": "success", "message": "Stress iniciado no host (CPU load por 60s)", "request_id": request_id}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
