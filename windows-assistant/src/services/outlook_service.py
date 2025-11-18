"""
Outlook service - Microsoft Graph API integration for calendar events
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json


class OutlookService:
    """Service for integrating with Microsoft Outlook via Graph API"""

    def __init__(self, db):
        self.db = db
        self.access_token = None
        self.refresh_token = None
        self.token_expires = None
        self.is_authenticated = False

        # Microsoft Graph API endpoints
        self.graph_api_base = "https://graph.microsoft.com/v1.0"
        self.auth_endpoint = "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
        self.token_endpoint = "https://login.microsoftonline.com/common/oauth2/v2.0/token"

        # Required scopes
        self.scopes = [
            "Calendars.Read",
            "Calendars.Read.Shared",
            "User.Read"
        ]

    def authenticate(self, client_id: str, client_secret: str = None):
        """
        Authenticate with Microsoft Graph API using OAuth 2.0

        Note: This is a placeholder. Real implementation would require:
        1. Redirecting user to Microsoft login page
        2. Handling OAuth callback
        3. Exchanging auth code for access token
        4. Storing tokens securely

        Args:
            client_id: Azure AD application client ID
            client_secret: Azure AD application client secret (for confidential clients)
        """
        # This is a simplified version
        # Real implementation would use msal library
        print("⚠ OAuth authentication flow should be implemented")
        print("  Required steps:")
        print("  1. Register app in Azure AD")
        print("  2. Implement OAuth 2.0 flow")
        print("  3. Store access/refresh tokens securely")

        # For now, mark as not authenticated
        self.is_authenticated = False

    def sync_calendar_events(self, days_ahead: int = 7) -> int:
        """
        Sync calendar events from Outlook

        Args:
            days_ahead: Number of days ahead to fetch events

        Returns:
            Number of events synced
        """
        if not self.is_authenticated:
            print("⚠ Not authenticated with Microsoft Graph API")
            return 0

        try:
            # This would make actual API calls
            # For now, return mock data for testing
            events = self._fetch_events_mock(days_ahead)
            count = self._store_events(events)
            return count

        except Exception as e:
            print(f"Error syncing calendar events: {e}")
            return 0

    def _fetch_events_mock(self, days_ahead: int) -> List[Dict[str, Any]]:
        """
        Mock function for testing - returns sample events

        In real implementation, this would make API calls to:
        GET https://graph.microsoft.com/v1.0/me/calendar/calendarView?startDateTime=...&endDateTime=...
        """
        # Return empty list for now
        # Real implementation would use requests library
        return []

    def _store_events(self, events: List[Dict[str, Any]]) -> int:
        """Store calendar events in local database"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        count = 0

        for event in events:
            try:
                # Extract event data
                event_id = event.get('id')
                subject = event.get('subject', 'No Subject')
                start_time = event.get('start', {}).get('dateTime')
                end_time = event.get('end', {}).get('dateTime')
                location = event.get('location', {}).get('displayName', '')
                description = event.get('body', {}).get('content', '')
                organizer = event.get('organizer', {}).get('emailAddress', {}).get('name', '')
                is_all_day = event.get('isAllDay', False)

                # Parse attendees
                attendees_list = event.get('attendees', [])
                attendees = ', '.join([
                    att.get('emailAddress', {}).get('name', '')
                    for att in attendees_list
                ])

                # Insert or update event
                cursor.execute('''
                    INSERT OR REPLACE INTO calendar_events
                    (event_id, subject, start_time, end_time, location, attendees,
                     description, organizer, is_all_day, last_synced)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (event_id, subject, start_time, end_time, location, attendees,
                      description, organizer, is_all_day))

                count += 1

            except Exception as e:
                print(f"Error storing event: {e}")
                continue

        conn.commit()
        return count

    def get_upcoming_events(self, hours_ahead: int = 24) -> List[Dict[str, Any]]:
        """
        Get upcoming events from local cache

        Args:
            hours_ahead: Number of hours ahead to look

        Returns:
            List of upcoming events
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()

        now = datetime.now()
        until = now + timedelta(hours=hours_ahead)

        cursor.execute('''
            SELECT * FROM calendar_events
            WHERE start_time >= ? AND start_time <= ?
                AND notification_sent = 0
            ORDER BY start_time ASC
        ''', (now.isoformat(), until.isoformat()))

        return [dict(row) for row in cursor.fetchall()]

    def mark_notification_sent(self, event_id: int):
        """Mark that notification has been sent for an event"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE calendar_events
            SET notification_sent = 1
            WHERE id = ?
        ''', (event_id,))

        conn.commit()

    def check_events_for_notifications(self, notification_callback) -> int:
        """
        Check for events that need notifications (24 hours before)

        Args:
            notification_callback: Function to call for each event

        Returns:
            Number of notifications sent
        """
        events = self.get_upcoming_events(hours_ahead=24)
        count = 0

        for event in events:
            try:
                # Check if we should send notification (24 hours before)
                start_time = datetime.fromisoformat(event['start_time'])
                now = datetime.now()
                hours_until = (start_time - now).total_seconds() / 3600

                # Send notification if event is between 23-25 hours away
                if 23 <= hours_until <= 25:
                    notification_callback(event)
                    self.mark_notification_sent(event['id'])
                    count += 1

            except Exception as e:
                print(f"Error checking event for notification: {e}")
                continue

        return count


# Implementation guide for real OAuth flow:
"""
To implement real Microsoft Graph API integration:

1. Install required library:
   pip install msal requests

2. Register your app in Azure AD:
   - Go to https://portal.azure.com
   - Register a new application
   - Add redirect URI (e.g., http://localhost:8000/auth/callback)
   - Note down Client ID and create Client Secret
   - Grant API permissions: Calendars.Read, Calendars.Read.Shared

3. Implement OAuth flow:

from msal import PublicClientApplication
import requests

class OutlookService:
    def __init__(self):
        self.client_id = "YOUR_CLIENT_ID"
        self.authority = "https://login.microsoftonline.com/common"
        self.scope = ["Calendars.Read", "User.Read"]

        self.app = PublicClientApplication(
            self.client_id,
            authority=self.authority
        )

    def authenticate_interactive(self):
        # Interactive authentication
        result = self.app.acquire_token_interactive(scopes=self.scope)
        if "access_token" in result:
            self.access_token = result["access_token"]
            return True
        return False

    def get_calendar_events(self):
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

        # Get events for next 7 days
        start = datetime.now().isoformat()
        end = (datetime.now() + timedelta(days=7)).isoformat()

        url = f"https://graph.microsoft.com/v1.0/me/calendar/calendarView"
        params = {
            'startDateTime': start,
            'endDateTime': end
        }

        response = requests.get(url, headers=headers, params=params)
        return response.json().get('value', [])
"""
