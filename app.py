import newrelic.agent
from flask import Flask
import logging
import random
import string
from datetime import datetime

# Configurar logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Inicializar Flask
app = Flask(__name__)

# Configurar New Relic
newrelic.agent.initialize('newrelic.ini')

# Endpoint para gerar logs
@app.route('/logs', methods=['GET'])
def generate_logs():
    request_id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    log_metadata = newrelic.agent.get_linking_metadata()

    # Gerar logs de todos os níveis
    logger.debug(f"DEBUG log for request {request_id}", extra=log_metadata)
    logger.info(f"INFO log for request {request_id}", extra=log_metadata)
    logger.warning(f"WARNING log for request {request_id}", extra=log_metadata)
    
    try:
        if random.random() < 0.2:
            raise ValueError(f"Simulated ERROR for request {request_id}")
        logger.info("All logs generated successfully", extra=log_metadata)
        newrelic.agent.record_custom_event('LogEvent', {'request_id': request_id, 'timestamp': datetime.now().isoformat()})
        newrelic.agent.record_custom_metric('Custom/LogGenerated', 1)
        return {"status": "success", "message": "Logs generated", "request_id": request_id}
    except Exception as e:
        newrelic.agent.record_exception()
        logger.error(f"ERROR log: {str(e)}", extra=log_metadata)
        return {"status": "error", "message": str(e)}, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)