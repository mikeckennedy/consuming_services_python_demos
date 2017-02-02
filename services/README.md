# Public service for modifying demos

This service is running at [consumer_services_api.talkpython.fm](http://consumer_services_api.talkpython.fm/). You can work entirely against the public, deployed version.

I'm just including the code so you have a local version. 

If you want to run the local version, it's a standard Pyramid app so run it as follows:

    >> python3 -m venv --copies ~/sevices_env
    >> . ~/sevices_env/bin/activate
    >> python consuming_services_apis/setup.py develop
    >> serve consuming_services_apis/development.ini