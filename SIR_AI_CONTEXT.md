# SIR --- Product, Business & Engineering Context

## AI Coding Agent Master Context --- MVP v0.1

> This file is the source of truth for an AI coding agent working on
> SIR. Read it before changing architecture, UI, database models, API
> contracts, or business logic.

------------------------------------------------------------------------

# 1. PRODUCT OVERVIEW

SIR is a South African service-at-home marketplace.

Core promise:

**Book trusted professionals to come to you.**

Customers can discover and book independent service providers for
services performed at their home, workplace, gym, office, hotel, or
another chosen location.

SIR initially focuses on:

1.  Beauty & Personal Care
    -   Haircuts
    -   Hair styling / braiding
    -   Nails
    -   Lashes
    -   Makeup
    -   Massage
2.  Personal Training
    -   Personal training at home
    -   Personal training at a gym
    -   Strength / conditioning
    -   Weight-loss / fitness sessions
    -   Beginner / intermediate / advanced sessions
    -   Other trainer-defined session types
3.  Domestic Services
    -   Household cleaning
    -   Cleaning priced according to home size, rooms, duration, or
        package
4.  Automotive
    -   Mobile car washing
    -   Future detailing options

Future categories must be designed as extensions of the same marketplace
model rather than hard-coded special cases.

Future examples: - Laundry pickup and delivery - Barbers - Handyman
services - Gardening - Pet grooming - Other local services -
Business-to-business services - Partner businesses that fulfil multiple
jobs

------------------------------------------------------------------------

# 2. BUSINESS MODEL

SIR is a two-sided marketplace.

CUSTOMER: Needs a service -\> selects service -\> provides details -\>
selects location/date/time -\> receives provider/job options -\> books
-\> provider fulfils -\> customer reviews.

PROVIDER: Creates account -\> completes verification/KYC -\> selects
services -\> defines service area, pricing and availability -\> receives
nearby job opportunities -\> accepts/declines -\> fulfils job -\> marks
complete -\> earns money.

SIR owns the customer relationship, marketplace technology, discovery,
booking experience, trust layer and eventually payment/logistics
infrastructure.

SIR does NOT initially need to employ service providers.

Providers are intended to operate as independent
professionals/businesses, subject to the final legal structure and South
African legal/tax requirements.

------------------------------------------------------------------------

# 3. MVP BUSINESS MODEL

Recommended initial model:

## Provider commission

Start with approximately **15--20% commission on completed bookings**.

Recommended MVP default: **18% provider commission.**

Example:

Customer booking: R500

SIR commission: R90

Provider gross: R410

Payment processing fees will be handled separately once payments are
introduced.

Do not hard-code 18% everywhere. Store commission rules/configuration in
the backend so the business can change them later.

## Customer fees

Do NOT introduce a complicated customer fee during the no-payment MVP.

For payment-enabled v2, test: - Either commission-only initially - Or a
small transparent customer platform/booking fee

The customer must always see the total price before confirming.

Avoid hidden fees.

## Why commission is the preferred initial model

A marketplace should minimize provider friction while supply is being
built.

Providers should be able to: - Join for free - Create a profile for
free - List services for free - Only pay SIR when they earn

This is more attractive than an upfront subscription.

South African marketplace examples show several models in market: some
charge around 7--20% provider commission, while others use customer fees
or provider-set pricing. SIR should test pricing rather than assume one
permanent rate.

------------------------------------------------------------------------

# 4. SERVICE PRICING MODEL

SIR should NOT use one pricing model for every service.

The backend needs a flexible service pricing engine.

Supported pricing types:

-   FIXED
-   STARTING_FROM
-   HOURLY
-   DURATION
-   QUANTITY
-   SIZE
-   CUSTOM_OPTIONS
-   PROVIDER_DEFINED

## Beauty

Providers may define services such as:

Haircut: R250

Gel manicure: R350

Classic lashes: R500

Full glam: R900

60-minute massage: R700

For MVP, providers can choose from SIR's standardized service categories
and enter their own price.

Later SIR can establish recommended market price ranges.

## Personal training

Recommended model:

PRICE PER SESSION.

Example: 30 min: R250 45 min: R300 60 min: R400 90 min: R550

Additional configurable attributes: - Intensity - Session type - Fitness
goal - Equipment required - Indoor/outdoor - Home/gym - Number of people

Do not force every trainer into identical pricing.

## Cleaning

Cleaning should be structured around predictable inputs.

Example:

Home size: - Studio / 1 bedroom - 2 bedroom - 3 bedroom - 4 bedroom - 5+
bedroom

Optional: - Bathrooms - Deep clean - Standard clean - Move-in /
move-out - Add-ons

Alternative pricing: Hourly rate with minimum booking duration.

The platform should calculate an estimated price from the selected
package.

Example: 3-bedroom standard clean Base: R450 Deep-clean add-on: +R250
Total: R700

The exact commercial prices must be configurable.

## Car wash

Use vehicle type + package.

Vehicle: - Sedan - Hatchback - SUV - Bakkie - Luxury / large vehicle

Package: - Standard - Premium - Detail

Example: Standard Sedan: R150 Standard SUV: R200 Premium Sedan: R250
Premium SUV: R300

Again: configurable, not hard-coded.

------------------------------------------------------------------------

# 5. IMPORTANT MARKETPLACE PRINCIPLE

The SIR customer experience should feel like:

**"Tell us what you need and we'll handle the rest."**

It should NOT feel like: "Search through hundreds of random
freelancers."

Trust and convenience are more important than maximum choice.

For MVP, customers should see: - Service - Price - Estimated duration -
Provider - Rating - Verification status - Availability - Distance /
service area - Relevant portfolio/profile images

------------------------------------------------------------------------

# 6. BRAND

Brand name:

**SIR**

The existing SIR logo is the blue aura-style logo.

DO NOT redesign or replace the logo unless explicitly instructed.

Brand attributes:

-   Trustworthy
-   Calm
-   Modern
-   Convenient
-   Safe
-   Youthful
-   Technological
-   Human
-   Premium but accessible

The desired emotional direction is inspired by the calm, simple,
friendly feeling associated with modern South African consumer-tech
brands such as Naked Insurance, but SIR must have its own visual
identity. Do not copy Naked's exact colors, layouts, typography,
illustrations, language, or creative assets.

Brand feeling:

> "Relax. Sir's got it."

Possible brand language: - "We'll bring it to you." - "Book. Relax.
Done." - "Your service. Your place. Your time." - "Good service,
wherever you are."

Avoid: - Corporate jargon - Aggressive sales language - Cheap
marketplace aesthetic - Excessive gradients - Clutter - Overly technical
language - Fake claims such as "100% safe" or "guaranteed"

------------------------------------------------------------------------

# 7. TRUST & SAFETY

Trust is a core product feature.

Customers are allowing strangers into their homes, so the platform must
make verification highly visible.

Provider verification states:

PENDING VERIFIED REJECTED SUSPENDED

Provider profile should show: - Verified badge - Name - Profile photo -
Services - Ratings - Number of completed jobs - Relevant
certifications - Approximate service area

Sensitive KYC documents must NOT be displayed publicly.

KYC data must be stored securely and access-controlled.

For personal trainers, certification evidence is required.

For regulated services, the system should support configurable required
documents.

Never expose ID numbers, document images, addresses or other sensitive
KYC data to ordinary customers.

------------------------------------------------------------------------

# 8. CUSTOMER UX

The customer's journey should be extremely simple.

## Landing page

Hero:

**Services that come to you.**

Supporting text: "Book trusted professionals for beauty, fitness,
cleaning and more --- wherever you are."

Primary CTA: **Book a service**

Secondary CTA: **Become a provider**

Optional: **Partner with SIR**

Landing sections:

1.  Hero
2.  How SIR works
3.  Popular services
4.  Why customers trust SIR
5.  Provider opportunity
6.  Business partnership section
7.  Reviews/social proof
8.  FAQ
9.  Footer

Do NOT make the landing page feel like a corporate website.

It should feel like a consumer technology product.

------------------------------------------------------------------------

# 9. CUSTOMER AUTHENTICATION

Separate customer and provider onboarding experiences.

Customer routes:

/customer/login /customer/signup

Provider routes:

/provider/login /provider/signup

Users may eventually share one authentication system underneath, but the
UI should communicate clearly that the two journeys are different.

Customer signup: - Name - Email - Mobile number - Password/auth
provider - Basic location/area

Do not collect unnecessary information.

------------------------------------------------------------------------

# 10. CUSTOMER APP

Primary routes:

/ /services /services/\[category\] /services/\[service\]
/booking/\[service\] /bookings /bookings/\[id\] /profile /login /signup

Main customer dashboard:

"Good morning, \[Name\]"

Primary action: **What do you need today?**

Service cards: - Beauty - Fitness - Cleaning - Car Wash

Upcoming booking card: - Service - Provider - Date/time - Location -
Status

Past bookings: - Service - Date - Provider - Rating

------------------------------------------------------------------------

# 11. BOOKING UX

Booking should be a guided flow.

Step 1: Choose service.

Step 2: Choose service package/type.

Step 3: Provide service-specific details.

Step 4: Choose location.

Step 5: Choose date/time.

Step 6: Review request.

Step 7: Submit booking.

Payments are NOT part of MVP v0.1.

The UI should still show an estimated price.

MVP booking status:

REQUESTED ACCEPTED DECLINED CANCELLED EN_ROUTE IN_PROGRESS COMPLETED

------------------------------------------------------------------------

# 12. SERVICE-SPECIFIC BOOKING FORMS

Do NOT create one enormous generic form.

Create dynamic forms based on service.

## Beauty

Fields may include: - Service type - Style - Hair length/type where
relevant - Reference image upload - Date - Time - Location - Notes

## Massage

-   Massage type
-   Duration
-   Location
-   Date
-   Time
-   Notes

Do not collect medical information unless legally necessary.

## Personal training

-   Session duration
-   Intensity
-   Session type
-   Fitness goal
-   Location
-   Date
-   Time
-   Equipment available
-   Number of people

## Cleaning

-   Property type
-   Number of bedrooms
-   Number of bathrooms
-   Cleaning type
-   Approximate duration/package
-   Add-ons
-   Location
-   Date
-   Time
-   Notes

## Car wash

-   Vehicle type
-   Service package
-   Location
-   Date
-   Time
-   Access/site notes

------------------------------------------------------------------------

# 13. PROVIDER ONBOARDING

Provider signup is a multi-step onboarding flow.

Step 1: Account

Step 2: Personal/business information

Step 3: Services

Step 4: Pricing

Step 5: Service area

Step 6: Availability

Step 7: Required verification documents

Step 8: Review

Step 9: Submit for verification

Provider cannot receive jobs requiring verification until their account
is approved.

For MVP, an admin manually verifies providers.

Automated KYC integrations can come later.

------------------------------------------------------------------------

# 14. PROVIDER DASHBOARD

Provider home:

"Good morning, \[Provider\]"

Status: ONLINE / OFFLINE

Sections:

## New jobs nearby

Each job: - Service - Area - Date - Time - Estimated duration -
Estimated earnings - Distance - Customer notes - Accept - Decline

## Upcoming

Shows accepted jobs.

## Active job

Shows current job status.

## Earnings

For MVP, earnings can be an informational calculation because payments
are not implemented.

Example: Booking: R500 SIR commission: R90 Estimated provider earnings:
R410

## Profile

-   Services
-   Prices
-   Service area
-   Availability
-   Rating
-   Verification

------------------------------------------------------------------------

# 15. PROVIDER JOB ACCEPTANCE

MVP matching can be simple.

Find providers where:

-   Provider is verified
-   Provider offers requested service
-   Provider operates in requested area
-   Provider is available at requested time
-   Provider is not already booked

Send job to matching providers.

Provider accepts.

Booking becomes: ACCEPTED

For MVP, do NOT build sophisticated AI matching, dynamic pricing, route
optimization, or real-time dispatch.

Those are future improvements.

------------------------------------------------------------------------

# 16. ADMIN DASHBOARD

Admin must be able to operate the marketplace manually.

Routes:

/admin /admin/bookings /admin/providers /admin/customers /admin/services
/admin/reviews

Admin capabilities:

-   View providers
-   Approve/reject providers
-   View KYC status
-   View bookings
-   Change booking status
-   View customers
-   Manage services
-   Manage service packages
-   Manage pricing configuration
-   Suspend providers
-   Review complaints
-   View basic marketplace metrics

Admin is critical because SIR will initially be operationally managed by
humans.

------------------------------------------------------------------------

# 17. FUTURE BUSINESS PARTNERS

SIR should eventually support three supply types:

1.  INDIVIDUAL_PROVIDER
2.  SERVICE_BUSINESS
3.  PARTNER_BUSINESS

Example:

A laundromat becomes a SIR partner.

Customer: "Collect my laundry."

SIR: Creates collection request.

Courier: Collects laundry.

Laundry partner: Receives and processes laundry.

Courier: Returns laundry.

Customer: Receives completed order.

This should be designed as a future workflow, but NOT built into MVP
unless it is required for the first launch.

------------------------------------------------------------------------

# 18. BUSINESS PARTNERSHIP LANDING PAGE

Landing page section:

## "Run a business? Grow with SIR."

Copy concept:

"Bring your services to more customers without building your own
marketplace."

CTA: **Partner with SIR**

Partnership form: - Name - Business name - Email - Phone - Business
type - Services offered - Area - Message

Examples: - Salon - Car wash - Cleaning company - Laundromat - Gym -
Wellness business

Store partnership enquiries in the database.

Admin can view them.

------------------------------------------------------------------------

# 19. TECH STACK

Use a simple monolithic architecture for MVP.

## Frontend

Next.js TypeScript Tailwind CSS shadcn/ui

Use React Query/TanStack Query where appropriate.

## Backend

FastAPI Python Pydantic SQLAlchemy Alembic

## Database

PostgreSQL

## Local development

Docker Compose

Services: - frontend - backend - postgres

Do NOT introduce Kubernetes, microservices, Kafka, Redis, or complex
infrastructure for MVP.

------------------------------------------------------------------------

# 20. REPOSITORY STRUCTURE

Preferred:

/sir /frontend /backend /docs /docker-compose.yml /.env.example
/README.md

Frontend: - app/ - components/ - lib/ - hooks/ - types/

Backend: - app/ - api/ - core/ - models/ - schemas/ - services/ -
repositories/ - db/ - tests/

Keep business logic out of route handlers.

------------------------------------------------------------------------

# 21. CORE DATABASE ENTITIES

Minimum:

User ProviderProfile ProviderService ServiceCategory Service
ServiceOption Booking BookingStatusHistory Address ProviderAvailability
ProviderDocument Review PartnershipInquiry

Potential fields:

USER - id - role - name - email - phone - password/auth identifier -
created_at

PROVIDER - id - user_id - business_name - bio - verification_status -
rating - service_radius - created_at

SERVICE_CATEGORY - id - name - description

SERVICE - id - category_id - name - description - pricing_type - active

PROVIDER_SERVICE - id - provider_id - service_id - base_price - active

BOOKING - id - customer_id - provider_id - service_id - scheduled_at -
location - estimated_price - final_price - status - notes - created_at

BOOKING_STATUS_HISTORY - id - booking_id - old_status - new_status -
changed_by - created_at

PROVIDER_AVAILABILITY - id - provider_id - day_of_week - start_time -
end_time

PROVIDER_DOCUMENT - id - provider_id - document_type -
verification_status - secure_storage_reference

REVIEW - id - booking_id - customer_id - provider_id - rating - comment

PARTNERSHIP_INQUIRY - id - name - business_name - email - phone -
business_type - services - area - message - status - created_at

------------------------------------------------------------------------

# 22. API DESIGN

Example endpoints:

POST /auth/customer/signup POST /auth/provider/signup POST /auth/login

GET /services GET /services/{id}

GET /providers GET /providers/{id}

POST /providers/profile POST /providers/services POST
/providers/documents

GET /bookings POST /bookings GET /bookings/{id}

POST /bookings/{id}/accept POST /bookings/{id}/decline POST
/bookings/{id}/cancel POST /bookings/{id}/start POST
/bookings/{id}/complete

POST /reviews

POST /partnership-inquiries

Admin: GET /admin/providers POST /admin/providers/{id}/approve POST
/admin/providers/{id}/reject GET /admin/bookings

Use RESTful conventions and proper authorization.

------------------------------------------------------------------------

# 23. SECURITY

Implement:

-   Authentication
-   Role-based authorization
-   Input validation
-   Password hashing if handling passwords
-   Secure environment variables
-   CORS configuration
-   Rate limiting where practical
-   Audit logging for important provider/admin actions

Never expose: - KYC documents - ID numbers - sensitive provider
information - secrets - database credentials

Do not put secrets into source code.

------------------------------------------------------------------------

# 24. MVP NON-GOALS

Do NOT build these unless specifically requested:

-   Payment processing
-   Automated KYC API
-   Live GPS tracking
-   Chat
-   Push notifications
-   AI recommendations
-   Dynamic pricing
-   Complex provider ranking
-   Subscription plans
-   Corporate accounts
-   Laundry logistics
-   Multi-provider jobs
-   Advanced analytics
-   Native iOS app
-   Native Android app
-   Microservices

Design the system so these can be added later.

------------------------------------------------------------------------

# 25. UI/UX RULES

The UI must be:

-   Mobile-first
-   Extremely clear
-   Fast
-   Spacious
-   Trustworthy
-   Calm
-   Modern
-   Accessible

Use cards sparingly.

Prioritize large service imagery, clear CTAs and short forms.

Every screen should answer: "What do I do next?"

Use progressive disclosure: Only ask for information when it becomes
relevant.

Avoid giant forms.

------------------------------------------------------------------------

# 26. LANDING PAGE INFORMATION ARCHITECTURE

Hero:

SIR logo

Headline: **Services that come to you.**

Subheadline: "Book trusted professionals for beauty, fitness, cleaning
and car care --- wherever you are."

CTA: **Book a service**

Secondary: **Become a provider**

Then:

## How it works

1.  Pick a service
2.  Choose when and where
3.  A verified professional comes to you

## Services

Beauty Fitness Cleaning Car care

## Why SIR

Verified professionals Convenient booking Transparent pricing Local
providers Ratings and reviews

## For providers

"Turn your skills into more bookings."

CTA: **Become a SIR provider**

## For businesses

"Already run a service business?"

CTA: **Partner with SIR**

## Trust

Verification Reviews Support Safety messaging

------------------------------------------------------------------------

# 27. COPY STYLE

Short.

Human.

Confident.

Examples:

"Need a clean? We've got you."

"Your workout. Your place."

"Salon-quality, without the salon."

"Your car. Your driveway. Done."

Avoid: "Leverage our innovative platform to facilitate..."

Write like a modern consumer technology company.

------------------------------------------------------------------------

# 28. ENGINEERING WORKFLOW FOR THE AI CODING AGENT

The AI must NOT generate the entire application in one uncontrolled
pass.

Build in milestones.

## Milestone 1 --- Project setup

Create: - Next.js app - FastAPI app - PostgreSQL - Docker Compose -
Environment configuration - README

Verify everything runs.

## Milestone 2 --- Database

Create: - migrations - models - seed data

Seed: - categories - services - example providers - example service
packages

Run migrations successfully.

## Milestone 3 --- Authentication

Implement: - customer signup/login - provider signup/login - roles -
protected routes

## Milestone 4 --- Customer

Implement: - landing page - service browsing - service details - booking
form - booking creation - customer booking history

## Milestone 5 --- Provider

Implement: - provider onboarding - verification status - service
selection - provider dashboard - nearby job list - accept/decline -
upcoming jobs

## Milestone 6 --- Booking lifecycle

Test:

CUSTOMER CREATES BOOKING → PROVIDER SEES JOB → PROVIDER ACCEPTS →
CUSTOMER SEES ACCEPTED → PROVIDER STARTS → PROVIDER COMPLETES → CUSTOMER
SEES COMPLETED

## Milestone 7 --- Admin

Implement: - provider approval - booking overview - partnership
enquiries

## Milestone 8 --- Polish

Improve: - responsive UI - loading states - empty states - errors -
validation - accessibility - visual consistency

------------------------------------------------------------------------

# 29. AI AGENT BEHAVIOR RULES

You are a senior full-stack engineer working on SIR.

Before coding: 1. Inspect the repository. 2. Understand existing
architecture. 3. Do not overwrite working functionality unnecessarily.
4. Explain the implementation plan briefly. 5. Then execute.

After every meaningful milestone: 1. Run tests. 2. Run lint/type checks.
3. Run migrations. 4. Verify the application starts. 5. Fix errors. 6.
Only then continue.

Never claim something works without testing it.

Prefer simple solutions.

Do not introduce dependencies unless necessary.

Do not invent APIs.

Do not hard-code business-critical pricing.

Use environment variables for configuration.

Use database migrations for schema changes.

Use seed data for local development.

When a requirement is ambiguous: - Make the smallest reasonable
assumption. - Document it. - Continue. - Do not stop the build
unnecessarily.

When an error occurs: - Diagnose the root cause. - Fix it. - Re-run the
relevant test. - Do not hide or suppress errors.

------------------------------------------------------------------------

# 30. DEFINITION OF DONE FOR MVP V0.1

The MVP is considered functional when:

CUSTOMER: - Can visit landing page - Can understand SIR - Can browse
services - Can create an account - Can log in - Can choose a service -
Can provide service-specific details - Can choose a location - Can
select a date/time - Can create a booking - Can view booking status -
Can view booking history

PROVIDER: - Can create provider account - Can complete onboarding - Can
select services - Can enter pricing - Can provide service area - Can
submit verification - Can see verification status - Can view available
jobs - Can accept/decline jobs - Can view upcoming jobs - Can change job
status

ADMIN: - Can view providers - Can approve/reject providers - Can view
bookings - Can view partnership enquiries

SYSTEM: - Database persists data - API validates input - Roles are
enforced - Frontend communicates with backend - Docker Compose runs the
system locally - Tests cover the critical booking lifecycle

------------------------------------------------------------------------

# 31. PRODUCT ROADMAP

V0.1: Marketplace skeleton.

V0.2: Payments.

V0.3: Notifications + WhatsApp.

V0.4: Reviews + stronger trust/safety.

V0.5: Better provider matching.

V1: Corporate accounts.

V1.5: Partner businesses.

V2: Laundry/logistics.

V3: Subscriptions and loyalty.

V4: Intelligent marketplace automation.

------------------------------------------------------------------------

# 32. LONG-TERM SIR VISION

SIR should become an orchestration platform for local services.

The long-term platform should support:

Customer → service → provider/business → booking → payment → fulfilment
→ logistics → review → repeat booking

Supply can come from: - Individuals - Small businesses - Established
businesses - Partner networks

SIR becomes the demand and coordination layer.

The long-term competitive advantage should come from: - Local provider
density - Trust and verification - Customer data - Booking history -
Provider reliability data - Pricing intelligence - Operational
efficiency - Brand - Repeat usage - Business integrations - Logistics
capabilities

Do not attempt to build all of this in MVP.

Build the transaction first.

------------------------------------------------------------------------

# 33. FIRST VERTICAL SLICE

The first end-to-end implementation should be:

CUSTOMER: Signup → Choose cleaning → Choose 3-bedroom standard clean →
Select date/time → Enter address → Submit booking

PROVIDER: Login → See nearby cleaning job → Accept

CUSTOMER: See accepted booking

PROVIDER: Mark EN_ROUTE → Mark IN_PROGRESS → Mark COMPLETED

CUSTOMER: See COMPLETED

This vertical slice proves the marketplace works.

Then generalize it to beauty, fitness and car washing.

------------------------------------------------------------------------

# 34. FINAL PRODUCT PRINCIPLE

Do not build a complicated service marketplace.

Build the easiest way for someone to say:

**"I need someone to do this. Send them to me."**

That is SIR.
