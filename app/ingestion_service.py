from app.alert import Alert
from google.cloud import pubsub_v1
import os
import logging
from google.api_core.exceptions import DeadlineExceeded

# Number of messages to pull at once. There is a trade off here: using big numbers might
# Cause the crash of many messages becusae of 1 bad message, and using smaller numbers makes more calls to the API.
MAX_MESSAGES = 10 

# Get the logger set up 
logger = logging.getLogger(__name__)


class IngestionService:
    """
    This class is the service to authenticate with GCP using the service account key path,
    and  pull messages containing lists of IoCs from Pub/Sub transform them into predefined Alert objects, 
    and acknowledge the pub/sub when messages received.
    """
    def __init__(self, subscription_name:str, service_account_path:str):
        """
        This method initializes the IngestionService by configuring authentication with GCP,
        setting the subscription name, and creating a Pub/Sub subscriber client.
        """
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = service_account_path
        self.subscription_name = subscription_name 

        # Create a pub/sub subscriber client 
        self.subscriber = pubsub_v1.SubscriberClient() 

        logger.info("IngestiontService initialized successfully")


    def pull_messages(self,timeout: float=10.0) -> list:
        """
        This method pull messages using the subscriber, and return the messages list
        Parameters: 
       

        Returns:
        list of received messages
        """
        # Try pull, if successful then return the meesages.
        try:
            response = self.subscriber.pull(
                request={"subscription":self.subscription_name,"max_messages":MAX_MESSAGES},
                timeout=timeout
                )
            return response.received_messages
        
        except DeadlineExceeded:
            logger.info("Deadline Exceeded.")
            return []
        # If pull failed, logs an error message, and return an empty list to avoid crash the app
        except Exception as e:
            logger.error(f"failed to pull messages: {e}")
            return []
        
    
    def acknowledge_message_received(self,received_message:str):
        """
        This method gets a message in its argument and acknowledges 
        the pub/sub that the message has received.

        Parameters:
        received_message(str): the message received from transform_messages_to_alerts

        Returns:
        None
        """
        # Try acknowledge
        try:
            self.subscriber.acknowledge(request=
            {"subscription":self.subscription_name,
             "ack_ids":[received_message.ack_id]
             })
        # If not successful, then logs an error message
        except Exception as e:
            logger.error(f"failed to acknowledge message: {e}")

    
    def transform_messages_to_alerts(self, received_messages:list) ->list:
        """
        This method gets the received messages list in its argument, 
        and process the message to alert and append the to the alerts list.
        The function returns the alerts list.

        Parameters:
        received_messages (list): the list of received messages from pulling the messages

        Returns:
        Alerts (list of Alerts)
        """
        alerts = []
        for received_message in received_messages:
            try:
                # Decode the data to make it strings and not bytes
                data = received_message.message.data.decode("utf-8") 

                # Split iocs by blank line as the assignment says.
                ioc = data.strip().split("\n") 
                # Transform the message data to an alert object with the ioc list passed in the argument
                alert = Alert(ioc) 
                alerts.append(alert) 
                # Acknowledge pub/sub that the message has received. 
                self.acknowledge_message_received(received_message=received_message)

            # Account for malformed messages that cannot be processed to Alert objects
            except Exception as e:
                logger.error("Failed to transromed message to an Alert:{e}")
            # Even for the malformed message, acknowledge pub/sub that the message has received. 
            finally:
                self.acknowledge_message_received(received_message=received_message)
            
        return alerts      

        



