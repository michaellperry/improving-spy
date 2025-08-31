#!/usr/bin/env python3
"""
Demonstration of the simulated time system for spy travel.

This script shows how spies can only take trains that depart after their current
simulated time, and how their location and time are updated when they travel.
"""

import sys
import os
from datetime import datetime, timezone

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from backend.core.database import init_db, get_db
from backend.services.travel_service import TravelService
from backend.repositories.travel_state_repository import TravelStateRepository


def demo_simulated_time():
    """Demonstrate the simulated time system."""
    print("🚂 Spy Travel Simulated Time System Demo")
    print("=" * 50)
    
    # Initialize database
    print("📊 Initializing database...")
    init_db()
    
    # Get database session
    db = next(get_db())
    travel_service = TravelService(db)
    
    # Demo spy ID
    spy_id = "spy_001"
    
    print(f"\n🕵️  Spy {spy_id} starting their journey...")
    
    # Get initial travel state
    print("\n📍 Getting initial travel state...")
    initial_state = travel_service.get_travel_state(spy_id)
    print(f"   Current location: {initial_state.city_id}")
    print(f"   Current simulated time: {initial_state.simulated_time.strftime('%H:%M')}")
    print(f"   Inventory: {initial_state.inventory}")
    
    # Show available train services from Vienna
    print("\n🚆 Available train services from Vienna:")
    services = travel_service.get_available_services("vienna", "today")
    for service in services[:3]:  # Show first 3 services
        print(f"   {service['id']}: {service['origin']} → {service['destination']}")
        print(f"      Departure: {service['dep_local']}, Arrival: {service['arr_local']}")
    
    # Try to travel on a service
    print("\n🎫 Attempting to travel on ICE123 (Vienna → Munich)...")
    travel_result = travel_service.execute_travel(spy_id, "ICE123")
    
    if travel_result["success"]:
        print("✅ Travel successful!")
        print(f"   From: {travel_result['travel_result']['origin']}")
        print(f"   To: {travel_result['travel_result']['destination']}")
        print(f"   Departure: {travel_result['travel_result']['departure_time']}")
        print(f"   Arrival: {travel_result['travel_result']['arrival_time']}")
        print(f"   Duration: {travel_result['travel_result']['duration_minutes']} minutes")
        
        # Show updated state
        print("\n📍 Updated travel state:")
        updated_state = travel_service.get_travel_state(spy_id)
        print(f"   Current location: {updated_state.city_id}")
        print(f"   Current simulated time: {updated_state.simulated_time.strftime('%H:%M')}")
        print(f"   Inventory: {updated_state.inventory}")
        
        # Try to travel back to Vienna (should fail - wrong location)
        print("\n🔄 Attempting to travel back to Vienna from Munich...")
        travel_result2 = travel_service.execute_travel(spy_id, "ICE123")
        if not travel_result2["success"]:
            print(f"❌ Travel failed: {travel_result2['error_message']}")
        
        # Try to take a train that departed before current time
        print("\n⏰ Attempting to take a train that departed earlier...")
        # First, let's find a service that departs early
        early_services = travel_service.get_available_services("munich", "today")
        if early_services:
            early_service = early_services[0]
            print(f"   Trying service: {early_service['id']}")
            print(f"   Departure time: {early_service['dep_local']}")
            
            # Try to travel on this service
            travel_result3 = travel_service.execute_travel(spy_id, early_service['id'])
            if not travel_result3["success"]:
                print(f"❌ Travel failed: {travel_result3['error_message']}")
    
    else:
        print(f"❌ Travel failed: {travel_result['error_message']}")
    
    # Show route planning
    print("\n🗺️  Planning a route from Munich to Paris...")
    route_result = travel_service.plan_route(spy_id, "munich", "paris", {})
    
    if route_result["success"]:
        print("✅ Route planned successfully!")
        print(f"   Total duration: {route_result['total_duration']} minutes")
        print(f"   Departure: {route_result['departure_time']}")
        print(f"   Arrival: {route_result['arrival_time']}")
        print(f"   Spy's current time: {route_result['spy_current_time']}")
        
        # Show itinerary details
        print("\n📋 Itinerary details:")
        for i, leg in enumerate(route_result['itinerary'], 1):
            print(f"   Leg {i}: {leg['origin']} → {leg['destination']}")
            print(f"      Service: {leg['service_id']}")
            print(f"      Departure: {leg['departure_time']}")
            print(f"      Arrival: {leg['arrival_time']}")
            print(f"      Duration: {leg['duration']} minutes")
    else:
        print(f"❌ Route planning failed: {route_result['error_message']}")
    
    print("\n🎯 Demo completed!")
    print("\nKey points demonstrated:")
    print("1. Spies have simulated time that's independent of real clock time")
    print("2. Spies can only take trains that depart after their current simulated time")
    print("3. When they travel, their location and simulated time are updated")
    print("4. Location becomes the train's destination")
    print("5. Simulated time becomes the train's arrival time")
    print("6. Route planning considers the spy's current simulated time and location")


if __name__ == "__main__":
    demo_simulated_time()
