from pyvelociraptor.velo_pandas import DataFrameQuery
from pyvelociraptor import LoadConfigFile
import pandas as pd
import time

pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

def run_artifact(hostname, artifact_name, config=None, artifact_parameters=None, limit=None, artifact_collect_name=None, verbose=True, timeout=600):
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
    if config is None:
        config = LoadConfigFile()

    # FINDING CLIENT_ID FROM HOSTNAME
    cid_query = DataFrameQuery(f"""
    SELECT client_id FROM clients(search=Hostname)
    """, config=config, Hostname=hostname)
    if cid_query:
        cid = cid_query["client_id"][0]
        if verbose:
            print(f"[+] Client ID found: {cid}")
    else:
        print("[-] Cannot find any Client ID by provided hostname.")
        return None

    # INSTANTIATING ARTIFACT
    start_artifact_query = f"""
        SELECT collect_client(
            client_id=CID, 
            artifacts=Artifact_Name) 
        AS Flow FROM scope()"""
    
    if artifact_parameters:
        meta = DataFrameQuery(start_artifact_query, config=config,
                              CID=cid, Artifact_Name=artifact_name, **artifact_parameters)
    else:
        meta = DataFrameQuery(start_artifact_query, config=config,
                              CID=cid, Artifact_Name=artifact_name)

    if verbose:
        print("[!] Running VQL:")
        print(start_artifact_query\
            .replace("CID",f'"{cid}"')\
            .replace("Artifact_Name",f'"{artifact_name}"'),"\n")
        if artifact_parameters:
            print("[!] Using Query parameters:", end=" ")
            [print(f'{k}="{v}"', end=" ") for k,v in artifact_parameters.items()]
            print("\n")

    # GETTING RESPONSE METADATA    
    try:
        flow_id = meta["Flow"][0]["flow_id"]
    except (TypeError, IndexError):
        print("[-] Artifact not instantiated... Check validity of name or parameters!")
        return None
    
    if verbose:
        print(f"[+] Got artifact flow ID: {flow_id}")

    # GETTING RESPONSE ACTUAL DATA
    response_df = pd.DataFrame()
    if not artifact_collect_name:
        artifact_collect_name = artifact_name
    vql = f"""
        SELECT * FROM source(
            artifact=Artifact_Name,
            client_id=CID, 
            flow_id=Flow_ID)"""
    if limit:
        try:
            vql += f"\n\tLIMIT {int(limit)}"
        except ValueError:
            print("[-] Incorrect 'limit' value... Should be integer!")
            return None

    if verbose:
        print(f"[!] Collecting data using following VQL:")
        print(vql.replace("Artifact_Name", f'"{artifact_collect_name}"')\
                .replace("CID",f'"{cid}"')\
                .replace("Flow_ID", f'"{flow_id}"'),"\n")

    now = time.time()
    delay = 0
    while response_df.empty and delay < timeout:
        if verbose:
            print(f"[!] Artifact is running... {round(delay,2)}s")
    
        response_df = pd.DataFrame(DataFrameQuery(vql, Artifact_Name=artifact_collect_name, 
                                                  CID=cid, Flow_ID=flow_id))
        
        time.sleep(5)
        delay = time.time() - now
    
    if delay < timeout:
        if verbose:
            print(f"[+] Done! {round(delay,2)}s\n")
        return response_df
    else:
        # in case of error/timoeut should print message regardless of 'verbose' value
        print(f"[-] Reached timeout ({timeout}s). Check artifact status manually in Velociraptor's GUI!")
        # to provide VQL query for further analysis only when not printed previously (i.e. verbose=False)
        if not verbose:
            print(vql.replace("Artifact_Name", f'"{artifact_collect_name}"')\
                .replace("CID",f'"{cid}"')\
                .replace("Flow_ID", f'"{flow_id}"'),"\n")
        return None
