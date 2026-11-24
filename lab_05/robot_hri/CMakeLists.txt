cmake_minimum_required(VERSION 3.10)
project(robot_hri)

find_package(ament_cmake REQUIRED)

install(PROGRAMS
  scripts/command_driver.py
  scripts/speech_commands.py
  scripts/gesture_commands.py
  DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY launch DESTINATION share/${PROJECT_NAME})

# downloaded by setup.sh
install(DIRECTORY models DESTINATION share/${PROJECT_NAME} OPTIONAL)

ament_package()
