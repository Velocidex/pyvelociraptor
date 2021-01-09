

from velo_pandas import DataFrameQuery as run
import pandas as pd
import time

pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# helper functions
def getdf(vql):
    return pd.DataFrame(run(vql))

def getparams(d):
    o = "dict("
    for i,(k,v) in enumerate(d.items()):
        if i == len(d) - 1: #LAST
            o += k+'="'+v+'")'
            return o
        else:
            o += k+'="'+v+'",'


def run_artifact(hostname, artifact_name, artifact_parameters=None, limit=None, artifact_collect_name=None, verbose=True, timeout=600):
    """
    # [Instantiates artifact for specific hostname and returns it's results as a pandas DataFrame]
    # Examples:

    # >>> df = wrappers.run_artifact("MY_HOSTNAME", "Windows.System.Pslist")

    # [+] Client ID found: C.869eb611eaa5b899
    # [!] Running VQL:

    #         SELECT collect_client(
    #             client_id="C.869eb611eaa5b899", 
    #             artifacts="Windows.System.Pslist") 
    #         AS Flow FROM scope() 

    # [+] Got artifact flow ID: F.BVSSIUHNPUV7E
    # [!] Collecting data using following VQL:

    #         SELECT * FROM source(
    #             artifact='Windows.System.Pslist',
    #             client_id="C.869eb611eaa5b899", flow_id='F.BVSSIUHNPUV7E') 

    # [!] Artifact is running... 0s
    # [!] Artifact is running... 5.3s
    # [+] Done! 11.0s

    # >>> wrappers.run_artifact("NON_EXISTENT_HOSTNAME", "Windows.System.Pslist")
    # [-] Cannot find any Client ID by provided hostname.

    # >>> wrappers.run_artifact("MY_HOSTNAME", "Windows.System.NonExist")
    # [+] Client ID found: C.869eb611eaa5b899
    # [!] Running VQL:

    #         SELECT collect_client(
    #             client_id="C.869eb611eaa5b899", 
    #             artifacts="Windows.System.Pslist123") 
    #         AS Flow FROM scope() 

    # [-] Artifact not instantiated... Check name and parameters!

    # Returns:
    #     [pandas.DataFrane]: [Results of artifact execution.]
    """    

    # FINDING CLIENT_ID FROM HOSTNAME
    cid_query = run(f"""
    SELECT client_id FROM clients(search="{hostname}")
    """)
    if cid_query:
        cid = cid_query["client_id"][0]
        if verbose:
            print(f"[+] Client ID found: {cid}")
    else:
        print("[-] Cannot find any Client ID by provided hostname.")
        return None

    # INSTANTIATING ARTIFACT
    if artifact_parameters:
        start_artifact = f"""
        SELECT collect_client(
            client_id="{cid}", 
            artifacts="{artifact_name}", 
            env={getparams(artifact_parameters)}) 
        AS Flow FROM scope()"""
    else:
        start_artifact = f"""
        SELECT collect_client(
            client_id="{cid}", 
            artifacts="{artifact_name}") 
        AS Flow FROM scope()"""

    if verbose:
        print("[!] Running VQL:")
        print(start_artifact,"\n")
    
    # GETTING RESPONSE METADATA
    meta = run(start_artifact)
    if not meta["Flow"][0]:
        print("[-] Artifact not instantiated... Check name and parameters!")
        return None
    
    flow_id = meta["Flow"][0]["flow_id"]
    if verbose:
        print(f"[+] Got artifact flow ID: {flow_id}")

    # GETTING RESPONSE ACTUAL DATA
    response_df = pd.DataFrame()
    if not artifact_collect_name:
        artifact_collect_name = artifact_name
    if limit:
        vql = f"""
        SELECT * FROM source(
            artifact='{artifact_collect_name}',
            client_id="{cid}", flow_id='{flow_id}')
        LIMIT {limit}"""
    else:
        vql = f"""
        SELECT * FROM source(
            artifact='{artifact_collect_name}',
            client_id="{cid}", flow_id='{flow_id}')"""
    if verbose:
        print(f"[!] Collecting data using following VQL:")
        print(vql,"\n")

    now = time.time()
    delay = 0
    while response_df.empty and delay < timeout:
        if verbose:
            print(f"[!] Artifact is running... {round(delay,2)}s")
    
        response_df = getdf(vql)
        
        time.sleep(5)
        delay = time.time() - now
    
    if verbose:
        if delay < timeout:
            print(f"[+] Done! {round(delay,2)}s\n")
        else:
            print(f"[-] Reached timeout ({timeout}s)... Check artifact status manually in Velociraptor GUI.\n")
    
    return response_df
