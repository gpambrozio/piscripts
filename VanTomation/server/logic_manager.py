from base import SenderReceiver, logger


class LogicManager(SenderReceiver):
    def __init__(self):
        SenderReceiver.__init__(self, "Logic")
        self.current_state = {}
        self.is_moving = False


    def broadcast_received(self, broadcast):
        if broadcast.destination is None:
            self.current_state[broadcast.prop]= broadcast.value

        if broadcast.prop == "Speed" and broadcast.value > 10 and not self.is_moving:
            self.add_broadcast(None, "Moving", True)
            self.is_moving = True
        elif broadcast.prop == "Speed" and broadcast.value < 3 and self.is_moving:
            self.add_broadcast(None, "Moving", False)
            self.is_moving = False
