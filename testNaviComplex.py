# Assignment 6 - Executable Test Cases
# Project: Navi Complex Hotel Reservation System
# Name: Sundas Sattar (25i-8200)
# language: Python - pytest
# Run: pytest test_navi_complex.py -v


import pytest


class Room:
    def __init__(self, room_id, room_type, price):
        self.room_id = room_id
        self.room_type = room_type
        self.price = price
        # Initial state
        self.state = "Available"

    def room_booked(self):
        if self.state == "Available":
            self.state = "Reserved"

    def booking_cancelled(self):
        if self.state == "Reserved":
            self.state = "Available"

    def guest_checked_in(self):
        if self.state == "Reserved":
            self.state = "Occupied"

    def guest_checked_out(self):
        if self.state == "Occupied":
            self.state = "Available"

    def get_state(self):
        return self.state


class GuestProfile:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.loyalty_status = False
        # Initial state
        self.state = "NotRegistered"

    def sign_up(self, username, password):
        if self.state == "NotRegistered" and username and password:
            self.username = username
            self.password = password
            self.state = "Registered"
            return True
        return False

    def login(self, username, password):
        if self.state in ["Registered", "LoggedOut"]:
            if self.username == username and self.password == password:
                self.state = "LoggedIn"
                return True
        return False

    def logout(self):
        if self.state == "LoggedIn":
            self.state = "LoggedOut"

    def get_state(self):
        return self.state


class Booking:
    def __init__(self, booking_id, guest, room, dates, guest_count):
        self.booking_id = booking_id
        self.guest = guest
        self.room = room
        self.dates = dates
        self.guest_count = guest_count
        # Initial state
        self.state = "Created"

    def confirm_booking(self):
        if self.state == "Created":
            self.state = "AwaitingPayment"

    def process_payment(self, success=True):
        if self.state == "AwaitingPayment":
            if success:
                self.state = "Confirmed"
                return True
            else:
                # Retry — stays in AwaitingPayment
                self.state = "AwaitingPayment"
                return False

    def cancel_booking(self):
        if self.state in ["Created", "AwaitingPayment", "Confirmed"]:
            self.state = "Cancelled"

    def check_out(self):
        if self.state == "Confirmed":
            self.state = "Completed"

    def get_state(self):
        return self.state


class Controller:
    def __init__(self):
        self.state = "Idle"
        self.guest_profile = None
        self.current_booking = None
        self.current_room = None

    def user_logged_in(self, guest_profile):
        if self.state == "Idle":
            self.guest_profile = guest_profile
            self.state = "Active/WaitingEvent"

    def session_ended(self):
        if self.state == "Active/WaitingEvent":
            self.state = "Idle"

    def sign_up(self, username, password):
        if self.state == "Active/WaitingEvent":
            return self.guest_profile.sign_up(username, password)

    def login(self, username, password):
        if self.state == "Active/WaitingEvent":
            return self.guest_profile.login(username, password)

    def logout(self):
        if self.state == "Active/WaitingEvent":
            self.guest_profile.logout()

    def confirm_booking(self, booking):
        if self.state == "Active/WaitingEvent":
            self.current_booking = booking
            booking.confirm_booking()

    def process_payment(self, success=True):
        if self.state == "Active/WaitingEvent" and self.current_booking:
            return self.current_booking.process_payment(success)

    def cancel_booking(self):
        if self.state == "Active/WaitingEvent" and self.current_booking:
            self.current_booking.cancel_booking()

    def check_out(self):
        if self.state == "Active/WaitingEvent" and self.current_booking:
            self.current_booking.check_out()

    def room_booked(self, room):
        if self.state == "Active/WaitingEvent":
            self.current_room = room
            room.room_booked()

    def guest_checked_in(self):
        if self.state == "Active/WaitingEvent" and self.current_room:
            self.current_room.guest_checked_in()

    def guest_checked_out(self):
        if self.state == "Active/WaitingEvent" and self.current_room:
            self.current_room.guest_checked_out()

    def booking_cancelled_room(self):
        if self.state == "Active/WaitingEvent" and self.current_room:
            self.current_room.booking_cancelled()

    def get_state(self):
        return self.state


# 1. ROOM STATE MACHINE TEST CASES


class TestRoomStateMachine:

    def setup_method(self):
        """Room() constructor → Initial state = Available"""
        self.room = Room(101, "Deluxe", 150.0)

    # TC-ROOM-01
    # Sequence: Available →2→ Reserved →3→ *Available →6→ omega
    def test_TC_ROOM_01_booked_then_cancelled(self):
        """TC-ROOM-01: roomBooked() then bookingCancelled() returns to Available"""
        # Initial state check
        assert self.room.get_state() == "Available"

        # Event 2: roomBooked()
        self.room.room_booked()
        assert self.room.get_state() == "Reserved"

        # Event 3: bookingCancelled()
        self.room.booking_cancelled()
        assert self.room.get_state() == "Available"

    # TC-ROOM-02
    # Sequence: Available →2→ Reserved →4→ Occupied →5→ *Available →6→ omega
    def test_TC_ROOM_02_full_room_cycle(self):
        """TC-ROOM-02: Full cycle - booked, checked in, checked out"""
        # Initial state check
        assert self.room.get_state() == "Available"

        # Event 2: roomBooked()
        self.room.room_booked()
        assert self.room.get_state() == "Reserved"

        # Event 4: guestCheckedIn()
        self.room.guest_checked_in()
        assert self.room.get_state() == "Occupied"

        # Event 5: guestCheckedOut()
        self.room.guest_checked_out()
        assert self.room.get_state() == "Available"

    # TC-ROOM-03 — Sneak Path test
    # guestCheckedIn() must be IGNORED when Available
    def test_TC_ROOM_03_sneak_path_checkin_when_available(self):
        """TC-ROOM-03: guestCheckedIn() ignored when Available (sneak path)"""
        assert self.room.get_state() == "Available"

        self.room.guest_checked_in()
        assert (
            self.room.get_state() == "Available"
        ), "State must NOT change — guestCheckedIn() is invalid when Available"

    # TC-ROOM-04 — Sneak Path test
    # roomBooked() must be IGNORED when Occupied
    def test_TC_ROOM_04_sneak_path_book_when_occupied(self):
        """TC-ROOM-04: roomBooked() ignored when Occupied (sneak path)"""
        self.room.room_booked()
        self.room.guest_checked_in()

        self.room.room_booked()
        assert (
            self.room.get_state() == "Occupied"
        ), "State must NOT change — roomBooked() is invalid when Occupied"


# 2. BOOKING STATE MACHINE TEST CASES


class TestBookingStateMachine:

    def setup_method(self):
        """Booking() constructor → Initial state = Created"""
        self.room = Room(101, "Deluxe", 150.0)
        self.guest = GuestProfile("sundas", "pass123")
        self.booking = Booking(1, self.guest, self.room, "2026-04-01", 2)

    # TC-BOOKING-01
    # Sequence: Created →3→ AwaitingPayment →4→ Confirmed →7→ Completed →8→ omega
    def test_TC_BOOKING_01_happy_path_complete(self):
        """TC-BOOKING-01: Full happy path - confirm, pay, checkout"""
        assert self.booking.get_state() == "Created"

        # Event 3: roomSelected() / confirmBooking()
        self.booking.confirm_booking()
        assert self.booking.get_state() == "AwaitingPayment"

        # Event 4: processPayment()[success]
        result = self.booking.process_payment(success=True)
        assert result == True
        assert self.booking.get_state() == "Confirmed"

        # Event 7: checkedOut()
        self.booking.check_out()
        assert self.booking.get_state() == "Completed"

    # TC-BOOKING-02
    # Sequence: Created →3→ AwaitingPayment →4→ Confirmed →6→ Cancelled →8→ omega
    def test_TC_BOOKING_02_confirmed_then_cancelled(self):
        """TC-BOOKING-02: Booking confirmed then cancelled"""
        assert self.booking.get_state() == "Created"

        # Event 3: confirmBooking()
        self.booking.confirm_booking()
        assert self.booking.get_state() == "AwaitingPayment"

        # Event 4: processPayment()[success]
        self.booking.process_payment(success=True)
        assert self.booking.get_state() == "Confirmed"

        # Event 6: bookingCancelled()
        self.booking.cancel_booking()
        assert self.booking.get_state() == "Cancelled"

    # TC-BOOKING-03
    # Sequence: Created →3→ AwaitingPayment →*5→ *AwaitingPayment →4→ Confirmed →7→ Completed →8→ omega
    def test_TC_BOOKING_03_payment_retry_then_success(self):
        """TC-BOOKING-03: Payment fails first (retry), then succeeds"""
        assert self.booking.get_state() == "Created"

        # Event 3: confirmBooking()
        self.booking.confirm_booking()
        assert self.booking.get_state() == "AwaitingPayment"

        # Event *5: processPayment()[failed] — stays in AwaitingPayment
        result = self.booking.process_payment(success=False)
        assert result == False
        assert (
            self.booking.get_state() == "AwaitingPayment"
        ), "After failed payment, state must stay AwaitingPayment"

        # Event 4: processPayment()[success] — retry succeeds
        result = self.booking.process_payment(success=True)
        assert result == True
        assert self.booking.get_state() == "Confirmed"

        # Event 7: checkedOut()
        self.booking.check_out()
        assert self.booking.get_state() == "Completed"

    # TC-BOOKING-04
    # Sequence: Created →3→ AwaitingPayment →6→ Cancelled →8→ omega
    def test_TC_BOOKING_04_cancelled_at_payment(self):
        """TC-BOOKING-04: Booking cancelled while awaiting payment"""
        assert self.booking.get_state() == "Created"

        # Event 3: confirmBooking()
        self.booking.confirm_booking()
        assert self.booking.get_state() == "AwaitingPayment"

        # Event 6: bookingCancelled()
        self.booking.cancel_booking()
        assert self.booking.get_state() == "Cancelled"

    # TC-BOOKING-05
    # Sequence: Created →6→ Cancelled →8→ omega
    def test_TC_BOOKING_05_cancelled_at_created(self):
        """TC-BOOKING-05: Booking cancelled immediately after creation"""
        assert self.booking.get_state() == "Created"

        # Event 6: bookingCancelled()
        self.booking.cancel_booking()
        assert self.booking.get_state() == "Cancelled"

    # TC-BOOKING-06 — Sneak Path
    # checkedOut() must be IGNORED when AwaitingPayment
    def test_TC_BOOKING_06_sneak_path_checkout_when_awaiting(self):
        """TC-BOOKING-06: checkedOut() ignored when AwaitingPayment (sneak path)"""
        self.booking.confirm_booking()
        assert self.booking.get_state() == "AwaitingPayment"

        self.booking.check_out()
        assert (
            self.booking.get_state() == "AwaitingPayment"
        ), "checkedOut() must be ignored when state is AwaitingPayment"


# 3. GUESTPROFILE STATE MACHINE TEST CASES


class TestGuestProfileStateMachine:

    def setup_method(self):
        """GuestProfile() constructor → Initial state = NotRegistered"""
        self.guest = GuestProfile("", "")

    # TC-GUEST-01
    # Sequence: NotRegistered →2→ Registered →3→ LoggedIn →4→ LoggedOut →6→ omega
    def test_TC_GUEST_01_full_auth_cycle(self):
        """TC-GUEST-01: Full auth - signup, login, logout"""
        assert self.guest.get_state() == "NotRegistered"

        # Event 2: signUp()[valid details]
        result = self.guest.sign_up("sundas", "pass123")
        assert result == True
        assert self.guest.get_state() == "Registered"

        # Event 3: login()[credentials valid]
        result = self.guest.login("sundas", "pass123")
        assert result == True
        assert self.guest.get_state() == "LoggedIn"

        # Event 4: logout()
        self.guest.logout()
        assert self.guest.get_state() == "LoggedOut"

    # TC-GUEST-02
    # Sequence: NotRegistered →2→ Registered →3→ LoggedIn →4→ LoggedOut →5→ *LoggedIn →4→ LoggedOut →6→ omega
    def test_TC_GUEST_02_login_logout_login_again(self):
        """TC-GUEST-02: Logout then login again (*LoggedIn loop)"""
        assert self.guest.get_state() == "NotRegistered"

        # Event 2: signUp()
        self.guest.sign_up("sundas", "pass123")
        assert self.guest.get_state() == "Registered"

        # Event 3: login()
        self.guest.login("sundas", "pass123")
        assert self.guest.get_state() == "LoggedIn"

        # Event 4: logout()
        self.guest.logout()
        assert self.guest.get_state() == "LoggedOut"

        # Event 5: login() again → *LoggedIn
        result = self.guest.login("sundas", "pass123")
        assert result == True
        assert self.guest.get_state() == "LoggedIn"

        # Event 4: logout() again
        self.guest.logout()
        assert self.guest.get_state() == "LoggedOut"

    # TC-GUEST-03 — Sneak Path
    # login() must be IGNORED when NotRegistered
    def test_TC_GUEST_03_sneak_path_login_when_not_registered(self):
        """TC-GUEST-03: login() ignored when NotRegistered (sneak path)"""
        assert self.guest.get_state() == "NotRegistered"

        result = self.guest.login("sundas", "pass123")
        assert result == False
        assert (
            self.guest.get_state() == "NotRegistered"
        ), "login() must be ignored when state is NotRegistered"

    # TC-GUEST-04 — Sneak Path
    # signUp() must be IGNORED when already Registered
    def test_TC_GUEST_04_sneak_path_signup_when_registered(self):
        """TC-GUEST-04: signUp() ignored when already Registered (sneak path)"""
        self.guest.sign_up("sundas", "pass123")
        assert self.guest.get_state() == "Registered"

        result = self.guest.sign_up("other", "other123")
        assert result == False
        assert (
            self.guest.get_state() == "Registered"
        ), "signUp() must be ignored when already Registered"

    # TC-GUEST-05 — Invalid data
    # signUp() with invalid/empty details must be REJECTED
    def test_TC_GUEST_05_signup_with_invalid_details(self):
        """TC-GUEST-05: signUp()[invalid details] rejected, stays NotRegistered"""
        assert self.guest.get_state() == "NotRegistered"

        result = self.guest.sign_up("", "")
        assert result == False
        assert (
            self.guest.get_state() == "NotRegistered"
        ), "signUp() with invalid details must not change state"


# 4. CONTROLLER STATE MACHINE TEST CASES


class TestControllerStateMachine:

    def setup_method(self):
        """Controller() constructor → Initial state = Idle"""
        self.controller = Controller()
        self.guest = GuestProfile("sundas", "pass123")
        self.guest.sign_up("sundas", "pass123")
        self.room = Room(101, "Deluxe", 150.0)
        self.booking = Booking(1, self.guest, self.room, "2026-04-01", 2)

    # TC-CTRL-01
    # Sequence: Idle →2→ WaitingEvent →3→ GuestSM/NotReg →signUp→ Registered →login→ LoggedIn →logout→ LoggedOut →14→ *Idle →15→ omega
    def test_TC_CTRL_01_guest_profile_flow(self):
        """TC-CTRL-01: Full GuestProfile flow through Controller"""
        assert self.controller.get_state() == "Idle"

        # Event 2: userLoggedIn()
        fresh_guest = GuestProfile("", "")
        self.controller.user_logged_in(fresh_guest)
        assert self.controller.get_state() == "Active/WaitingEvent"

        # Event 3: signUp()[valid]
        result = self.controller.sign_up("ali", "ali123")
        assert result == True
        assert self.controller.guest_profile.get_state() == "Registered"

        # Event 4: login()[valid]
        result = self.controller.login("ali", "ali123")
        assert result == True
        assert self.controller.guest_profile.get_state() == "LoggedIn"

        # Event 5: logout()
        self.controller.logout()
        assert self.controller.guest_profile.get_state() == "LoggedOut"

        # Event 14: sessionEnded()
        self.controller.session_ended()
        assert self.controller.get_state() == "Idle"  # *Idle

    # TC-CTRL-02
    # Sequence: Idle →2→ WaitingEvent →6→ BookingSM/AwaitingPayment →7→ Confirmed →10→ Completed →14→ *Idle
    def test_TC_CTRL_02_booking_happy_path(self):
        """TC-CTRL-02: Full booking happy path through Controller"""
        assert self.controller.get_state() == "Idle"

        # Event 2: userLoggedIn()
        self.controller.user_logged_in(self.guest)
        assert self.controller.get_state() == "Active/WaitingEvent"

        # Event 6: bookingConfirmed()
        self.controller.confirm_booking(self.booking)
        assert self.booking.get_state() == "AwaitingPayment"

        # Event 7: processPayment()[success]
        result = self.controller.process_payment(success=True)
        assert result == True
        assert self.booking.get_state() == "Confirmed"

        # Event 10: checkedOut()
        self.controller.check_out()
        assert self.booking.get_state() == "Completed"

        # Event 14: sessionEnded()
        self.controller.session_ended()
        assert self.controller.get_state() == "Idle"

    # TC-CTRL-03
    # Sequence: Idle →2→ WaitingEvent →6→ BookingSM →*8→ *AwaitingPayment →7→ Confirmed →10→ Completed
    def test_TC_CTRL_03_payment_retry_through_controller(self):
        """TC-CTRL-03: Payment retry through Controller"""
        self.controller.user_logged_in(self.guest)
        self.controller.confirm_booking(self.booking)
        assert self.booking.get_state() == "AwaitingPayment"

        # Event *8: processPayment()[failed] — retry
        result = self.controller.process_payment(success=False)
        assert result == False
        assert (
            self.booking.get_state() == "AwaitingPayment"
        ), "After failed payment, booking must stay AwaitingPayment"

        # Event 7: processPayment()[success]
        result = self.controller.process_payment(success=True)
        assert result == True
        assert self.booking.get_state() == "Confirmed"

        self.controller.check_out()
        assert self.booking.get_state() == "Completed"

    # TC-CTRL-04
    # Sequence: Idle →2→ WaitingEvent →6→ BookingSM →9→ Cancelled →14→ *Idle
    def test_TC_CTRL_04_booking_cancelled_at_payment(self):
        """TC-CTRL-04: Booking cancelled while awaiting payment"""
        self.controller.user_logged_in(self.guest)
        self.controller.confirm_booking(self.booking)
        assert self.booking.get_state() == "AwaitingPayment"

        # Event 9: bookingCancelled()
        self.controller.cancel_booking()
        assert self.booking.get_state() == "Cancelled"

        self.controller.session_ended()
        assert self.controller.get_state() == "Idle"

    # TC-CTRL-05
    # Sequence: Idle →2→ WaitingEvent →6→ BookingSM →7→ Confirmed →9→ Cancelled →14→ *Idle
    def test_TC_CTRL_05_booking_cancelled_after_confirmed(self):
        """TC-CTRL-05: Booking cancelled after confirmation"""
        self.controller.user_logged_in(self.guest)
        self.controller.confirm_booking(self.booking)
        self.controller.process_payment(success=True)
        assert self.booking.get_state() == "Confirmed"

        # Event 9: bookingCancelled()
        self.controller.cancel_booking()
        assert self.booking.get_state() == "Cancelled"

        self.controller.session_ended()
        assert self.controller.get_state() == "Idle"

    # TC-CTRL-06
    # Sequence: Idle →2→ WaitingEvent →11→ RoomSM →11→ Reserved →12→ Occupied →13→ *Available →14→ *Idle
    def test_TC_CTRL_06_full_room_flow_through_controller(self):
        """TC-CTRL-06: Full room flow through Controller"""
        self.controller.user_logged_in(self.guest)
        assert self.controller.get_state() == "Active/WaitingEvent"

        # Event 11: roomBooked()
        self.controller.room_booked(self.room)
        assert self.room.get_state() == "Reserved"

        # Event 12: guestCheckedIn()
        self.controller.guest_checked_in()
        assert self.room.get_state() == "Occupied"

        # Event 13: guestCheckedOut()
        self.controller.guest_checked_out()
        assert self.room.get_state() == "Available"

        self.controller.session_ended()
        assert self.controller.get_state() == "Idle"

    # TC-CTRL-07
    # Sequence: Idle →2→ WaitingEvent →11→ RoomSM →13→ *Available →14→ *Idle
    def test_TC_CTRL_07_room_booking_cancelled_through_controller(self):
        """TC-CTRL-07: Room booking cancelled through Controller"""
        self.controller.user_logged_in(self.guest)

        # Event 11: roomBooked()
        self.controller.room_booked(self.room)
        assert self.room.get_state() == "Reserved"

        # Event 13: bookingCancelled()
        self.controller.booking_cancelled_room()
        assert self.room.get_state() == "Available"

        self.controller.session_ended()
        assert self.controller.get_state() == "Idle"

    # TC-CTRL-08
    # Sequence: Idle →2→ WaitingEvent →14→ *Idle →15→ omega
    def test_TC_CTRL_08_session_ended_immediately(self):
        """TC-CTRL-08: Session ended immediately after login"""
        assert self.controller.get_state() == "Idle"

        self.controller.user_logged_in(self.guest)
        assert self.controller.get_state() == "Active/WaitingEvent"

        # Event 14: sessionEnded() immediately
        self.controller.session_ended()
        assert self.controller.get_state() == "Idle"

    # TC-CTRL-09 — Sneak Path
    # Events must be IGNORED when Controller is Idle
    def test_TC_CTRL_09_sneak_path_events_when_idle(self):
        """TC-CTRL-09: All events ignored when Controller is Idle (sneak path)"""
        assert self.controller.get_state() == "Idle"

        # These should all be ignored
        self.controller.sign_up("test", "test")
        self.controller.logout()
        self.controller.cancel_booking()

        assert (
            self.controller.get_state() == "Idle"
        ), "Controller must stay Idle — all events ignored when not Active"
