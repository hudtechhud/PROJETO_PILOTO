import newrelic.agent
from flask import Flask
import logging
import random
import string
from datetime import datetime
import time

# Configurar logger
logging.basicConfig(level=logging.DEBUG, filename='app.log', format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Inicializar Flask
app = Flask(__name__)

# Configurar New Relic
newrelic.agent.initialize('newrelic.ini')

# Endpoint home para gerar log INFO e throughput básico
@app.route('/', methods=['GET'])
def home():
    request_id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    log_metadata = newrelic.agent.get_linking_metadata()
    
    logger.info(f"INFO log for home request {request_id}", extra=log_metadata)
    newrelic.agent.record_custom_event('HomeAccess', {'request_id': request_id, 'timestamp': datetime.now().isoformat()})
    newrelic.agent.record_custom_metric('Custom/HomeAccess', 1)
    
    return {"status": "success", "message": "Home endpoint accessed", "request_id": request_id}

# Endpoint para gerar log DEBUG
@app.route('/debug', methods=['GET'])
def generate_debug():
    request_id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    log_metadata = newrelic.agent.get_linking_metadata()
    
    logger.debug(f"DEBUG log for request {request_id}", extra=log_metadata)
    newrelic.agent.record_custom_event('DebugLog', {'request_id': request_id, 'timestamp': datetime.now().isoformat()})
    newrelic.agent.record_custom_metric('Custom/DebugLogGenerated', 1)
    
    return {"status": "success", "message": "DEBUG log generated", "request_id": request_id}

# Endpoint para gerar log INFO
@app.route('/info', methods=['GET'])
def generate_info():
    request_id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    log_metadata = newrelic.agent.get_linking_metadata()
    
    logger.info(f"INFO log for request {request_id}", extra=log_metadata)
    newrelic.agent.record_custom_event('InfoLog', {'request_id': request_id, 'timestamp': datetime.now().isoformat()})
    newrelic.agent.record_custom_metric('Custom/InfoLogGenerated', 1)
    
    return {"status": "success", "message": "INFO log generated", "request_id": request_id}

# Endpoint para gerar log WARNING
@app.route('/warning', methods=['GET'])
def generate_warning():
    request_id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    log_metadata = newrelic.agent.get_linking_metadata()
    
    logger.warning(f"WARNING log for request {request_id}", extra=log_metadata)
    newrelic.agent.record_custom_event('WarningLog', {'request_id': request_id, 'timestamp': datetime.now().isoformat()})
    newrelic.agent.record_custom_metric('Custom/WarningLogGenerated', 1)
    
    return {"status": "success", "message": "WARNING log generated", "request_id": request_id}

# Endpoint para gerar log ERROR com exceção simulada
@app.route('/error', methods=['GET'])
def generate_error():
    request_id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    log_metadata = newrelic.agent.get_linking_metadata()
    
    try:
        raise ValueError(f"Simulated ERROR for request {request_id}")
    except Exception as e:
        newrelic.agent.record_exception()
        logger.error(f"ERROR log: {str(e)}", exc_info=True, extra=log_metadata)
        newrelic.agent.record_custom_event('ErrorLog', {'request_id': request_id, 'timestamp': datetime.now().isoformat(), 'error': str(e)})
        newrelic.agent.record_custom_metric('Custom/ErrorLogGenerated', 1)
        return {"status": "error", "message": str(e)}, 500

# Endpoint para simular lentidão e gerar throughput variado com log WARNING
@app.route('/slow', methods=['GET'])
def generate_slow():
    request_id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    log_metadata = newrelic.agent.get_linking_metadata()
    
    delay = random.uniform(0.5, 3.0)  # Delay aleatório para simular variações de performance
    time.sleep(delay)
    
    logger.warning(f"WARNING log for slow request {request_id} with delay {delay:.2f}s", extra=log_metadata)
    newrelic.agent.record_custom_event('SlowEndpoint', {'request_id': request_id, 'timestamp': datetime.now().isoformat(), 'delay': delay})
    newrelic.agent.record_custom_metric('Custom/SlowEndpointDelay', delay)
    
    return {"status": "success", "message": f"Slow endpoint accessed with delay {delay:.2f}s", "request_id": request_id}

# Endpoint legado para gerar todos os logs (mantido para compatibilidade)
@app.route('/logs', methods=['GET'])
def generate_all_logs():
    request_id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    log_metadata = newrelic.agent.get_linking_metadata()

    logger.debug(f"DEBUG log for request {request_id}", extra=log_metadata)
    logger.info(f"INFO log for request {request_id}", extra=log_metadata)
    logger.warning(f"WARNING log for request {request_id}", extra=log_metadata)
    
    try:
        if random.random() < 0.2:
            raise ValueError(f"Simulated ERROR for request {request_id}")
        logger.info("All logs generated successfully", extra=log_metadata)
        newrelic.agent.record_custom_event('AllLogsEvent', {'request_id': request_id, 'timestamp': datetime.now().isoformat()})
        newrelic.agent.record_custom_metric('Custom/AllLogsGenerated', 1)
        return {"status": "success", "message": "All logs generated", "request_id": request_id}
    except Exception as e:
        newrelic.agent.record_exception()
        logger.error(f"ERROR log: {str(e)}", exc_info=True, extra=log_metadata)
        return {"status": "error", "message": str(e)}, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
