// Run with: dotnet script 08_mission_planner_sim.cs  (or compile with csc)
using System;
using System.Collections.Generic;
using System.Threading;

namespace BengalWings.MissionPlanner
{
    public class Waypoint
    {
        public int Id { get; set; }
        public double Lat { get; set; }
        public double Lon { get; set; }
        public float Alt { get; set; }
    }

    class MissionPlannerSim
    {
        static void Main(string[] args)
        {
            Console.WriteLine("==================================================================");
            Console.WriteLine(" 🦅 BENGAL WINGS :: C# HIGH-RELIABILITY MISSION ENGINE (.NET)     ");
            Console.WriteLine("==================================================================");

            var waypoints = new List<Waypoint>
            {
                new Waypoint { Id = 1, Lat = 24.3745, Lon = 88.6042, Alt = 15.0f },
                new Waypoint { Id = 2, Lat = 24.3758, Lon = 88.6055, Alt = 20.0f },
                new Waypoint { Id = 3, Lat = 24.3770, Lon = 88.6070, Alt = 10.0f }
            };

            foreach (var wpt in waypoints)
            {
                Console.WriteLine($"[MISSION EXEC]: Uploading Waypoint #{wpt.Id} -> Lat: {wpt.Lat}, Lon: {wpt.Lon}, Target Alt: {wpt.Alt}m");
                Thread.Sleep(400);
                Console.WriteLine($"[STATUS ACK]: Drone Reached Waypoint #{wpt.Id} Successfully.");
                Console.WriteLine("------------------------------------------------------------------");
            }

            Console.WriteLine("[COMPLETE]: Autonomous Mission Flight Plan Finished Successfully.");
        }
    }
}