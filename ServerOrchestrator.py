#!/usr/bin/env python3

from flask import render_template
import connexion
	
# Create the application instance
app = connexion.App(__name__, specification_dir='./')
# Read the Orchestrator Api specification Yaml file defined in OpenApi3 to configure the endpoints
app.add_api('OrchestratorApi.yaml',validate_responses=True,strict_validation=True)

# Create a URL route in our application for "/"
@app.route('/')
	
def home():
    """
    This function just responds to the browser URL
    localhost:5000/
    :return:        the rendered template 'home.html'
    """
    return render_template('home.html')

# If we're running in stand alone mode, run the application
if __name__ == '__main__':
    app.run(port=5000, debug=True)

