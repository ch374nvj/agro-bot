import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
import xacro

def generate_launch_description():
    #the name that is mentioned in the robot.xacro file ref:line6
    robot_xacro_name = 'differential_drive_robot' 

    #the package/folder name which the launch file resides
    pkg_name = 'gazebo_env'

    #relative paths
    xacro_rel_path = 'model/robot.xacro'

    world_rel_path = 'model/agri_env.world'

    #Absolute paths
    xacro_path = os.path.join(get_package_share_directory(pkg_name), xacro_rel_path)

    world_path = os.path.join(get_package_share_directory(pkg_name), world_rel_path)

    #Get robot description from xacro file
    robot_description = xacro.process_file(xacro_path).toxml()

    #Launch file from gazebo_ros package
    gazebo_rospkg_launch = PythonLaunchDescriptionSource(
        os.path.join(
            get_package_share_directory('gazebo_ros'), 
            'launch', 
            'gazebo.launch.py'
        )
    )

    #Launch description of above
    gazebo_world_launch = IncludeLaunchDescription(
        gazebo_rospkg_launch,
        launch_arguments={
            'world':world_path
        }.items()
    )

    rviz2_launch_node = Node(
        package='rviz2',
        namespace='',
        executable='rviz2',
        name='rviz',
        arguments=[' -d' + os.path.join(get_package_share_directory(pkg_name), 'config', 'config.rviz')],
        parameters=[{'use_sim_time':True}],
    )

    #gazebo_ros Node to spawn model
    spawn_model_node = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-topic', 'robot_description', '-entity', robot_xacro_name, 
        '-x', '-0.08', '-y', "-8.37", '-z', "-0.758", '-Y', "1.57" # -Y => yaw, -R => roll, -P => pitch
        ],
        output='screen'
    )

    #Robot State publisher node
    robot_state_pub_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description' : robot_description,
            'use_sim_time':True
        }]
    )

    # TF for Lidar Scanner; tf b/w dummy and laser_frame
    static_tf_laser_frame_pub_node = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        arguments=['0','0','0','0','0','0','dummy','laser_frame'],
    )

    # Gazebo -> ROS Bridge 
    bridge_params = os.path.join(
        get_package_share_directory('gazebo_env'),
        'params',
        'gz_to_ros.yaml'
    )

    start_gazebo_ros_bridge_cmd = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '--ros-args',
            '-p',
            f'config_file:={bridge_params}',
        ],
        output='screen',
    )

    start_gazebo_ros_image_bridge_cmd = Node(
        package='ros_gz_image',
        executable='image_bridge',
        arguments=['/camera/image_raw'],
        output='screen',
    )

    # SLAM Toolbox launch
    declare_mapper_params_online_async = DeclareLaunchArgument(
        'async_param',
        default_value=os.path.join(get_package_share_directory('gazebo_env'),'config', 'mapper_params_online_async.yaml'),
    )

    mapper_params_online_async_dir = os.path.join(get_package_share_directory('gazebo_env'),'config', 'mapper_params_online_async.yaml')

    launch_online_async_mapper = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('slam_toolbox'), 'launch', 'online_async_launch.py'),
        ),
        launch_arguments=[('slam_params_file', mapper_params_online_async_dir),('use_sim_time','true')],
    )

    #Create Empty Launch description object
    launch_description_obj = LaunchDescription()

    #add gazebo_ros launch desc
    launch_description_obj.add_action(gazebo_world_launch)

    #add nodes to launch desc
    launch_description_obj.add_action(spawn_model_node)
    launch_description_obj.add_action(robot_state_pub_node)
    launch_description_obj.add_action(rviz2_launch_node)
    launch_description_obj.add_action(static_tf_laser_frame_pub_node)
    launch_description_obj.add_action(start_gazebo_ros_bridge_cmd)
    launch_description_obj.add_action(start_gazebo_ros_image_bridge_cmd)
    # launch_description_obj.add_action(declare_mapper_params_online_async)
    launch_description_obj.add_action(launch_online_async_mapper)

    return launch_description_obj
