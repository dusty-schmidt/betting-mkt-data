# DraftKings API Dynamic Discovery Workflow

This document outlines the dynamic discovery process used by the DraftKings API to fetch betting market data. Unlike traditional APIs with static endpoints, DraftKings uses a 3-step flow that requires dynamic extraction of IDs and queries.

## Overview

The workflow consists of three main steps:
1.  **Manifest**: Discover available sports and their current configuration.
2.  **Template**: Retrieve the page structure and specific queries for a sport.
3.  **Market Data**: Fetch the actual odds using the constructed query.

## Step 1: Manifest

**Endpoint**: `https://sportsbook-nash.draftkings.com/sites/US-OH-SB/api/sportslayout/v1/manifest?format=json`

**Purpose**: To find the current `templateId` and `leagueId` for the desired sport.

**Key Data to Extract**:
*   Iterate through `sidebar.navigationMenu.items`.
*   Find the item where `title` matches the sport (e.g., "NFL", "NBA").
*   Extract:
    *   `templateId`: The ID of the page template (e.g., `02d63505-bc8a-47d7-9ab4-eae634706188__client_web_1.4.0`).
    *   `leagueId`: The numeric ID of the league (e.g., `88808` for NFL, `42648` for NBA).

## Step 2: Template

**Endpoint**: `https://sportsbook-nash.draftkings.com/sites/US-OH-SB/api/sportsstructure/v1/templates/{templateId}?format=json`

**Purpose**: To define the structure of the betting page and identify the correct query for the desired market tab (e.g., "Game Lines").

**Key Data to Extract**:
*   The template contains a list of `modules`.
*   Look for modules that define the market tabs.
*   Identify the query associated with the "Game Lines" tab.
*   **Crucial**: The query string often contains placeholders like `@leagueId` and `@subcategoryId`.
*   **Subcategory IDs**:
    *   NFL Game Lines: `4518`
    *   NBA Game Lines: `4511`

## Step 3: Market Data

**Endpoint**: `https://sportsbook-nash.draftkings.com/sites/US-OH-SB/api/sportscontent/controldata/league/leagueSubcategory/v1/markets`

**Purpose**: To fetch the actual event and odds data.

**URL Construction**:
*   **Base URL**: `https://sportsbook-nash.draftkings.com/sites/US-OH-SB/api/sportscontent/controldata/league/leagueSubcategory/v1/markets`
*   **Parameters**:
    *   `isBatchable`: `false`
    *   `templateVars`: The `leagueId` (e.g., `88808`).
    *   `eventsQuery`: The extracted query string with placeholders replaced.
        *   Replace `@leagueId` with the actual `leagueId`.
        *   Replace `@subcategoryId` with the specific ID (e.g., `4518`).
    *   `marketsQuery`: Similar to `eventsQuery`, usually filtering by subcategory.
    *   `include`: `Events`
    *   `entity`: `events`

## Data Parsing

The response is a relational JSON structure, not a simple list of objects.

1.  **Events**: Located in `events`. Contains game info (teams, start time, `eventId`).
2.  **Markets**: Located in `markets`. Linked to events via `eventId`. Contains market info (name like "Moneyline", "Spread", `marketId`).
3.  **Selections**: Located in `selections`. Linked to markets via `marketId`. Contains the actual odds (`trueOdds`, `points`).

**Mapping Logic**:
*   Iterate through `events`.
*   For each event, find all `markets` where `market.eventId == event.eventId`.
*   Filter markets by `name` (e.g., "Moneyline", "Spread", "Total").
*   For each market, find all `selections` where `selection.marketId == market.marketId`.
*   Extract the odds from the selections.

## Example: NFL Flow

1.  **Manifest**: Found NFL. `templateId` = `abc-123`, `leagueId` = `88808`.
2.  **Template**: Fetched `abc-123`. Found query `WPY62O4Data` for Game Lines.
3.  **Market Data**:
    *   Constructed URL with `leagueId=88808` and `subcategoryId=4518`.
    *   Fetched data.
    *   Parsed:
        *   Event: CIN Bengals @ BUF Bills
        *   Market: Moneyline
        *   Selection: CIN Bengals (+230)