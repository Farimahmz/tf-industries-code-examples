## How to implement a new processor (python version)

#### Prerequisites

1. create python virtual environments. Preferred location: `processors/python/venv`
   `processors/python$ python -m venv venv`

2. active virtual environment
   `processors/python$ source venv/bin/activate`

3. install baseprocessor library `anxprocessor` (for local development)
   `processors/python/base$ pip install .`

4. build baseprocessor image (for processor image builds)
   `processors/python/base$ ./build.sh`

#### Processor development

1. Copy folder `template` to `<your-processor-name>`

2. Implement processor.py (do not forget unit tests)

3. Local testing
    1. run processor locally using `processors/python/run-local.py <folder>`
    2. use tools from `tools` folder
        1. `processors/tools$ config.sh <config.json>  # send config to processor`
        2. `processors/tools$ start.sh    # start processor`
        3. `processors/tools$ stop.sh     # stop processor`
        4. `processors/tools$ reload.sh   # run stop, config and start in a single command`
    3. **Important**: for nearly all use cases you will need a kafka process locally running on your host that can be accessed from the processors, e.g. on `localhost:29092`.

4. Package
    - adjust `requirements.txt` file (using `pip freeze` and `grep import *.py`)
    - adjust `Dockerfile` (only if needed)
    - set version in `_version.py` file
    - run `processors/python$ ./build.sh <processor folder name>`

5. Integration testing
    - load processor into local environment or anx test environment
    - test creation/configuration/starting/stoppping/destroying

6. Release
    - push all source, rebase onto develop
    - create pull request, assign reviewer
