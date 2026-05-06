import rclpy
from rclpy.node import Node
from rclpy.duration import Duration

from nav_msgs.msg import Path
from geometry_msgs.msg import PoseStamped

import tf2_ros


class EEPathNode(Node):
    def __init__(self):
        super().__init__('ee_path_node')

        # Parameters
        self.declare_parameter('base_frame', 'base_link')
        self.declare_parameter('ee_frame', 'tool0')
        self.declare_parameter('max_points', 1000)

        self.base_frame = self.get_parameter('base_frame').value
        self.ee_frame = self.get_parameter('ee_frame').value
        self.max_points = self.get_parameter('max_points').value

        # ROS2 TF setup
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

        # Publisher
        self.path_pub = self.create_publisher(Path, '/ee_path', 10)

        # Path message
        self.path = Path()
        self.path.header.frame_id = self.base_frame

        # WAIT FOR TF BEFORE STARTING TIMER
        self.get_logger().info(f"Waiting for TF: {self.base_frame} -> {self.ee_frame}")

        self.wait_for_tf()
        
        

        # Timer starts ONLY after TF is ready
        self.timer = self.create_timer(0.1, self.update_path)

        self.get_logger().info("EE Path Node started successfully ✔")

    def wait_for_tf(self):
        timeout = 0.5

        while rclpy.ok():
            try:
                if self.tf_buffer.can_transform(
                    self.base_frame,
                    self.ee_frame,
                    rclpy.time.Time(),
                    timeout=Duration(seconds=timeout)
                ):
                    self.get_logger().info("TF is ready ✔")
                    return
            except Exception as e:
                pass

            self.get_logger().info("Waiting for TF...")
            rclpy.spin_once(self, timeout_sec=0.5)
            self.update_path()

    def update_path(self):
        try:
            transform = self.tf_buffer.lookup_transform(
                self.base_frame,
                self.ee_frame,
                rclpy.time.Time(),
                timeout=Duration(seconds=1.0)
            )

            pose = PoseStamped()
            pose.header.stamp = self.get_clock().now().to_msg()
            pose.header.frame_id = self.base_frame

            pose.pose.position.x = transform.transform.translation.x
            pose.pose.position.y = transform.transform.translation.y
            pose.pose.position.z = transform.transform.translation.z
            pose.pose.orientation = transform.transform.rotation

            self.path.poses.append(pose)

            if len(self.path.poses) > self.max_points:
                self.path.poses.pop(0)

            self.path.header.stamp = pose.header.stamp

            self.path_pub.publish(self.path)

        except Exception as e:
            self.get_logger().warn(
                f"TF lookup failed: {str(e)}",
                throttle_duration_sec=2.0
            )


def main(args=None):
    rclpy.init(args=args)
    node = EEPathNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
