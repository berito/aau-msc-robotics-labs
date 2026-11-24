cmake_minimum_required(VERSION 3.10)
project(turtlebot3_sim)

find_package(ament_cmake REQUIRED)

install(DIRECTORY
  config
  launch
  maps
  models
  rviz
  urdf
  worlds
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
