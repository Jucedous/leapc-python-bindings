import leap

class MyListener(leap.Listener):
    def __init__(self):
        super().__init__()
        self.prev_x = 0
        self.prev_y = 0
        self.prev_z = 0
        self.threshold = 10
        self.hand_detected = False
        self.offset_x = 0
        self.offset_y = 0
        self.offset_z = 0
        self.change_x = 0
        self.change_y = 0
        self.change_z = 0
        self.fist_detected = False

    def on_connect(self, event):
        try:
            with event.device.open():
                info = event.device.get_info()
        except leap.LeapCannotOpenDeviceError:
            info = event.device.get_info()

        print(f"Found device {info.serial}")

    def on_tracking_event(self, event):
        self.hand_detected = len(event.hands) > 0
        for hand in event.hands:
            x, y, z = hand.palm.position.x, hand.palm.position.y, hand.palm.position.z

            # Check if the hand is making a fist
            if hand.grab_strength == 1.0:
                self.fist_detected = True
                self.offset_x, self.offset_y, self.offset_z = x, y, z
                self.prev_x, self.prev_y, self.prev_z = 0, 0, 0
                print("Fist detected, resetting coordinates to (0, 0, 0)")
                continue
            else:
                self.fist_detected = False

            # Adjust coordinates based on the offset
            adj_x = x - self.offset_x
            adj_y = y - self.offset_y
            adj_z = z - self.offset_z

            # Check if the change in any axis exceeds the threshold
            if (abs(adj_x - self.prev_x) > self.threshold or 
                abs(adj_y - self.prev_y) > self.threshold or 
                abs(adj_z - self.prev_z) > self.threshold):
                adj_x, adj_y, adj_z = round(adj_x, 2), round(adj_y, 2), round(adj_z, 2)
                print(f"({adj_x}, {adj_y}, {adj_z})")
                self.change_x, self.change_y, self.change_z = (adj_x - self.prev_x), (adj_y - self.prev_y), (adj_z - self.prev_z)
                self.prev_x, self.prev_y, self.prev_z = adj_x, adj_y, adj_z