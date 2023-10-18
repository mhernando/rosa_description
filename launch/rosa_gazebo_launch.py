import os
from ament_index_python.packages import get_package_prefix
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource
import xacro

def xacro_2_urdf_with_absolute_refs(pkg, xacro_model):
    share_dir = get_package_share_directory(pkg)
    xacro_file = os.path.join(share_dir, xacro_model)
    robot_description_config = xacro.process_file(xacro_file)
    urdf_content = robot_description_config.toprettyxml().replace(f'package://{pkg}',share_dir)
    urdf_file = os.path.join(share_dir,f'{xacro_model}.urdf')
    with open(urdf_file, 'w') as file:
        file.write(urdf_content)
    return urdf_file
    
def generate_launch_description():
  urdf_file = xacro_2_urdf_with_absolute_refs('rosa_description','models/rosa/rosa.xacro')
  
  use_sim_time = LaunchConfiguration('use_sim_time', default='false')

  return LaunchDescription([

        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use simulation (Gazebo) clock if true'),

        ExecuteProcess(
            cmd=['gazebo', '--verbose', '-s', 'libgazebo_ros_factory.so'],
            output='screen'),

        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{'use_sim_time': use_sim_time}],
            arguments=[urdf_file]),

 
        Node(
            package='gazebo_ros',
            executable='spawn_entity.py',
            name='urdf_spawner',
            output='screen',
            arguments=["-topic", "/robot_description", "-entity", "rosa"])
  ])
