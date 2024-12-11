import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
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

    world_rel_path = 'model/empty_world.world'

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
        arguments=['-d' + os.path.join(get_package_share_directory(pkg_name), 'config', 'config.rviz')]
    )

    #gazebo_ros Node to spawn model
    spawn_model_node = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-topic', 'robot_description', '-entity', robot_xacro_name, '-x', '-18.4387', '-y', "-41.5350", '-z', "-0.7494"],
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

    #Create Empty Launch description object
    launch_description_obj = LaunchDescription()

    #add gazebo_ros launch desc
    launch_description_obj.add_action(gazebo_world_launch)

    #add nodes to launch desc
    launch_description_obj.add_action(spawn_model_node)
    launch_description_obj.add_action(robot_state_pub_node)
    launch_description_obj.add_action(rviz2_launch_node)

    return launch_description_obj
