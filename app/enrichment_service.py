from app.alert import Alert
import os
import requests
from dotenv import load_dotenv
import json
from app.utils import get_current_time,ensure_output_directory
import logging


# Get the logger setup.
logger= logging.getLogger(__name__)

# Get context from .env file
load_dotenv() 

class EnrichmentService:
    """
    This class service queries VirusTotal for each ioc in the alert,
    process the response and determine if it's malicious or not, 
    Then analyze the alert to determine it's severity create the
    full report by the results, and lastly save the report to a .json file
    with execution time as part of the file name.
    """
    def __init__(self):
        """
        This method initilizes the EnrichmentService by
        setting the headers, and setting its base urlt
        """
        self.headers = {"x-apikey":os.getenv("VIRUSTOTAL_API_KEY")}
        self.base_url = "https://www.virustotal.com/api/v3/ip_addresses/"
        logger.info("EnrichmentService initialized successfully\n")

    def query_virustotal(self,ioc:str)->dict:
        """
        This method query VirusTotal API for the given IoC and return the full JSON response.

        Parameters:
        ioc (str)

        Returns:
        a json repsonse dictionary from querying VirusTotal
        """
        # Add the specific ioc to the base url
        url = self.base_url + ioc 

        # Try query the VirusTotal api, if successful then return the response,json()
        try:
            response = requests.get(url,headers=self.headers)

            # Raise error if bad response status code
            response.raise_for_status() 
            return response.json()
        
        # If query is not successful, logs an error message, and return an empty dict
        except Exception as e:
            logger.error(f"Failed to query VirusTotal for {ioc} becasue of: {e}")
            return {}
        
    def is_ioc_malicious_from_response (self,json_response:dict) ->bool:
        """
        This method takes the response from the api call and determine
        if ioc is meliciouss

        Parameters:
        json_response (dict): the json dictionary response
        returned from querying VirusToal

        Returns:
        True if ioc is malicious, False otherwise
        """
        try:
            # Get malicious value
            is_malicious = json_response.get("data",{}).get("attributes",{}).get("last_analysis_stats",{}).get("malicious") 

            # Return true if is_malicious(malicious value) is bigger than 0, false otheriwse
            return is_malicious > 0  
        
        # If there is an exception, log an error message and return false.
        except Exception as e:
            logger.error(f"failed to determine if malicious or not: {e}")
            return False
        
    def analyze_response(self,alert:Alert)->dict:
        """
        This method analyze each Ioc in the alert using VirusTotal and calculate severity.

        Parameters:
        alert (Alert): Alert object with a list of Iocs.

        Returns:
        dict: report containing alert ID, severity score, and IoC analysis.
        """
        malicious_counter = 0
        results = []
        for ioc in alert.ioc:
            # Get response for the current IoC
            json_response = self.query_virustotal(ioc=ioc) 
            is_malicious = self.is_ioc_malicious_from_response(json_response=json_response)
            results.append({
                "IoCs":ioc,
                "IsMalicious":is_malicious
                })
            if is_malicious:
                # Increase the malicious iocs counts.
                malicious_counter += 1 

        # Calculate severity as a percentage of malicious IoCs
        severity = int((malicious_counter/len(alert.ioc)) * 100) if alert.ioc else 0
        # Beside updating the severity in the report, also updating the alert.
        alert.severity = severity 
        report={
            "AlertId":alert.id,
            "Severity":severity,
            "IoCs":results
            }
        return report
    
    def save_report_to_file(self,report:dict):
        """
        Save the report dictionary to a json file with a with execution time 
        as part of the file name. filename.

        Parameters:
        report (dict): the report generated from analyzing the alert.

        Returns:
        None
        """
        #Get the current time
        timestamp = get_current_time() 

        directory = "app/output"

        #Make the "output" directory if does not exist
        ensure_output_directory(directory=directory) 

        #Create the json file name with the current time
        name_of_file= os.path.join(directory,f"report_{timestamp}.json") 

        try:
            with open(name_of_file,"w") as file:
                # Save the report to the json file
                json.dump(report, file, indent=4) 
            logger.info(f"report saved to {name_of_file}")
        except Exception as e:
            logger.error(f"Failed to save report to file: {e}")





        