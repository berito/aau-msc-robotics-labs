"""Pick three cubes from a table and drop them into a basket with the FR3 and MoveIt 2.

Joint and pose goals are planned with OMPL's RRT-Connect, using the LMA inverse kinematics solver
for the pose goals, and timed with time-optimal trajectory parameterization. The approach and the
lift are straight-line Cartesian paths.
"""

import sys

from geometry_msgs.msg import Pose
from moveit_msgs.action import ExecuteTrajectory, MoveGroup
from moveit_msgs.msg import (
    AttachedCollisionObject,
    BoundingVolume,
    CollisionObject,
    Constraints,
    JointConstraint,
    MotionPlanRequest,
    MoveItErrorCodes,
    ObjectColor,
    OrientationConstraint,
    PlanningScene,
    PlanningSceneComponents,
    PositionConstraint,
)
from moveit_msgs.srv import ApplyPlanningScene, GetCartesianPath, GetPlanningScene
import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from shape_msgs.msg import SolidPrimitive
from std_msgs.msg import ColorRGBA

ARM_GROUP = 'fr3_arm'
HAND_GROUP = 'fr3_hand'
BASE_FRAME = 'fr3_link0'
TCP_LINK = 'fr3_hand_tcp'
HAND_LINKS = ['fr3_hand', 'fr3_leftfinger', 'fr3_rightfinger']

READY_JOINTS = [0.0, -0.785, 0.0, -2.356, 0.0, 1.571, 0.785]
HAND_OPEN = 0.035
# Fingers are commanded past the cube faces to build up grip force in Gazebo.
GRIP_SQUEEZE = 0.005

# Must match worlds/pick_place.sdf.
BASKET_SIZE = 0.2
BASKET_HEIGHT = 0.08
BASKET_WALL = 0.01

DROP_CLEARANCE = 0.015
DROP_OFFSETS = [(-0.045, -0.045), (0.045, -0.045), (0.0, 0.045)]

TABLE_COLOR = (0.55, 0.35, 0.2)
BASKET_COLOR = (0.3, 0.3, 0.35)
CUBE_COLORS = [(0.8, 0.1, 0.1), (0.1, 0.7, 0.1), (0.1, 0.2, 0.8)]

DOWN = (1.0, 0.0, 0.0, 0.0)
NO_ROTATION = (0.0, 0.0, 0.0, 1.0)

PLANNING_ATTEMPTS = 3
ERROR_NAMES = {value: name for name, value in vars(MoveItErrorCodes).items()
               if name.isupper() and isinstance(value, int)}


def make_pose(x, y, z, orientation=DOWN):
    pose = Pose()
    pose.position.x, pose.position.y, pose.position.z = x, y, z
    (pose.orientation.x, pose.orientation.y,
     pose.orientation.z, pose.orientation.w) = orientation
    return pose


def make_object(object_id, boxes, frame_id):
    """Collision object made of (size, pose) boxes."""
    obj = CollisionObject()
    obj.id = object_id
    obj.header.frame_id = frame_id
    obj.primitives = [SolidPrimitive(type=SolidPrimitive.BOX, dimensions=list(size))
                      for size, _ in boxes]
    obj.primitive_poses = [pose for _, pose in boxes]
    obj.operation = CollisionObject.ADD
    return obj


def make_color(object_id, rgb):
    return ObjectColor(id=object_id, color=ColorRGBA(r=rgb[0], g=rgb[1], b=rgb[2], a=1.0))


class PickPlace(Node):

    def __init__(self, node_name='pick_place'):
        super().__init__(node_name)
        self.declare_parameter('cube_positions', [0.45, -0.30, 0.62, -0.30, 0.53, -0.12])
        self.declare_parameter('basket_xy', [0.55, 0.25])
        self.declare_parameter('table_height', 0.2)
        self.declare_parameter('cube_size', 0.04)
        self.declare_parameter('approach_height', 0.12)
        self.declare_parameter('velocity_scaling', 0.3)

        flat = self.get_parameter('cube_positions').value
        self.cubes = {f'cube_{i + 1}': (flat[2 * i], flat[2 * i + 1])
                      for i in range(len(flat) // 2)}
        self.colors = {'table': TABLE_COLOR, 'basket': BASKET_COLOR}
        self.colors.update(zip(self.cubes, CUBE_COLORS))
        self.basket_xy = self.get_parameter('basket_xy').value
        self.table_height = self.get_parameter('table_height').value
        self.cube_size = self.get_parameter('cube_size').value
        self.approach = self.get_parameter('approach_height').value
        self.speed = self.get_parameter('velocity_scaling').value

        if len(self.cubes) > len(DROP_OFFSETS):
            raise ValueError(f'The basket holds at most {len(DROP_OFFSETS)} cubes')

        self.move_group = ActionClient(self, MoveGroup, 'move_action')
        self.execute = ActionClient(self, ExecuteTrajectory, 'execute_trajectory')
        self.cartesian = self.create_client(GetCartesianPath, 'compute_cartesian_path')
        self.scene = self.create_client(ApplyPlanningScene, 'apply_planning_scene')
        self.get_scene = self.create_client(GetPlanningScene, 'get_planning_scene')

        self.get_logger().info('Waiting for MoveIt')
        self.move_group.wait_for_server()
        self.execute.wait_for_server()
        self.cartesian.wait_for_service()
        self.scene.wait_for_service()
        self.get_scene.wait_for_service()

    def apply_scene(self, scene):
        scene.is_diff = True
        scene.robot_state.is_diff = True
        request = ApplyPlanningScene.Request(scene=scene)
        return self.call(self.scene.call_async(request)).success

    def clear_scene(self):
        components = PlanningSceneComponents(
            components=PlanningSceneComponents.WORLD_OBJECT_NAMES
            | PlanningSceneComponents.ROBOT_STATE_ATTACHED_OBJECTS)
        current = self.call(self.get_scene.call_async(
            GetPlanningScene.Request(components=components))).scene

        scene = PlanningScene()
        for attached in current.robot_state.attached_collision_objects:
            detach = AttachedCollisionObject(link_name=attached.link_name)
            detach.object.id = attached.object.id
            detach.object.operation = CollisionObject.REMOVE
            scene.robot_state.attached_collision_objects.append(detach)
        object_ids = {o.id for o in current.world.collision_objects}
        object_ids |= {a.object.id for a in current.robot_state.attached_collision_objects}
        for object_id in object_ids:
            remove = CollisionObject(id=object_id, operation=CollisionObject.REMOVE)
            remove.header.frame_id = BASE_FRAME
            scene.world.collision_objects.append(remove)
        return self.apply_scene(scene) if object_ids else True

    def cube_object(self, cube_id, x, y, z):
        size = (self.cube_size,) * 3
        return make_object(cube_id, [(size, make_pose(x, y, z, NO_ROTATION))], BASE_FRAME)

    def basket_object(self):
        x, y = self.basket_xy
        z = self.table_height
        s, h, t = BASKET_SIZE, BASKET_HEIGHT, BASKET_WALL
        wall = s / 2 - t / 2
        boxes = [
            ((s, s, t), make_pose(x, y, z + t / 2, NO_ROTATION)),
            ((t, s, h), make_pose(x + wall, y, z + h / 2, NO_ROTATION)),
            ((t, s, h), make_pose(x - wall, y, z + h / 2, NO_ROTATION)),
            ((s, t, h), make_pose(x, y + wall, z + h / 2, NO_ROTATION)),
            ((s, t, h), make_pose(x, y - wall, z + h / 2, NO_ROTATION)),
        ]
        return make_object('basket', boxes, BASE_FRAME)

    def add_objects(self):
        h = self.table_height
        table = make_object('table', [((0.4, 0.9, h), make_pose(0.55, 0.0, h / 2, NO_ROTATION))],
                            BASE_FRAME)
        scene = PlanningScene()
        scene.world.collision_objects = [table, self.basket_object()] + [
            self.cube_object(cube_id, x, y, h + self.cube_size / 2)
            for cube_id, (x, y) in self.cubes.items()
        ]
        scene.object_colors = [make_color(i, rgb) for i, rgb in self.colors.items()]
        return self.apply_scene(scene)

    def attach(self, cube_id):
        # Reusing the world object's id moves the cube from the world to the robot.
        attached = AttachedCollisionObject(link_name=TCP_LINK, touch_links=HAND_LINKS)
        attached.object = make_object(
            cube_id, [((self.cube_size,) * 3, make_pose(0.0, 0.0, 0.0, NO_ROTATION))], TCP_LINK)
        scene = PlanningScene()
        scene.robot_state.attached_collision_objects = [attached]
        return self.apply_scene(scene)

    def release_into_basket(self, cube_id, x, y):
        """Detach the cube and put it where it lands on the basket floor."""
        detach = AttachedCollisionObject(link_name=TCP_LINK)
        detach.object.id = cube_id
        detach.object.operation = CollisionObject.REMOVE
        scene = PlanningScene()
        scene.robot_state.attached_collision_objects = [detach]
        scene.world.collision_objects = [self.cube_object(
            cube_id, x, y, self.table_height + BASKET_WALL + self.cube_size / 2)]
        scene.object_colors = [make_color(cube_id, self.colors[cube_id])]
        return self.apply_scene(scene)

    def plan_and_execute(self, group, goal):
        request = MotionPlanRequest()
        request.group_name = group
        request.num_planning_attempts = 5
        request.allowed_planning_time = 5.0
        request.max_velocity_scaling_factor = self.speed
        request.max_acceleration_scaling_factor = self.speed
        request.goal_constraints = [goal]
        action_goal = MoveGroup.Goal(request=request)
        action_goal.planning_options.plan_only = False
        for attempt in range(1, PLANNING_ATTEMPTS + 1):
            code = self.send_action(self.move_group, action_goal).error_code.val
            if code == MoveItErrorCodes.SUCCESS:
                return True
            self.get_logger().warn(
                f'MoveIt returned {ERROR_NAMES.get(code, code)} '
                f'(attempt {attempt}/{PLANNING_ATTEMPTS})')
        return False

    def move_joints(self, group, names, positions):
        goal = Constraints()
        goal.joint_constraints = [
            JointConstraint(joint_name=name, position=position,
                            tolerance_above=0.001, tolerance_below=0.001, weight=1.0)
            for name, position in zip(names, positions)
        ]
        return self.plan_and_execute(group, goal)

    def move_to_ready(self):
        names = [f'fr3_joint{i}' for i in range(1, 8)]
        return self.move_joints(ARM_GROUP, names, READY_JOINTS)

    def set_gripper(self, finger_position):
        return self.move_joints(HAND_GROUP, ['fr3_finger_joint1'], [finger_position])

    def move_to_pose(self, pose):
        region = BoundingVolume()
        region.primitives = [SolidPrimitive(type=SolidPrimitive.SPHERE, dimensions=[0.002])]
        region.primitive_poses = [pose]
        position = PositionConstraint(link_name=TCP_LINK, constraint_region=region, weight=1.0)
        position.header.frame_id = BASE_FRAME
        orientation = OrientationConstraint(
            link_name=TCP_LINK, orientation=pose.orientation, weight=1.0,
            absolute_x_axis_tolerance=0.01, absolute_y_axis_tolerance=0.01,
            absolute_z_axis_tolerance=0.01)
        orientation.header.frame_id = BASE_FRAME
        goal = Constraints(position_constraints=[position],
                           orientation_constraints=[orientation])
        return self.plan_and_execute(ARM_GROUP, goal)

    def move_straight(self, pose):
        request = GetCartesianPath.Request()
        request.header.frame_id = BASE_FRAME
        request.start_state.is_diff = True
        request.group_name = ARM_GROUP
        request.link_name = TCP_LINK
        request.waypoints = [pose]
        request.max_step = 0.005
        request.avoid_collisions = True
        request.max_velocity_scaling_factor = self.speed / 2
        request.max_acceleration_scaling_factor = self.speed / 2
        response = self.call(self.cartesian.call_async(request))
        if response.fraction < 0.99:
            self.get_logger().error(f'Straight-line path only {response.fraction:.0%} feasible')
            return False
        result = self.send_action(self.execute,
                                  ExecuteTrajectory.Goal(trajectory=response.solution))
        return result.error_code.val == MoveItErrorCodes.SUCCESS

    def cube_steps(self, cube_id, cube_xy, drop_offset):
        grasp_z = self.table_height + self.cube_size / 2
        above_z = grasp_z + self.approach
        drop_x = self.basket_xy[0] + drop_offset[0]
        drop_y = self.basket_xy[1] + drop_offset[1]
        drop_z = self.table_height + BASKET_HEIGHT + DROP_CLEARANCE + self.cube_size / 2
        return [
            (f'Move above {cube_id}', lambda: self.move_to_pose(make_pose(*cube_xy, above_z))),
            (f'Approach {cube_id}', lambda: self.move_straight(make_pose(*cube_xy, grasp_z))),
            (f'Attach {cube_id} to gripper', lambda: self.attach(cube_id)),
            ('Close gripper', lambda: self.set_gripper(self.cube_size / 2 - GRIP_SQUEEZE)),
            (f'Lift {cube_id}', lambda: self.move_straight(make_pose(*cube_xy, above_z))),
            ('Move over basket', lambda: self.move_to_pose(make_pose(drop_x, drop_y, drop_z))),
            ('Open gripper', lambda: self.set_gripper(HAND_OPEN)),
            (f'Release {cube_id} into basket',
             lambda: self.release_into_basket(cube_id, drop_x, drop_y)),
        ]

    def run(self):
        steps = [
            ('Clear planning scene', self.clear_scene),
            ('Move to ready pose', self.move_to_ready),
            ('Place table, basket and cubes', self.add_objects),
            ('Open gripper', lambda: self.set_gripper(HAND_OPEN)),
        ]
        for (cube_id, cube_xy), drop_offset in zip(self.cubes.items(), DROP_OFFSETS):
            steps += self.cube_steps(cube_id, cube_xy, drop_offset)
        steps.append(('Return to ready pose', self.move_to_ready))

        for number, (name, step) in enumerate(steps, start=1):
            self.get_logger().info(f'[{number}/{len(steps)}] {name}')
            if not step():
                self.get_logger().error(f'Step failed: {name}')
                return False
        self.get_logger().info(f'All {len(self.cubes)} cubes are in the basket')
        return True

    def call(self, future):
        rclpy.spin_until_future_complete(self, future)
        return future.result()

    def send_action(self, client, goal):
        goal_handle = self.call(client.send_goal_async(goal))
        if not goal_handle.accepted:
            raise RuntimeError('Goal rejected')
        return self.call(goal_handle.get_result_async()).result


def main(args=None):
    rclpy.init(args=args)
    node = PickPlace()
    try:
        ok = node.run()
    finally:
        node.destroy_node()
        rclpy.shutdown()
    sys.exit(0 if ok else 1)


def add_scene(args=None):
    """Put the table, basket and cubes into the planning scene and exit."""
    rclpy.init(args=args)
    node = PickPlace('add_scene')
    try:
        ok = node.clear_scene() and node.add_objects()
        node.get_logger().info('Planning scene ready' if ok else 'Could not set up the scene')
    finally:
        node.destroy_node()
        rclpy.shutdown()
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
