## How to Run

### Prerequisites
- Python 3.x installed
- pytest installed

### Install pytest
pip install pytest

### Run all tests
python -m pytest testNaviComplex.py -v

### Run tests for one state machine only
# Room only
python -m pytest testNaviComplex.py::TestRoomStateMachine -v

# Booking only
python -m pytest testNaviComplex.py::TestBookingStateMachine -v

# GuestProfile only
python -m pytest testNaviComplex.py::TestGuestProfileStateMachine -v

# Controller only
python -m pytest testNaviComplex.py::TestControllerStateMachine -v

| Assignment 4 | State Machine Diagrams (PlantUML) |
| Assignment 5 | State Transition Tables + Trees |
| Assignment 6 | Executable Test Cases (this) |
