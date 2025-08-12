# OURPROJ

Note: all system's functional files are inside the UI folder. please ignore any file outside that folder.

## Steps to successfully run the system:

#### 1. Initialize your enviroment
run this `python -m venv .venv` and activate it if have not done that already

#### 2. Install required libraries
run `pip install -r requirements.txt`
*Note: I tried to include all necessary libraries in the requirements.txt file. But in case I missed some and you got errors, please inspect the error message you got, install the missing library, and kindly add it to the requirements.txt to eliminate future problems*

### 3. Prepare docker
1. ensure you have docker installed
2. ensure that docker desktop is active
3. run `docker run -d -p 6333:6333 -p 6334:6334 -v "($pwd)/qdrant_storage:/qdrant/storage:z" qdrant/qdrant`, replacing `($pwd)` with your actuall current working directory

#### 4. Set up your google api key
in agent_prep.py, make sure to configure this line `google_api_key = "YOUR GOOGLE API KEY"`

#### 5. Set up the Qdrant store
if this this the first time you run the system, run `python db_prep.py`.
this step needs to only be run once at the start of the experiments.

#### 6. Run the system
now you're all set. you can run `streamlit run app.py` and interact with the agent through the interface.
