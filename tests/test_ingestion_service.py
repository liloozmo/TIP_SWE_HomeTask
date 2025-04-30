from app.ingestion_service import IngestionService
import unittest
from unittest.mock import patch,MagicMock
from app.alert import Alert

class TestIngestionService(unittest.TestCase):
    """
    Unit tests for the IngestionService class to validate 
    message pulling, transformation, and acknowledgment.
    """

    @patch("app.ingestion_service.pubsub_v1.SubscriberClient") #patching a fake subscriber client
    def setUp(self, mock_subscriber_client):
        """
        Set up a mocked IngestionService instance for testing.
        """
        self.mock_subscriber = MagicMock() # Assigning a mock subscriber
        mock_subscriber_client.return_value = self.mock_subscriber #make the return value of pubsub_v1.SubscriberClien the mocked subscriber
        
        self.ingestion_service = IngestionService(
            subscription_name="path/to/fake_subscription_name",
            service_account_path= "path/to/fake_service_acount_path.json"
            )
        
    def test_pull_messages(self):
        """
        Test that pulling messages returns the expected number of messages
        """
        # Arrange
        mock_message = MagicMock()  # mock a message
        self.mock_subscriber.pull.return_value.received_messages = [mock_message]

        #Act
        messages = self.ingestion_service.pull_messages()

        # Assert
        self.assertEqual(len(messages),1)
        self.assertEqual(messages[0],mock_message)

    def test_empty_pull_messages(self):
        """
        Test that pulling no messages returns an empty list.
        """
        # Arrange
        self.mock_subscriber.pull.return_value.received_messages = []

        # Act
        messages = self.ingestion_service.pull_messages()

        # assert
        self.assertEqual(messages,[],"messages should be empty as no messages received")

    def test_empty_pull_messages_failure(self):
        """
        Test that an exception during pull returns an empty list.
        """
        # arrange
        self.mock_subscriber.pull.side_effect = Exception("failed to pull")

        # Act
        messages = self.ingestion_service.pull_messages()

        # ssert
        self.assertEqual(messages,[],"should return an empty list in case of failure")

    def test_transform_messages_to_alerts(self):
        """
        Test that raw message data is correctly transformed into an Alert object.
        """
        # arrange
        mock_message = MagicMock()
        mock_message.message.data.decode.return_value = "1.2.3.4\n5.6.7.8"
        mock_message.ack_id = "fake-ack-id"

        # act
        alerts = self.ingestion_service.transform_messages_to_alerts([mock_message])

        alert = alerts[0] # assignt alert to be the first and only alert

        # assert
        self.assertEqual(len(alerts),1,"there should be 1 alert only")
        self.assertIsInstance(alert,Alert,"message should transfrom to Alert object")
        self.assertEqual(alert.ioc, ["1.2.3.4","5.6.7.8"],"iocs did not assigned properly")
        self.assertIsInstance(alert.id, str,"alert id should be a string")

    def test_acknowledge_message_received(self):
        """
        Test that acknowledging a message calls the acknowledge method with correct arguments.
        """
        # Arrange
        message = MagicMock()
        message.ack_id = "fake-ack-id"

        # Act
        self.ingestion_service.acknowledge_message_received(received_message=message)

        #Assert
        self.mock_subscriber.acknowledge.assert_called_once_with(
            request={"subscription":self.ingestion_service.subscription_name,"ack_ids":[message.ack_id]}
        )

    def test_acknowledge_message_received_failure(self):
        """
        Test that an exception during acknowledgment is handled gracefully.
        """
        #Arrange
        mock_message = MagicMock()
        mock_message.ack_id = "fake-ack-id"
        self.mock_subscriber.acknowledge.side_effect = Exception("failed to acknowledge")
        
        #Act
        result = self.ingestion_service.acknowledge_message_received(mock_message)

        #Assert 
        self.mock_subscriber.acknowledge.assert_called_once()