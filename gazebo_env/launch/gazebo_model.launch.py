import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
import xacro

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

