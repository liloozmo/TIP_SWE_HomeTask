from app.enrichment_service import EnrichmentService
from app.ingestion_service import IngestionService
from dotenv import load_dotenv
import os
import time
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,  
    format="%(asctime)s - %(levelname)s - %(message)s"
)

load_dotenv()  # Load environment variables from .env file

def main():
    # Retrieve required environment variables
    subscription_name = os.getenv("SUBSCRIPTION_NAME")
    service_account_path = os.getenv("SERVICE_ACCOUNT")

    # Validate required inputs
    if not subscription_name or not service_account_path:
        logging.error("missing environment variables, please check your .env file")
        return
    
    # Initialize services
    ingestion_service = IngestionService(subscription_name=subscription_name, service_account_path=service_account_path)
    enrichment_service = EnrichmentService()

    try:
        while(True):
            logging.info("pulling new messages...")
            messages = ingestion_service.pull_messages()

            if not messages:
                logging.info("no new messages received")
            else:
                logging.info(f"{len(messages)} message(s) received. Proccessing messages to Alerts")
                # Convert raw messages into Alert objects
                alerts = ingestion_service.transform_messages_to_alerts(messages)

                if alerts:
                    logging.info("enriching...")
                    for alert in alerts:
                        # Analyze the alert using VirusTotal and save results
                        report = enrichment_service.analyze_response(alert)
                        enrichment_service.save_report_to_file(report=report)
                    logging.info("alerts processed and reports saved.")
                else:
                    logging.info("messages pulled, but not valid alerts found")

            logging.info("waiting 5 minutes until pulling new alerts... \n")

            # Sleep for 5 minutes before pulling new messages to avoid excessive querying
            time.sleep(300) 
    except KeyboardInterrupt:
        # Gracefully handle keyboard shutdown
        logging.info("Shutdown requested, exiting gracefully ")

if __name__== "__main__":
    main()






