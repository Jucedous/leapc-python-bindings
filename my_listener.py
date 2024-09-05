import leap
import math

class MyListener(leap.Listener):
    def __init__(self):
        super().__init__()
        self.prev_x = 0
        self.prev_y = 0
        self.prev_z = 0
        self.threshold = 20
        self.hand_detected = False
        self.offset_x = 0
        self.offset_y = 0
        self.offset_z = 0
        self.change_x = 0
        self.change_y = 0
        self.change_z = 0
        self.fist_detected = False
        self.prev_yaw = 0
        self.yaw_threshold = 5
        self.thumb_index_flag = -1

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
            
            thumb_tip_x = hand.digits[0].distal.next_joint.x;
            thumb_tip_y = hand.digits[0].distal.next_joint.y;
            thumb_tip_z = hand.digits[0].distal.next_joint.z;
            index_tip_x = hand.digits[1].distal.next_joint.x;
            index_tip_y = hand.digits[1].distal.next_joint.y;
            index_tip_z = hand.digits[1].distal.next_joint.z;

            if hand.grab_strength == 1.0:
                self.fist_detected = True
                self.offset_x, self.offset_y, self.offset_z = x, y, z
                self.prev_x, self.prev_y, self.prev_z = 0, 0, 0
                continue
            else:
                self.fist_detected = False

            adj_x = x - self.offset_x
            adj_y = y - self.offset_y
            adj_z = z - self.offset_z
            
            rotation = hand.palm.orientation
            yaw_radians = math.atan2(2.0 * (rotation.w * rotation.z + rotation.x * rotation.y), 1.0 - 2.0 * (rotation.y * rotation.y + rotation.z * rotation.z))
            yaw_degrees = round(yaw_radians * (180.0 / math.pi), 2)
            
            total_change = abs(adj_x - self.prev_x) + abs(adj_y - self.prev_y) + abs(adj_z - self.prev_z)
            yaw_change = abs(yaw_degrees - self.prev_yaw)
            
            
            distance = math.sqrt((thumb_tip_x - index_tip_x) ** 2 + (thumb_tip_y - index_tip_y) ** 2 + (thumb_tip_z - index_tip_z) ** 2)
            distance = round(distance, 2)

            if (total_change > self.threshold):
                adj_x, adj_y, adj_z = round(adj_x, 2), round(adj_y, 2), round(adj_z, 2)
                # print(f"({adj_x}, {adj_y}, {adj_z})")
                self.change_x, self.change_y, self.change_z = (adj_x - self.prev_x), (adj_y - self.prev_y), (adj_z - self.prev_z)
                self.prev_x, self.prev_y, self.prev_z = adj_x, adj_y, adj_z
            if (yaw_change > self.yaw_threshold):
                self.prev_yaw = yaw_degrees
            if (distance < 40):
                self.thumb_index_flag = 0
            elif (40 < distance < 100):
                self.thumb_index_flag = 1
            elif (distance > 100):
                self.thumb_index_flag = 2