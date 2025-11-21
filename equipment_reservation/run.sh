#!/bin/bash

# Equipment Reservation System - Startup Script

echo "=================================="
echo "Equipment Reservation System"
echo "=================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if database exists
if [ ! -f "equipment_reservation.db" ]; then
    echo "Initializing database..."
    flask init-db

    echo ""
    read -p "Do you want to load sample data? (y/n): " load_sample
    if [ "$load_sample" = "y" ]; then
        echo "Loading sample data..."
        flask seed-db
        echo ""
        echo "Sample users created:"
        echo "  Admin: username=admin, password=admin123"
        echo "  User: username=user, password=user123"
    fi
fi

echo ""
echo "Starting application..."
echo "Access the application at: http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo ""

# Run the application
python app.py
