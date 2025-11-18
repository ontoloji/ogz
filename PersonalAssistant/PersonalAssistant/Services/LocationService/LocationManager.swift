//
//  LocationManager.swift
//  PersonalAssistant
//
//  Manages location services for location-based reminders
//

import Foundation
import CoreLocation
import Combine

@MainActor
class LocationManager: NSObject, ObservableObject {
    static let shared = LocationManager()

    @Published var authorizationStatus: CLAuthorizationStatus = .notDetermined
    @Published var currentLocation: CLLocation?
    @Published var isMonitoring = false

    private let locationManager = CLLocationManager()
    private var monitoredRegions: Set<CLCircularRegion> = []

    override init() {
        super.init()
        locationManager.delegate = self
        locationManager.desiredAccuracy = kCLLocationAccuracyHundredMeters
        authorizationStatus = locationManager.authorizationStatus
    }

    // MARK: - Authorization

    func requestWhenInUseAuthorization() {
        locationManager.requestWhenInUseAuthorization()
    }

    func requestAlwaysAuthorization() {
        locationManager.requestAlwaysAuthorization()
    }

    var hasLocationPermission: Bool {
        return authorizationStatus == .authorizedWhenInUse || authorizationStatus == .authorizedAlways
    }

    // MARK: - Location Updates

    func startUpdatingLocation() {
        guard hasLocationPermission else { return }
        locationManager.startUpdatingLocation()
    }

    func stopUpdatingLocation() {
        locationManager.stopUpdatingLocation()
    }

    func requestCurrentLocation() {
        guard hasLocationPermission else { return }
        locationManager.requestLocation()
    }

    // MARK: - Geofencing

    func startMonitoring(region: CLCircularRegion) {
        guard hasLocationPermission else { return }
        guard CLLocationManager.isMonitoringAvailable(for: CLCircularRegion.self) else {
            print("Geofencing is not available on this device")
            return
        }

        locationManager.startMonitoring(for: region)
        monitoredRegions.insert(region)
        isMonitoring = true
    }

    func stopMonitoring(region: CLCircularRegion) {
        locationManager.stopMonitoring(for: region)
        monitoredRegions.remove(region)

        if monitoredRegions.isEmpty {
            isMonitoring = false
        }
    }

    func stopAllMonitoring() {
        for region in locationManager.monitoredRegions {
            locationManager.stopMonitoring(for: region)
        }
        monitoredRegions.removeAll()
        isMonitoring = false
    }

    // MARK: - Geocoding

    func geocodeAddress(_ address: String) async throws -> CLLocation {
        let geocoder = CLGeocoder()
        let placemarks = try await geocoder.geocodeAddressString(address)

        guard let location = placemarks.first?.location else {
            throw LocationError.geocodingFailed
        }

        return location
    }

    func reverseGeocodeLocation(_ location: CLLocation) async throws -> CLPlacemark {
        let geocoder = CLGeocoder()
        let placemarks = try await geocoder.reverseGeocodeLocation(location)

        guard let placemark = placemarks.first else {
            throw LocationError.reverseGeocodingFailed
        }

        return placemark
    }

    // MARK: - Distance Calculation

    func distanceFromCurrentLocation(to coordinate: CLLocationCoordinate2D) -> CLLocationDistance? {
        guard let currentLocation = currentLocation else { return nil }

        let targetLocation = CLLocation(latitude: coordinate.latitude, longitude: coordinate.longitude)
        return currentLocation.distance(from: targetLocation)
    }

    // MARK: - Location Reminder Helper

    func createLocationReminder(
        for noteID: String,
        coordinate: CLLocationCoordinate2D,
        radius: CLLocationDistance,
        placeName: String,
        notifyOnEntry: Bool,
        notifyOnExit: Bool
    ) async throws {
        guard hasLocationPermission else {
            throw LocationError.noPermission
        }

        // Create region
        let region = CLCircularRegion(
            center: coordinate,
            radius: radius,
            identifier: noteID
        )
        region.notifyOnEntry = notifyOnEntry
        region.notifyOnExit = notifyOnExit

        // Start monitoring
        startMonitoring(region: region)
    }

    func removeLocationReminder(for noteID: String) {
        if let region = monitoredRegions.first(where: { $0.identifier == noteID }) {
            stopMonitoring(region: region)
        }
    }

    // MARK: - Errors

    enum LocationError: Error, LocalizedError {
        case noPermission
        case geocodingFailed
        case reverseGeocodingFailed
        case locationUnavailable

        var errorDescription: String? {
            switch self {
            case .noPermission:
                return "Konum izni gerekiyor"
            case .geocodingFailed:
                return "Adres bulunamadı"
            case .reverseGeocodingFailed:
                return "Konum bilgisi alınamadı"
            case .locationUnavailable:
                return "Konum servisi kullanılamıyor"
            }
        }
    }
}

// MARK: - CLLocationManagerDelegate

extension LocationManager: CLLocationManagerDelegate {
    nonisolated func locationManagerDidChangeAuthorization(_ manager: CLLocationManager) {
        Task { @MainActor in
            authorizationStatus = manager.authorizationStatus
        }
    }

    nonisolated func locationManager(_ manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        Task { @MainActor in
            currentLocation = locations.last
        }
    }

    nonisolated func locationManager(_ manager: CLLocationManager, didFailWithError error: Error) {
        print("Location manager error: \(error.localizedDescription)")
    }

    nonisolated func locationManager(_ manager: CLLocationManager, didEnterRegion region: CLRegion) {
        guard let circularRegion = region as? CLCircularRegion else { return }

        print("Entered region: \(circularRegion.identifier)")

        // Trigger notification
        Task {
            await MainActor.run {
                NotificationCenter.default.post(
                    name: .locationReminderTriggered,
                    object: nil,
                    userInfo: ["regionID": circularRegion.identifier, "action": "enter"]
                )
            }
        }
    }

    nonisolated func locationManager(_ manager: CLLocationManager, didExitRegion region: CLRegion) {
        guard let circularRegion = region as? CLCircularRegion else { return }

        print("Exited region: \(circularRegion.identifier)")

        // Trigger notification
        Task {
            await MainActor.run {
                NotificationCenter.default.post(
                    name: .locationReminderTriggered,
                    object: nil,
                    userInfo: ["regionID": circularRegion.identifier, "action": "exit"]
                )
            }
        }
    }

    nonisolated func locationManager(
        _ manager: CLLocationManager,
        monitoringDidFailFor region: CLRegion?,
        withError error: Error
    ) {
        print("Monitoring failed for region: \(region?.identifier ?? "unknown") - \(error.localizedDescription)")
    }
}
