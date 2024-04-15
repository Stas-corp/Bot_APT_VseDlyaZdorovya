from datetime import datetime

class Manager:
    def __init__(self, 
                 user_id: str, 
                 delivery_type: str, 
                 order: str, 
                 adress: str, 
                 date: datetime) -> None:
        self.user_id = user_id
        self.delivery_type = delivery_type
        self.order = order
        self.adress = adress
        self.date = date
        self.order_completed = False