# Import uuid for generating unique string to alert id
import uuid 

class Alert:
    """
    This Alert class has an initialization method for alert with id, ioc
    and severirty attributes by receiving list of Ioc's in the argument and assign 
    them to the alert Iocs when creating the object 
    """
    def __init__(self,ioc:list):
        """
        This method initilize the alert object with unique string id,
        severity = None and assign the ioc list to alert.ioc

        Parameters:
        ioc (list): list of iocs

        Returns:
        None
        """
        # Creats unique id for each alert
        self.id = str(uuid.uuid4()) 
        self.severity = None
        self.ioc = ioc
        