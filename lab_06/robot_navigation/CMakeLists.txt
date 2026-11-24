cmake_minimum_required(VERSION 3.10)
project(robot_navigation)

find_package(ament_cmake REQUIRED)

install(PROGRAMS
  scripts/patrol.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
