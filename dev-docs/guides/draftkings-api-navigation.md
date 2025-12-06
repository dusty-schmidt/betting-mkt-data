# DraftKings API Navigation & Extraction Guide

This document details the reverse-engineered workflow for programmatically navigating the DraftKings Sportsbook API to extract game lines and prop markets.

## Overview

DraftKings uses a **Dynamic Content System**. Unlike traditional REST APIs with static endpoints (e.g., `/get_odds`), it uses a **Manifest-Template-Query** architecture.

1.  **Manifest**: Defines the available Sports and Leagues.
2.  **Template**: Defines the structure of a League page, including available data sources (Queries).
3.  **Market URL**: Constructed dynamically by combining a Query with specific variables (Reference ID, Subcategory ID).

## Core Workflow

### 1. Fetch the Manifest
The entry point is the configured `manifest_url` (usually accessing the `/v1/sports` or similar configuration endpoint).

*   **Goal**: Find the `league_id` (numeric) and `template_id` (UUID) for your target Sport/League.
*   **Key Data**:
    *   `league_id`: e.g., `88808` (NFL), `42648` (NBA).
    *   **Subcategories**: Often hidden in the navigation menu within the Manifest or a separate Navigation call.

### 2. Fetch the Template
Using the `template_id` found in the Manifest, request the Template JSON.

*   **URL Pattern**: `https://sportsbook.draftkings.com/api/sportscontent/dkusoh/v1/pages/{template_id}?format=json`
*   **Goal**: Extract **Market Queries**.
*   **Structure**: Look for `data.sets` in the JSON. These represent the generic SQL-like queries the frontend uses to fetch data.
    *   `name`: The identifier for the query (e.g., `SLSWD5OData`).
    *   `parameters`: Contains template variables like `@leagueId` and `@subcategoryId`.

### 3. Construct the Market URL
To fetch actual odds, you must "hydrate" the query template.

*   **Base Pattern**: `https://sportsbook-us-oh.draftkings.com//sites/US-OH-SB/api/v5/eventgroups/{league_id}?format=json` (This is the simplified Game Lines endpoint).
*   **Advanced Pattern (Dynamic)**:
    For specific subcategories (Props), you assume the structure matches the queries found in Step 2, but practically, the API often exposes a cleaner route:
    
    `https://sportsbook.draftkings.com//sites/US-OH-SB/api/v5/eventgroups/{league_id}/categories/{subcategory_id}?format=json`

    *   `league_id`: From Step 1.
    *   `subcategory_id`: The ID for the specific market group (e.g., `16477` for NBA Player Points).

### 4. Parsing the Response
The response contains `events` (Match metadata) and `markets` (The betting lines).

*   **Events**: Contains Teams, Start Time, Status.
*   **Markets**: Contains the betting options (Moneyline, Spread, Total, Player Props).
*   **Selections**: The actual outcomes and odds.

## Configuration & Scaling

To support extracting **ALL** markets without hardcoding, the system should:

1.  **Discover Subcategories**: Parse the Navigation menus to build a map of `{"Market Name": "Subcategory ID"}` for each sport.
2.  **Config-Driven Fetching**: The extraction client should accept a `subcategory` argument and look up the ID from this map.
3.  **Generic Parsing**: The parser must be agnostic to Market Names, simply linking `Market -> Selection` pairs to the `Game/Event`.

## Architecture Soundness Note

The current architecture (Config -> Client -> Parser) is robust for this expansion because:
1.  **Decoupled Selection**: The `client` doesn't care *what* it's fetching, only *how* (ID lookup).
2.  **Stable IDs**: Since subcategory IDs are relatively stable, caching them in `config.yaml` is efficient.
3.  **Isolation**: Fetching "Player Props" uses a distinct API call key from "Game Lines", so expanding to props does not risk the stability of the core Game Line extraction.
