// Build with: colcon build --packages-select bengal_wings_nodes
#include <chrono>
#include <memory>
#include "rclcpp/rclcpp.hpp"
#include "geometry_msgs/msg/pose_stamped.hpp"

using namespace std::chrono_literals;

class DroneTelemetryPublisher : public rclcpp::Node {
public:
    DroneTelemetryPublisher() : Node("bengal_wings_telemetry_node") {
        publisher_ = this->create_publisher<geometry_msgs::msg::PoseStamped>("bengal_wings/drone/pose", 10);
        timer_ = this->create_wall_timer(500ms, std::bind(&DroneTelemetryPublisher::publish_pose, this));
        RCLCPP_INFO(this->get_logger(), "🦅 BENGAL WINGS :: ROS 2 Drone Telemetry Node Started!");
    }

private:
    void publish_pose() {
        auto message = geometry_msgs::msg::PoseStamped();
        message.header.stamp = this->now();
        message.header.frame_id = "map";
        
        // Simulated GPS/SLAM Coordinates
        message.pose.position.x = 24.3745;
        message.pose.position.y = 88.6042;
        message.pose.position.z = 15.5; // Altitude in meters

        RCLCPP_INFO(this->get_logger(), "[ROS2 TX] Drone Altitude: '%.2f m'", message.pose.position.z);
        publisher_->publish(message);
    }

    rclcpp::Publisher<geometry_msgs::msg::PoseStamped>::SharedPtr publisher_;
    rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char * argv[]) {
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<DroneTelemetryPublisher>());
    rclcpp::shutdown();
    return 0;
}