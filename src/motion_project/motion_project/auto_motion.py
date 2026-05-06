import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from moveit_msgs.action import MoveGroup
from moveit_msgs.msg import (
    MotionPlanRequest,
    Constraints,
    PositionConstraint,
    OrientationConstraint,
    PlanningScene,
    CollisionObject
)

from geometry_msgs.msg import PoseStamped, Pose
from shape_msgs.msg import SolidPrimitive
import time


class AutoMotion(Node):

    def __init__(self):
        super().__init__('auto_motion_node')

        # MoveIt action client
        self.client = ActionClient(self, MoveGroup, '/move_action')

        # Planning scene publisher
        self.scene_pub = self.create_publisher(
            PlanningScene,
            '/planning_scene',
            10
        )

        self.timer = self.create_timer(3.0, self.run_once)
        self.done = False

    # ----------------------------
    # ADD SAFE OBSTACLE (IMPORTANT)
    # ----------------------------
    def add_box(self):

        scene = PlanningScene()
        scene.is_diff = True

        box = CollisionObject()
        box.id = "obstacle_box"
        box.header.frame_id = "base_link"

        primitive = SolidPrimitive()
        primitive.type = SolidPrimitive.BOX
        primitive.dimensions = [0.2, 0.2, 0.2]

        pose = Pose()
        # IMPORTANT: keep far from robot workspace center
        pose.position.x = 0.8
        pose.position.y = 0.6
        pose.position.z = 0.3
        pose.orientation.w = 1.0

        box.primitives.append(primitive)
        box.primitive_poses.append(pose)
        box.operation = CollisionObject.ADD

        scene.world.collision_objects.append(box)

        self.scene_pub.publish(scene)

        self.get_logger().info("📦 Obstacle added safely")

    # ----------------------------
    # MAIN
    # ----------------------------
    def run_once(self):

        if self.done:
            return

        self.done = True

        self.get_logger().info("Starting motion pipeline")

        # 1. Add obstacle
        self.add_box()

        # 2. wait for MoveIt to update scene
        time.sleep(2.0)

        # 3. wait for action server
        self.client.wait_for_server()

        goal = MoveGroup.Goal()

        request = MotionPlanRequest()
        request.group_name = "ur5e_arm"

        # VERY IMPORTANT: let MoveIt use current state
        request.start_state.is_diff = True
        request.allowed_planning_time = 5.0

        # ----------------------------
        # TARGET POSE
        # ----------------------------
        pose = PoseStamped()
        pose.header.frame_id = "base_link"

        pose.pose.position.x = 0.4
        pose.pose.position.y = -0.3
        pose.pose.position.z = 0.3
        pose.pose.orientation.w = 1.0

        # ----------------------------
        # POSITION CONSTRAINT
        # ----------------------------
        pc = PositionConstraint()
        pc.header.frame_id = "base_link"
        pc.link_name = "tool0"

        box = SolidPrimitive()
        box.type = SolidPrimitive.BOX
        box.dimensions = [0.05, 0.05, 0.05]

        pc.constraint_region.primitives.append(box)
        pc.constraint_region.primitive_poses.append(pose.pose)
        pc.weight = 1.0

        # ----------------------------
        # ORIENTATION CONSTRAINT
        # ----------------------------
        oc = OrientationConstraint()
        oc.header.frame_id = "base_link"
        oc.link_name = "tool0"
        oc.orientation = pose.pose.orientation
        oc.absolute_x_axis_tolerance = 3.14
        oc.absolute_y_axis_tolerance = 3.14
        oc.absolute_z_axis_tolerance = 3.14
        oc.weight = 1.0

        # ----------------------------
        # GOAL
        # ----------------------------
        constraints = Constraints()
        constraints.position_constraints.append(pc)
        constraints.orientation_constraints.append(oc)

        request.goal_constraints.append(constraints)
        goal.request = request

        # ----------------------------
        # SEND GOAL
        # ----------------------------
        self.get_logger().info("Sending MoveIt goal...")

        future = self.client.send_goal_async(goal)
        future.add_done_callback(self.goal_response_callback)

    # ----------------------------
    def goal_response_callback(self, future):
        goal_handle = future.result()

        if not goal_handle.accepted:
            self.get_logger().error("❌ Goal rejected")
            return

        self.get_logger().info("✅ Goal accepted")

        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.result_callback)

    # ----------------------------
    def result_callback(self, future):
        result = future.result().result
        code = result.error_code.val

        if code == 1:
            self.get_logger().info("🎉 SUCCESS")
        else:
            self.get_logger().error(f"❌ Failed with code: {code}")


def main():
    rclpy.init()
    node = AutoMotion()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()