---
stepsCompleted: [1, 2]
inputDocuments: []
workflowType: 'research'
lastStep: 1
research_type: 'technical'
research_topic: 'IRL day assistant mobile agent'
research_goals: 'Research the technical architecture and implementation path for a phone app that acts like an IRL Jarvis: checks location through the phone, understands the user day, and proactively directs the user where to go and what to do.'
user_name: 'Krishiv'
date: '2026-05-22'
web_research_enabled: true
source_verification: true
---

# Research Report: technical

**Date:** 2026-05-22
**Author:** Krishiv
**Research Type:** technical

---

## Research Overview

[Research overview and methodology will be appended here]

---

<!-- Content will be appended sequentially through research workflow steps -->

## Technical Research Scope Confirmation

**Research Topic:** IRL day assistant mobile agent
**Research Goals:** Research the technical architecture and implementation path for a phone app that acts like an IRL Jarvis: checks location through the phone, understands the user day, and proactively directs the user where to go and what to do.

**Technical Research Scope:**

- Architecture Analysis - design patterns, frameworks, system architecture
- Implementation Approaches - development methodologies, coding patterns
- Technology Stack - languages, frameworks, tools, platforms
- Integration Patterns - APIs, protocols, interoperability
- Performance Considerations - scalability, optimization, patterns

**Research Methodology:**

- Current web data with rigorous source verification
- Multi-source validation for critical technical claims
- Confidence level framework for uncertain information
- Comprehensive technical coverage with architecture-specific insights

**Scope Confirmed:** 2026-05-22

## Technology Stack Analysis

### Programming Languages

The most practical implementation paths are either a cross-platform mobile app in TypeScript/React Native or Flutter/Dart, or fully native apps using Swift/SwiftUI on iOS and Kotlin/Jetpack Compose on Android. For an MVP, React Native with Expo development builds is attractive because Expo TaskManager supports background tasks used by Location, BackgroundTask, BackgroundFetch, and Notifications, while still allowing native configuration for iOS background modes. Expo Go is not enough for real background execution testing, so the MVP should use development builds or a bare/native workflow.

For a production app that depends heavily on background location, native Swift and Kotlin provide the clearest access to platform-specific behavior, permission flows, and battery controls. iOS background location uses Core Location services such as significant-change updates, region monitoring, CLMonitor, and background location sessions; Android uses Geofencing API, Fused Location Provider, foreground service types, and WorkManager-style background execution. React Native remains viable, but location-critical features must be treated as native modules, not ordinary JavaScript screens.

_Popular Languages: TypeScript for React Native/Expo; Dart for Flutter; Swift for iOS; Kotlin for Android; TypeScript/Python for backend agent services._
_Emerging Languages: Dart/Flutter is relevant for agent-on-phone experiments such as Ferri-style native tool bridges; Kotlin Multiplatform may help share Android/iOS business logic if the team wants a native UI._
_Language Evolution: The stack is moving toward native-capability bridges and event-driven background execution rather than a continuously running mobile agent loop._
_Performance Characteristics: Native Swift/Kotlin is strongest for precise location and battery behavior; React Native/Expo is fastest for MVP iteration but needs dev builds and careful native configuration._
_Sources: https://docs.expo.dev/versions/latest/sdk/task-manager/ ; https://developer.apple.com/documentation/corelocation/handling-location-updates-in-the-background ; https://developer.android.com/develop/sensors-and-location/location/geofencing_

### Development Frameworks and Libraries

The core mobile framework decision is between speed of iteration and platform control. React Native with Expo can ship a cross-platform MVP quickly and supports background tasks through `expo-task-manager`, `expo-location`, `expo-background-task`, and notifications. The task definition must live in global scope because the JavaScript bundle can be launched in the background without mounted React views. iOS requires `UIBackgroundModes` configuration for background features, and Expo Go has limitations, so testing needs standalone/dev builds.

Native iOS should use SwiftUI plus Core Location, UserNotifications, EventKit/Calendar, MapKit or Google Maps SDK, and SwiftData/Core Data for local state. Native Android should use Kotlin, Jetpack Compose, Fused Location Provider, Geofencing API, foreground services for active navigation, WorkManager for deferrable sync, Room for local storage, and FCM for push notifications. If using React Native, evaluate native-backed location libraries or custom modules for background tracking, geofencing, and headless Android execution.

For the agent layer, use a tool-calling architecture. The assistant should expose typed tools such as `get_current_location`, `list_calendar_events`, `compute_route`, `rank_next_actions`, `schedule_notification`, and `request_user_confirmation`. OpenAI's Realtime API and function calling documentation support voice-agent sessions and tool calls, while open-source mobile agent examples such as Ferri show a phone-resident agent loop that registers native phone capabilities as callable tools.

_Major Frameworks: React Native/Expo for MVP; SwiftUI + Kotlin/Compose for production-grade native control; Flutter is plausible if using a Dart-native agent prototype._
_Micro-frameworks: Expo TaskManager/Location/Notifications, Core Location, Android Geofencing API, Room, SwiftData, WorkManager, BGTaskScheduler, OpenAI Realtime/function calling._
_Evolution Trends: Mobile assistants are trending toward local native tool registries, cloud/on-device LLM calls, and event-driven wakeups instead of always-on agents._
_Ecosystem Maturity: Core Location, Android location APIs, Google Maps Platform, Firebase, and native local storage are mature. Mobile LLM agent frameworks are newer and should be wrapped behind internal interfaces._
_Sources: https://docs.expo.dev/versions/latest/sdk/task-manager/ ; https://developers.openai.com/api/docs/guides/realtime ; https://developers.openai.com/api/docs/guides/function-calling ; https://github.com/ferri-ai/Ferri_

### Database and Storage Technologies

The app should be offline-first. The phone needs a local source of truth for today's plan, recent location context, cached places, user preferences, notification decisions, and pending agent actions. On iOS, SwiftData/Core Data is the native persistence path. SwiftData uses `ModelContainer`, `ModelContext`, and model configuration for persistent app data and can share storage with widgets/extensions through app groups. On Android, Room is the standard SQLite abstraction with entities, DAOs, and a database class; it fits itinerary, geofence, preference, and sync-queue tables.

For a cross-platform React Native MVP, SQLite-backed storage is the right local primitive for structured data. Avoid making remote state mandatory for deciding what to tell the user next; location and calendar-triggered recommendations should continue to work with stale-but-available local context. Cloud sync can keep long-term memories, preferences, accounts, and analytics, but the immediate "where should I go now?" decision should be able to run locally or with a graceful degraded mode.

For backend storage, Supabase/Postgres is strong if the product needs relational data, user preferences, audit trails, and self-hosting portability. Firebase is strong for mobile-first auth, push, crash reporting, realtime sync, and Google ecosystem integration. Given this product's dependency on push notifications, mobile auth, and fast mobile operations, Firebase is the default backend for an MVP; Supabase/Postgres becomes attractive if the data model quickly becomes relational or the team wants SQL/RLS from day one.

_Relational Databases: Postgres/Supabase for user profiles, preferences, memories, audit logs, and planner state._
_NoSQL Databases: Firestore/Firebase for mobile-first realtime documents, lightweight sync, and quick MVP backend development._
_In-Memory Databases: Redis is useful backend-side for short-lived session state, route-cache entries, and notification dedupe windows, but should not be required for core mobile behavior._
_Data Warehousing: Defer analytics warehousing until after product-market signal; start with privacy-preserving event logs and explicit consent._
_Sources: https://developer.apple.com/documentation/swiftdata/preserving-your-apps-model-data-across-launches ; https://developer.android.com/training/data-storage/room ; https://supabase.com/docs/guides/functions/examples/push-notifications?platform=fcm_

### Development Tools and Platforms

The development workflow should include real-device testing from the beginning because simulators are weak proxies for background location, battery behavior, notification delivery, and permission recovery. For React Native/Expo, use EAS development builds, not Expo Go, once background location is involved. For native iOS, use Xcode Instruments energy diagnostics and location simulation only as a supplement to real-world tests. For Android, test API 29+ background location permission flows and Android 14+ foreground service type requirements.

Use GitHub Actions or another CI runner for linting, unit tests, and typed contract checks around agent tools. For mobile quality, add crash reporting early: Firebase Crashlytics is the pragmatic default if Firebase is already selected; Sentry is a good cross-platform alternative. For agent testing, create deterministic fixtures for calendar events, location traces, route responses, and permission states so the model/tool orchestration can be evaluated without physically moving around each time.

_IDE and Editors: Xcode for iOS, Android Studio for Android, Cursor/VS Code for cross-platform TypeScript and backend work._
_Version Control: Git with feature branches; protect tool schemas and permission-related code with code review._
_Build Systems: EAS Build for Expo, Xcode build/test for iOS, Gradle for Android, Docker for backend services._
_Testing Frameworks: Jest/Vitest for TypeScript logic, XCTest for iOS, JUnit/Instrumented tests for Android, Detox/Maestro for mobile flows, fixture-based agent evals for planner behavior._
_Sources: https://docs.expo.dev/versions/latest/sdk/task-manager/ ; https://developer.android.com/develop/background-work/services/fgs/service-types ; https://developer.apple.com/documentation/xcode/configuring-background-execution-modes_

### Cloud Infrastructure and Deployment

The backend should act as a coordinator, not as an always-on shadow copy of the user's private life. A minimal backend needs auth, encrypted preference/memory storage, push notification delivery, route/place API proxying where keys must be protected, and optional cloud LLM calls for complex planning. For the MVP, Firebase plus Cloud Functions/Cloud Run is the fastest path because FCM, auth, crash reporting, and mobile SDKs fit the product. If using Supabase, pair it with Expo push notifications, FCM/APNs, or Supabase Edge Functions that send pushes from notification rows.

Google Maps Platform is the most obvious maps stack: Routes API `computeRoutes` provides real-time traffic, modes such as transit/driving/walking/biking, alternate routes, waypoints, and field masks; Places API supports search, autocomplete, details, and place IDs. The app should hide provider choice behind a routing/places abstraction because Apple Maps/MapKit may be preferable for iOS-native integrations or cost/UX reasons.

AI infrastructure should support two paths. Use low-latency realtime voice when the user is actively conversing, using ephemeral mobile credentials from the backend. Use cheaper asynchronous model calls or on-device heuristics for background ranking, notification summarization, and "should I bother the user?" decisions. Long-running agent state should be durable and event-driven rather than a blocked thread: store explicit state transitions and wake the agent on calendar, geofence, notification, or user events.

_Major Cloud Providers: Firebase/GCP is the default MVP path; Supabase/Postgres is a strong alternative for SQL-first data; AWS/Azure are viable but add less mobile-specific advantage._
_Container Technologies: Cloud Run or similar serverless containers for API orchestration, route proxying, and model-tool execution._
_Serverless Platforms: Firebase Cloud Functions, Cloud Run, Supabase Edge Functions, scheduled jobs, and webhooks._
_CDN and Edge Computing: Not central for MVP except static content and edge functions close to API users._
_Sources: https://developers.google.com/maps/documentation/routes/overview ; https://developers.google.com/maps/documentation/places/web-service/overview ; https://developers.googleblog.com/build-long-running-ai-agents-that-pause-resume-and-never-lose-context-with-adk/_

### Technology Adoption Trends

The strongest technical pattern is not a literal always-running Jarvis. Modern iOS and Android both constrain background execution to protect battery and privacy. The assistant should therefore use a layered model: local schedules and geofences wake small deterministic code; a lightweight ranking engine decides whether an action is urgent enough; the LLM is invoked only for ambiguous reasoning, user-facing language, or multi-step planning. This reduces cost, improves battery life, and improves App Store/Play Store compliance.

A good MVP stack is React Native/Expo development build, Firebase Auth/Firestore/FCM/Crashlytics, Google Maps Routes/Places, OpenAI function calling or Realtime for conversational flows, and local SQLite storage. A stronger production stack may move high-risk pieces to native Swift/Kotlin modules or full native apps, especially background location, permission education, navigation sessions, widgets/live activities, and wearable/voice surfaces.

_Migration Patterns: Start cross-platform for speed; migrate background location and notification-critical paths to native modules as reliability requirements rise._
_Emerging Technologies: Realtime voice agents, native tool registries, on-device LLMs for private summarization, and event-driven long-running agents._
_Legacy Technology: Continuous GPS polling and always-on background loops should be avoided except during explicit active navigation._
_Community Trends: Developers are combining mobile-native APIs with LLM tool calling, durable agent state, and local-first storage instead of relying on a monolithic cloud assistant._
_Sources: https://developer.android.com/develop/sensors-and-location/location/battery/scenarios ; https://developer.apple.com/library/archive/documentation/UserExperience/Conceptual/LocationAwarenessPG/CoreLocation/CoreLocation.html ; https://developers.openai.com/api/docs/guides/realtime-models-prompting_

## Integration Patterns Analysis

### API Design Patterns

The core API pattern should be a provider-agnostic internal tool API. The agent should never directly know the details of Google Calendar, EventKit, FCM, APNs, Routes API, or Places API. Instead, expose typed product-level tools such as `get_day_plan`, `get_current_location_context`, `find_candidate_destinations`, `compute_route_options`, `rank_next_actions`, `schedule_user_notification`, and `create_calendar_event`. Each tool should have a strict JSON schema, explicit permission requirements, and a bounded side-effect policy.

For backend APIs, REST/JSON is the pragmatic default because Google Maps Platform, Google Calendar, Firebase Cloud Messaging, and APNs all expose HTTP-based provider APIs. GraphQL is not necessary for the MVP because the product's integrations are action-oriented and event-oriented rather than client-driven data graph traversal. gRPC is useful only inside a larger backend once high-throughput service-to-service calls become important.

Webhook-style APIs are essential for calendar and external signal ingestion. Google Calendar push notifications notify the backend that a calendar resource changed, but they do not include event details; the backend must use stored channel metadata and then call `events.list` with an incremental `syncToken` to fetch actual changes. This means calendar integration requires both webhooks and scheduled incremental sync as a safety net.

_RESTful APIs: Use REST/JSON for mobile-backend, maps, calendar, notification, and LLM tool execution APIs._
_GraphQL APIs: Defer unless the app develops a complex client-driven query surface for history, memories, and analytics._
_RPC and gRPC: Use only for internal backend services where strict contracts and performance justify added complexity._
_Webhook Patterns: Use webhook-plus-incremental-sync for calendars; use provider callbacks/events as signals, not as full source-of-truth payloads._
_Sources: https://developers.google.com/workspace/calendar/api/guides/push ; https://developers.google.com/workspace/calendar/api/guides/sync ; https://developers.openai.com/api/docs/guides/function-calling_

### Communication Protocols

The app needs four communication modes. First, normal mobile-to-backend calls over HTTPS for profile, preferences, route proxying, notification registration, and agent actions. Second, provider webhooks over HTTPS for calendar/resource changes. Third, realtime voice sessions while the user is actively interacting with the assistant. Fourth, push notifications for proactive prompts when the app is not in the foreground.

Realtime voice should use a session-based protocol rather than repeated request/response calls. OpenAI's Realtime API supports mobile/browser voice-agent sessions, ephemeral client credentials from the backend, audio streaming, session events, and tool calls. In this mode, tool results must be returned to the model with the relevant call identifier so the model can continue the conversation with grounded state.

Push notifications should be treated as delivery mechanisms, not as the system of record. FCM HTTP v1 sends to device tokens, topics, or conditions using OAuth2 bearer authorization. APNs sends HTTP/2 POST requests to `/3/device/{deviceToken}` with JWT provider-token authentication, APNs headers, and a JSON payload. The backend should store notification intents and delivery results separately from provider-specific delivery attempts.

_HTTP/HTTPS Protocols: Default for app APIs, provider APIs, OAuth, routes, places, calendar sync, FCM, and APNs._
_WebSocket/Realtime Protocols: Use for active voice/conversation sessions only; avoid keeping persistent mobile sockets alive for passive proactivity._
_Message Queue Protocols: Use backend queues for notification scheduling, calendar sync jobs, route recalculation jobs, and retryable provider calls._
_gRPC and Protocol Buffers: Defer to internal service-to-service use; not required for the first mobile product._
_Sources: https://developers.openai.com/api/docs/guides/realtime ; https://firebase.google.com/docs/reference/fcm/rest/v1/projects.messages/send ; https://developer.apple.com/documentation/usernotifications/sending-notification-requests-to-apns_

### Data Formats and Standards

JSON should be the standard exchange format across app, backend, agent tools, and external APIs. Use strict JSON schemas for LLM tool calls so the model returns predictable arguments, and validate every tool call before execution. OpenAI's function calling supports `strict: true` structured outputs for tool arguments, which is especially important when tools can send notifications, create calendar events, or direct the user to move.

Calendar data should be normalized internally rather than exposing raw provider payloads to the agent. Google Calendar uses event resources and sync tokens; iOS EventKit uses local `EKEventStore` access with permission scopes. Normalize both into an internal `CalendarEvent` shape with provider IDs, time zone, location text, recurrence metadata, confidence/source fields, and sync status.

Maps data should also be normalized. Google Routes and Places APIs require explicit response field masks and return provider-specific structures. The internal model should use `Place`, `RouteOption`, `TravelMode`, `ETA`, and `Waypoint` objects that preserve provider IDs but avoid leaking provider-specific fields into the agent prompt unless needed.

_JSON and XML: JSON is the default; XML is not useful for this MVP unless a specific enterprise calendar/provider requires it._
_Protobuf and MessagePack: Not needed initially; consider Protobuf only if backend event volume or service count grows._
_CSV and Flat Files: Useful only for exporting user data or offline analysis, not runtime integrations._
_Custom Data Formats: Define domain schemas for `DecisionEvent`, `CalendarEvent`, `LocationContext`, `RouteOption`, `NotificationIntent`, and `AgentAction`._
_Sources: https://developers.openai.com/api/docs/guides/structured-outputs ; https://developers.google.com/maps/documentation/routes/choose_fields ; https://developers.google.com/maps/documentation/places/web-service/choose-fields_

### System Interoperability Approaches

The cleanest interoperability approach is an adapter layer around each external system. The mobile app talks to native adapters for location, calendar, notifications, and local storage. The backend talks to provider adapters for Google Calendar, Google Maps, FCM/APNs, and LLM providers. The agent talks only to product tools. This isolates provider churn and makes it possible to swap Google Maps for MapKit, Firebase for Supabase, or one LLM provider for another.

For iOS calendar/reminder integration, EventKit now distinguishes write-only and full calendar access. The app should request the least privilege needed for each feature: write-only if it only creates events, full access only if it must read the user's schedule locally. For Google Calendar, use OAuth 2.0 with Authorization Code + PKCE for account connection, store refresh tokens securely server-side or in platform secure storage depending on architecture, and subscribe to calendar changes with channel IDs mapped to users/calendars.

For AI tool interoperability beyond first-party tools, Model Context Protocol may become useful later, especially for connecting external services through standardized tools. For a mobile consumer MVP, MCP is probably not needed inside the phone app. It is more relevant as a backend tool gateway where OAuth 2.1, protected-resource metadata, dynamic client registration, and per-user token isolation can be handled centrally.

_Point-to-Point Integration: Acceptable for MVP provider adapters, but keep each provider behind an internal interface._
_API Gateway Patterns: Use a backend API gateway/BFF to protect provider keys, mint ephemeral realtime credentials, enforce auth, and centralize rate limits._
_Service Mesh: Unnecessary for MVP; revisit only after multiple independently deployed backend services exist._
_Enterprise Service Bus: Not relevant unless the product pivots into enterprise workflow integration._
_Sources: https://developer.apple.com/documentation/EventKit/accessing-calendar-using-eventkit-and-eventkitui ; https://datatracker.ietf.org/doc/rfc8252/ ; https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/specification/2025-03-26/basic/authorization.mdx_

### Microservices Integration Patterns

Start with a modular monolith or small backend-for-frontend rather than many microservices. The first backend can contain auth/session management, provider-token vaulting, calendar sync, route/places proxying, notification scheduling, and LLM orchestration. Split services only when operational pressure appears, such as calendar sync retries interfering with realtime voice sessions or notification throughput requiring independent scaling.

The high-value microservice patterns even in a small backend are queue-based jobs, idempotency keys, and circuit breakers. Calendar webhooks can arrive early, late, duplicated, or with minimal detail; route providers can fail or rate-limit; notification delivery can be delayed. Every provider-facing action should have retry policy, dedupe keys, and stored state transitions.

Distributed transactions should be avoided. For multi-step user actions, use a saga-like state machine: detect signal, create recommendation candidate, ask for confirmation if needed, execute calendar/notification/navigation side effect, then record outcome. This is safer than letting an LLM call multiple write tools without a durable action log.

_API Gateway Pattern: Use one authenticated mobile BFF/API gateway for app requests and provider proxying._
_Service Discovery: Not required in MVP; use managed platform discovery if services split later._
_Circuit Breaker Pattern: Apply around maps, calendar, LLM, and notification providers to prevent cascading failure and user spam._
_Saga Pattern: Use durable `AgentAction` state transitions for multi-step recommendations and side effects._
_Sources: https://developers.googleblog.com/build-long-running-ai-agents-that-pause-resume-and-never-lose-context-with-adk/ ; https://developers.google.com/workspace/calendar/api/guides/sync ; https://developers.google.com/maps/documentation/routes/reference/rest/v2/TopLevel/computeRoutes_

### Event-Driven Integration

Event-driven architecture is the product's backbone. Useful events include `LocationRegionEntered`, `SignificantLocationChanged`, `CalendarChanged`, `UpcomingEventWindowOpened`, `RouteETAChanged`, `NotificationTapped`, `UserDismissedSuggestion`, and `PermissionChanged`. These events should feed a local or backend decision pipeline that decides whether to wake the agent, update local state, or notify the user.

On mobile, event-driven does not mean always-running. iOS Core Location and Android geofencing/background APIs should wake limited work. The app should write events locally, run cheap deterministic checks, and only escalate to the backend/LLM when the decision is valuable enough. On backend, provider webhooks and scheduled jobs should publish events into queues for sync and recommendation processing.

Event sourcing is useful selectively. Store high-value decision and action events for debugging, user trust, and model evaluation: what signal arrived, what data was considered, why the assistant notified or stayed silent, and what the user did next. Do not store raw location trails by default; privacy and battery constraints argue for summarized context and short retention.

_Publish-Subscribe Patterns: Use event topics/queues for calendar changes, route recalculations, notification jobs, and user interaction events._
_Event Sourcing: Store decision/action audit events, not raw continuous location history._
_Message Broker Patterns: Start with managed queues/tasks; add Kafka/Pub/Sub only if event volume demands it._
_CQRS Patterns: Useful later for separating write-heavy event logs from read-optimized day summaries and recommendation history._
_Sources: https://developer.android.com/develop/sensors-and-location/location/geofencing ; https://developer.apple.com/library/archive/documentation/UserExperience/Conceptual/LocationAwarenessPG/RegionMonitoring/RegionMonitoring.html ; https://nango.dev/blog/how-to-build-a-real-time-google-calendar-api-integration/_

### Integration Security Patterns

OAuth 2.0 Authorization Code with PKCE is mandatory for mobile account linking and sign-in. Native apps should use external user agents such as system browser sessions, not embedded WebViews. Use claimed HTTPS redirects through Universal Links/App Links where possible, with private-use URI schemes only as a fallback. Always include high-entropy state and the S256 PKCE method.

Tool security should be stricter than chat security. The LLM can propose actions, but tool execution should pass through policy checks. Read tools can often run automatically if the user granted permission; write tools such as "create event", "send notification", "start navigation", or "message someone" need explicit side-effect classification, confirmation rules, and audit logs. Use strict schemas for tool arguments and do not let the model directly hold provider credentials.

Provider credentials and user tokens need compartmentalization. Store mobile secrets in Keychain/Keystore. Keep Google Maps server keys, APNs signing keys, Firebase service credentials, and OAuth client secrets on the backend. For APNs, provider tokens are JWTs signed with ES256 and expire after about an hour. For FCM HTTP v1, use OAuth2 bearer tokens with the Firebase Messaging scope.

_OAuth 2.0 and JWT: Use Authorization Code + PKCE for native/mobile auth; JWT provider tokens for APNs; OAuth2 bearer tokens for FCM and Google APIs._
_API Key Management: Keep Maps and provider keys on the backend where possible; restrict keys by API, platform, bundle/package, and environment._
_Mutual TLS: Not needed for MVP consumer integrations, but useful for future enterprise or high-trust backend service calls._
_Data Encryption: TLS in transit, platform secure storage on device, encrypted backend token storage, minimized location retention, and per-user access controls._
_Sources: https://datatracker.ietf.org/doc/html/rfc7636 ; https://developer.apple.com/library/archive/documentation/NetworkingInternet/Conceptual/RemoteNotificationsPG/CommunicatingwithAPNs.html ; https://firebase.google.cn/docs/cloud-messaging/send/v1-api_
