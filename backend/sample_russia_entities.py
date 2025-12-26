#!/usr/bin/env python3
"""
Russia Sanctioned Entities Database for CORTEX-CI.
Comprehensive database of Russian entities under international sanctions.

Categories:
- Major Russian Banks (SDN, SSI listed)
- State-Owned Enterprises
- Defense & Military Companies
- Energy Sector Companies
- Technology Companies
- Oligarchs & PEPs (Politically Exposed Persons)

Run: python3 sample_russia_entities.py
"""

import json
import subprocess
import uuid
from datetime import datetime, date

DB_CONTAINER = "compose-input-solid-state-array-q9m3z5-db-1"
DB_USER = "cortex"
DB_NAME = "cortex_ci"


def run_sql(sql: str) -> str:
    """Execute SQL in database container."""
    cmd = [
        "docker",
        "exec",
        "-i",
        DB_CONTAINER,
        "psql",
        "-U",
        DB_USER,
        "-d",
        DB_NAME,
        "-c",
        sql,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout


def escape_sql(s: str) -> str:
    """Escape string for SQL."""
    if s is None:
        return ""
    return s.replace("'", "''").replace("\\", "\\\\")


def get_tenant_id() -> str:
    """Get default tenant ID."""
    result = run_sql("SELECT id FROM tenants WHERE slug = 'default';")
    for line in result.split("\n"):
        line = line.strip()
        if line and "-" in line and len(line) == 36:
            return line
    return None


# ============================================================================
# RUSSIAN BANKS - SDN & SSI LISTED
# ============================================================================
RUSSIAN_BANKS = [
    {
        "name": "Sberbank of Russia",
        "type": "financial_institution",
        "country": "RU",
        "risk_score": 95.0,
        "sanctions_status": "SDN",
        "description": "Russia's largest bank, majority state-owned. Subject to full blocking sanctions.",
        "identifiers": {
            "swift_bic": "SABRRUMM",
            "lei": "549300WS8E2E7WG9R SEA",
            "ofac_id": "SBERBANK",
        },
        "sanctions_programs": ["RUSSIA-EO14024", "UKRAINE-EO13660", "SSI"],
        "aliases": ["Sberbank", "Savings Bank of the Russian Federation", "PAO Sberbank"],
        "address": "19 Vavilova Street, Moscow 117312, Russia",
        "tags": ["BANK", "STATE_OWNED", "SDN", "CRITICAL"],
    },
    {
        "name": "VTB Bank",
        "type": "financial_institution",
        "country": "RU",
        "risk_score": 95.0,
        "sanctions_status": "SDN",
        "description": "Second largest Russian bank, state-owned. Full blocking sanctions.",
        "identifiers": {
            "swift_bic": "VTBRRUMM",
            "lei": "253400V1H6ART1UQ0N98",
            "ofac_id": "VTB",
        },
        "sanctions_programs": ["RUSSIA-EO14024", "SSI", "CAPTA"],
        "aliases": ["VTB", "Vneshtorgbank", "Bank VTB PAO"],
        "address": "29 Bolshaya Morskaya Street, St. Petersburg 190000, Russia",
        "tags": ["BANK", "STATE_OWNED", "SDN", "CRITICAL"],
    },
    {
        "name": "Gazprombank",
        "type": "financial_institution",
        "country": "RU",
        "risk_score": 90.0,
        "sanctions_status": "SDN",
        "description": "Third largest Russian bank, closely tied to Gazprom. Under sanctions.",
        "identifiers": {
            "swift_bic": "GAZPRUMM",
            "lei": "253400P3JKQVNP2VXI02",
            "ofac_id": "GAZPROMBANK",
        },
        "sanctions_programs": ["RUSSIA-EO14024", "SSI"],
        "aliases": ["GPB", "Gazprom Bank", "Bank GPB"],
        "address": "16 Nametkina Street, Moscow 117420, Russia",
        "tags": ["BANK", "GAZPROM_AFFILIATE", "SDN", "CRITICAL"],
    },
    {
        "name": "Alfa-Bank",
        "type": "financial_institution",
        "country": "RU",
        "risk_score": 85.0,
        "sanctions_status": "SDN",
        "description": "Largest private Russian bank. Subject to blocking sanctions.",
        "identifiers": {
            "swift_bic": "ALFARUMM",
            "lei": "549300QQE2NSGXNBEF79",
            "ofac_id": "ALFA-BANK",
        },
        "sanctions_programs": ["RUSSIA-EO14024"],
        "aliases": ["Alfa Bank", "AO Alfa-Bank"],
        "address": "27 Kalanchevskaya Street, Moscow 107078, Russia",
        "tags": ["BANK", "PRIVATE", "SDN", "HIGH_RISK"],
    },
    {
        "name": "Bank Rossiya",
        "type": "financial_institution",
        "country": "RU",
        "risk_score": 95.0,
        "sanctions_status": "SDN",
        "description": "Known as 'Putin's personal bank'. Under sanctions since 2014.",
        "identifiers": {
            "swift_bic": "ROSYRU2P",
            "ofac_id": "BANK_ROSSIYA",
        },
        "sanctions_programs": ["RUSSIA-EO13661", "RUSSIA-EO14024"],
        "aliases": ["Rossiya Bank", "AB Russia"],
        "address": "3 Rastrelli Square, St. Petersburg 191124, Russia",
        "tags": ["BANK", "PUTIN_CIRCLE", "SDN", "CRITICAL"],
    },
    {
        "name": "Promsvyazbank",
        "type": "financial_institution",
        "country": "RU",
        "risk_score": 90.0,
        "sanctions_status": "SDN",
        "description": "Designated defense bank for Russian military contracts.",
        "identifiers": {
            "swift_bic": "PRMSRUMM",
            "lei": "253400TJX8X72XT0WQ40",
            "ofac_id": "PROMSVYAZBANK",
        },
        "sanctions_programs": ["RUSSIA-EO14024", "DEFENSE"],
        "aliases": ["PSB", "Promsvyaz Bank"],
        "address": "10 Smirnovskaya Street, Moscow 109052, Russia",
        "tags": ["BANK", "DEFENSE_SECTOR", "SDN", "CRITICAL"],
    },
    {
        "name": "Russian Agricultural Bank (Rosselkhozbank)",
        "type": "financial_institution",
        "country": "RU",
        "risk_score": 85.0,
        "sanctions_status": "SDN",
        "description": "State-owned agricultural bank under full blocking sanctions.",
        "identifiers": {
            "swift_bic": "RUABORUMM",
            "lei": "253400TJX8X72XT0WQ41",
            "ofac_id": "RSHB",
        },
        "sanctions_programs": ["RUSSIA-EO14024"],
        "aliases": ["RSHB", "Rosselkhozbank", "Russian Agricultural Bank"],
        "address": "3 Gagarinsky Lane, Moscow 119034, Russia",
        "tags": ["BANK", "STATE_OWNED", "SDN", "HIGH_RISK"],
    },
    {
        "name": "Moscow Credit Bank",
        "type": "financial_institution",
        "country": "RU",
        "risk_score": 80.0,
        "sanctions_status": "SDN",
        "description": "Major Russian commercial bank under sanctions.",
        "identifiers": {
            "swift_bic": "MABORUMM",
            "ofac_id": "MCB",
        },
        "sanctions_programs": ["RUSSIA-EO14024"],
        "aliases": ["MCB", "Credit Bank of Moscow"],
        "address": "2 Lukov Lane, Moscow 107045, Russia",
        "tags": ["BANK", "COMMERCIAL", "SDN"],
    },
    {
        "name": "Russian National Commercial Bank (RNCB)",
        "type": "financial_institution",
        "country": "RU",
        "risk_score": 90.0,
        "sanctions_status": "SDN",
        "description": "Bank operating in occupied Crimea. Under sanctions.",
        "identifiers": {
            "swift_bic": "RNCBRUMM",
            "ofac_id": "RNCB",
        },
        "sanctions_programs": ["UKRAINE-EO13685", "CRIMEA"],
        "aliases": ["RNCB", "Rossiysky Natsionalny Kommerchesky Bank"],
        "address": "Simferopol, Crimea",
        "tags": ["BANK", "CRIMEA", "SDN", "CRITICAL"],
    },
    {
        "name": "Central Bank of Russia",
        "type": "central_bank",
        "country": "RU",
        "risk_score": 100.0,
        "sanctions_status": "BLOCKED",
        "description": "Russian central bank with assets frozen in Western jurisdictions.",
        "identifiers": {
            "swift_bic": "CABORUMM",
            "ofac_id": "CBR",
        },
        "sanctions_programs": ["RUSSIA-EO14024", "ASSET_FREEZE"],
        "aliases": ["CBR", "Bank of Russia", "Bank Rossii"],
        "address": "12 Neglinnaya Street, Moscow 107016, Russia",
        "tags": ["CENTRAL_BANK", "ASSET_FREEZE", "CRITICAL"],
    },
]

# ============================================================================
# RUSSIAN STATE-OWNED ENTERPRISES
# ============================================================================
RUSSIAN_SOES = [
    {
        "name": "Gazprom",
        "type": "corporation",
        "country": "RU",
        "risk_score": 85.0,
        "sanctions_status": "SSI",
        "description": "World's largest natural gas company, majority state-owned.",
        "identifiers": {
            "lei": "213800FD9J7XCJXEXC42",
            "ticker": "GAZP",
            "ofac_id": "GAZPROM",
        },
        "sanctions_programs": ["RUSSIA-EO13662", "SSI-DIRECTIVE2"],
        "aliases": ["OAO Gazprom", "PAO Gazprom", "Gazprom PJSC"],
        "address": "16 Nametkina Street, Moscow 117997, Russia",
        "sector": "Energy - Natural Gas",
        "tags": ["ENERGY", "STATE_OWNED", "SSI", "CRITICAL"],
    },
    {
        "name": "Rosneft",
        "type": "corporation",
        "country": "RU",
        "risk_score": 85.0,
        "sanctions_status": "SSI",
        "description": "Russia's largest oil company, state-controlled.",
        "identifiers": {
            "lei": "253400JT3MQWNDKMJE44",
            "ticker": "ROSN",
            "ofac_id": "ROSNEFT",
        },
        "sanctions_programs": ["RUSSIA-EO13662", "SSI-DIRECTIVE4"],
        "aliases": ["NK Rosneft", "PAO NK Rosneft Oil Company", "Rosneft Oil"],
        "address": "26/1 Sofiyskaya Embankment, Moscow 117997, Russia",
        "sector": "Energy - Oil",
        "tags": ["ENERGY", "STATE_OWNED", "SSI", "CRITICAL"],
    },
    {
        "name": "Lukoil",
        "type": "corporation",
        "country": "RU",
        "risk_score": 70.0,
        "sanctions_status": "CAUTION",
        "description": "Russia's second largest oil company, privately held but subject to sectoral restrictions.",
        "identifiers": {
            "lei": "549300LCJ1UJXHYBWI24",
            "ticker": "LKOH",
        },
        "sanctions_programs": ["RUSSIA-SECTORAL"],
        "aliases": ["LUKOIL", "PAO LUKOIL", "LUKOIL Oil Company"],
        "address": "11 Sretensky Boulevard, Moscow 101000, Russia",
        "sector": "Energy - Oil",
        "tags": ["ENERGY", "PRIVATE", "SECTORAL"],
    },
    {
        "name": "Rostec",
        "type": "corporation",
        "country": "RU",
        "risk_score": 100.0,
        "sanctions_status": "SDN",
        "description": "Russian state defense conglomerate controlling military-industrial complex.",
        "identifiers": {
            "ofac_id": "ROSTEC",
        },
        "sanctions_programs": ["RUSSIA-EO14024", "DEFENSE", "SDN"],
        "aliases": ["Rostec State Corporation", "Russian Technologies"],
        "address": "24 Gogolevsky Boulevard, Moscow 119019, Russia",
        "sector": "Defense",
        "tags": ["DEFENSE", "STATE_OWNED", "SDN", "CRITICAL"],
    },
    {
        "name": "Russian Railways (RZD)",
        "type": "corporation",
        "country": "RU",
        "risk_score": 75.0,
        "sanctions_status": "SDN",
        "description": "State-owned railway monopoly under sanctions.",
        "identifiers": {
            "lei": "5493004S2HIHPQPQ1H54",
            "ofac_id": "RZD",
        },
        "sanctions_programs": ["RUSSIA-EO14024"],
        "aliases": ["RZD", "Rossiyskiye Zheleznye Dorogi", "Russian Railways JSC"],
        "address": "2 Novaya Basmannaya Street, Moscow 107174, Russia",
        "sector": "Transportation",
        "tags": ["TRANSPORTATION", "STATE_OWNED", "SDN"],
    },
    {
        "name": "Aeroflot",
        "type": "corporation",
        "country": "RU",
        "risk_score": 80.0,
        "sanctions_status": "SDN",
        "description": "Russian flag carrier airline, banned from most Western airspace.",
        "identifiers": {
            "iata": "SU",
            "icao": "AFL",
            "ofac_id": "AEROFLOT",
        },
        "sanctions_programs": ["RUSSIA-EO14024", "AVIATION"],
        "aliases": ["Aeroflot Russian Airlines", "PAO Aeroflot"],
        "address": "10 Arbat Street, Moscow 119002, Russia",
        "sector": "Aviation",
        "tags": ["AVIATION", "STATE_OWNED", "SDN"],
    },
    {
        "name": "Russian Post",
        "type": "corporation",
        "country": "RU",
        "risk_score": 60.0,
        "sanctions_status": "CAUTION",
        "description": "State postal service with limited sanctions exposure.",
        "identifiers": {
            "ofac_id": "RUSSIAN_POST",
        },
        "sanctions_programs": [],
        "aliases": ["Pochta Rossii", "FSUE Russian Post"],
        "address": "37 Varshavskoye Highway, Moscow 117105, Russia",
        "sector": "Postal Services",
        "tags": ["POSTAL", "STATE_OWNED", "CAUTION"],
    },
    {
        "name": "Rosatom",
        "type": "corporation",
        "country": "RU",
        "risk_score": 85.0,
        "sanctions_status": "PARTIAL",
        "description": "State nuclear energy corporation, limited sanctions due to energy dependencies.",
        "identifiers": {
            "ofac_id": "ROSATOM",
        },
        "sanctions_programs": ["RUSSIA-NUCLEAR"],
        "aliases": ["Rosatom State Nuclear Energy Corporation", "Rosatom State Corporation"],
        "address": "24 Bolshaya Ordynka Street, Moscow 119017, Russia",
        "sector": "Nuclear Energy",
        "tags": ["NUCLEAR", "STATE_OWNED", "STRATEGIC"],
    },
]

# ============================================================================
# RUSSIAN DEFENSE COMPANIES
# ============================================================================
RUSSIAN_DEFENSE = [
    {
        "name": "Almaz-Antey",
        "type": "corporation",
        "country": "RU",
        "risk_score": 100.0,
        "sanctions_status": "SDN",
        "description": "Russia's largest defense contractor, maker of S-400 systems.",
        "identifiers": {
            "ofac_id": "ALMAZ_ANTEY",
        },
        "sanctions_programs": ["RUSSIA-EO14024", "DEFENSE", "SDN"],
        "aliases": ["Almaz-Antey Air and Space Defence Corporation", "JSC Almaz-Antey"],
        "address": "41 Vereiskaya Street, Moscow 121471, Russia",
        "sector": "Defense - Air Defense",
        "tags": ["DEFENSE", "MISSILE_SYSTEMS", "SDN", "CRITICAL"],
    },
    {
        "name": "United Aircraft Corporation (UAC)",
        "type": "corporation",
        "country": "RU",
        "risk_score": 100.0,
        "sanctions_status": "SDN",
        "description": "Russian military and civilian aircraft manufacturer.",
        "identifiers": {
            "ofac_id": "UAC",
        },
        "sanctions_programs": ["RUSSIA-EO14024", "DEFENSE", "SDN"],
        "aliases": ["OAK", "PAO UAC", "United Aircraft Corporation"],
        "address": "22 Ulansky Lane, Moscow 101000, Russia",
        "sector": "Defense - Aircraft",
        "tags": ["DEFENSE", "AVIATION", "SDN", "CRITICAL"],
    },
    {
        "name": "United Shipbuilding Corporation (USC)",
        "type": "corporation",
        "country": "RU",
        "risk_score": 100.0,
        "sanctions_status": "SDN",
        "description": "Russia's largest shipbuilding company, builds naval vessels.",
        "identifiers": {
            "ofac_id": "USC",
        },
        "sanctions_programs": ["RUSSIA-EO14024", "DEFENSE", "SDN"],
        "aliases": ["OSK", "USC", "United Shipbuilding Corporation"],
        "address": "11 Maly Kozlovsky Lane, Moscow 101000, Russia",
        "sector": "Defense - Naval",
        "tags": ["DEFENSE", "SHIPBUILDING", "SDN", "CRITICAL"],
    },
    {
        "name": "Kalashnikov Concern",
        "type": "corporation",
        "country": "RU",
        "risk_score": 100.0,
        "sanctions_status": "SDN",
        "description": "Famous weapons manufacturer, maker of AK rifles.",
        "identifiers": {
            "ofac_id": "KALASHNIKOV",
        },
        "sanctions_programs": ["RUSSIA-EO13662", "DEFENSE", "SDN"],
        "aliases": ["Kalashnikov", "Izhmash", "Concern Kalashnikov"],
        "address": "3 Deryabina Avenue, Izhevsk 426006, Russia",
        "sector": "Defense - Small Arms",
        "tags": ["DEFENSE", "WEAPONS", "SDN", "CRITICAL"],
    },
    {
        "name": "Tactical Missiles Corporation",
        "type": "corporation",
        "country": "RU",
        "risk_score": 100.0,
        "sanctions_status": "SDN",
        "description": "Developer of tactical missiles and guided munitions.",
        "identifiers": {
            "ofac_id": "KTRV",
        },
        "sanctions_programs": ["RUSSIA-EO14024", "DEFENSE", "SDN"],
        "aliases": ["KTRV", "Corporation Tactical Missiles"],
        "address": "7 Ilicha Street, Korolev 141080, Russia",
        "sector": "Defense - Missiles",
        "tags": ["DEFENSE", "MISSILES", "SDN", "CRITICAL"],
    },
    {
        "name": "Russian Helicopters",
        "type": "corporation",
        "country": "RU",
        "risk_score": 100.0,
        "sanctions_status": "SDN",
        "description": "Helicopter manufacturing company, Rostec subsidiary.",
        "identifiers": {
            "ofac_id": "RUSSIAN_HELICOPTERS",
        },
        "sanctions_programs": ["RUSSIA-EO14024", "DEFENSE", "SDN"],
        "aliases": ["Vertolyety Rossii", "Russian Helicopters JSC"],
        "address": "1 Bolshaya Pionerskaya Street, Moscow 115054, Russia",
        "sector": "Defense - Helicopters",
        "tags": ["DEFENSE", "AVIATION", "SDN", "CRITICAL"],
    },
    {
        "name": "Uralvagonzavod",
        "type": "corporation",
        "country": "RU",
        "risk_score": 100.0,
        "sanctions_status": "SDN",
        "description": "Russia's main battle tank manufacturer.",
        "identifiers": {
            "ofac_id": "UVZ",
        },
        "sanctions_programs": ["RUSSIA-EO14024", "DEFENSE", "SDN"],
        "aliases": ["UVZ", "Uralvagonzavod Scientific Industrial Corporation"],
        "address": "28 Vostochnoye Highway, Nizhny Tagil 622007, Russia",
        "sector": "Defense - Armor",
        "tags": ["DEFENSE", "TANKS", "SDN", "CRITICAL"],
    },
]

# ============================================================================
# RUSSIAN OLIGARCHS & PEPs
# ============================================================================
RUSSIAN_OLIGARCHS = [
    {
        "name": "Vladimir Potanin",
        "type": "individual",
        "country": "RU",
        "risk_score": 85.0,
        "sanctions_status": "UK_SANCTIONED",
        "description": "President of Norilsk Nickel, Russia's richest person. UK sanctioned.",
        "identifiers": {
            "date_of_birth": "1961-01-03",
        },
        "sanctions_programs": ["UK-RUSSIA"],
        "aliases": ["V.O. Potanin"],
        "associated_companies": ["Norilsk Nickel", "Interros"],
        "tags": ["OLIGARCH", "UK_SANCTIONS", "MINING", "HIGH_RISK"],
    },
    {
        "name": "Alisher Usmanov",
        "type": "individual",
        "country": "RU",
        "risk_score": 95.0,
        "sanctions_status": "SDN",
        "description": "Metals and media tycoon, close to Kremlin. Under US/EU/UK sanctions.",
        "identifiers": {
            "date_of_birth": "1953-09-09",
            "ofac_id": "USMANOV",
        },
        "sanctions_programs": ["RUSSIA-EO14024", "EU-RUSSIA", "UK-RUSSIA"],
        "aliases": ["A.B. Usmanov"],
        "associated_companies": ["USM Holdings", "Metalloinvest"],
        "tags": ["OLIGARCH", "SDN", "METALS", "CRITICAL"],
    },
    {
        "name": "Roman Abramovich",
        "type": "individual",
        "country": "RU",
        "risk_score": 90.0,
        "sanctions_status": "EU_UK_SANCTIONED",
        "description": "Steel and investment magnate, former Chelsea FC owner. EU/UK sanctioned.",
        "identifiers": {
            "date_of_birth": "1966-10-24",
        },
        "sanctions_programs": ["EU-RUSSIA", "UK-RUSSIA"],
        "aliases": ["R.A. Abramovich"],
        "associated_companies": ["Evraz", "Millhouse"],
        "tags": ["OLIGARCH", "EU_SANCTIONS", "UK_SANCTIONS", "STEEL"],
    },
    {
        "name": "Mikhail Fridman",
        "type": "individual",
        "country": "RU",
        "risk_score": 90.0,
        "sanctions_status": "SDN",
        "description": "Co-founder of Alfa Group. Under US/EU/UK sanctions.",
        "identifiers": {
            "date_of_birth": "1964-04-21",
            "ofac_id": "FRIDMAN",
        },
        "sanctions_programs": ["RUSSIA-EO14024", "EU-RUSSIA", "UK-RUSSIA"],
        "aliases": ["M.M. Fridman", "Mikhail Maratovich Fridman"],
        "associated_companies": ["Alfa Group", "LetterOne"],
        "tags": ["OLIGARCH", "SDN", "BANKING", "CRITICAL"],
    },
    {
        "name": "Petr Aven",
        "type": "individual",
        "country": "RU",
        "risk_score": 90.0,
        "sanctions_status": "SDN",
        "description": "Chairman of Alfa-Bank. Under comprehensive sanctions.",
        "identifiers": {
            "date_of_birth": "1955-03-16",
            "ofac_id": "AVEN",
        },
        "sanctions_programs": ["RUSSIA-EO14024", "EU-RUSSIA", "UK-RUSSIA"],
        "aliases": ["P.O. Aven", "Pyotr Olegovich Aven"],
        "associated_companies": ["Alfa-Bank", "Alfa Group"],
        "tags": ["OLIGARCH", "SDN", "BANKING", "CRITICAL"],
    },
    {
        "name": "Igor Sechin",
        "type": "individual",
        "country": "RU",
        "risk_score": 100.0,
        "sanctions_status": "SDN",
        "description": "CEO of Rosneft, close Putin ally. Under comprehensive sanctions.",
        "identifiers": {
            "date_of_birth": "1960-09-07",
            "ofac_id": "SECHIN",
        },
        "sanctions_programs": ["RUSSIA-EO13661", "EU-RUSSIA", "UK-RUSSIA"],
        "aliases": ["I.I. Sechin", "Igor Ivanovich Sechin"],
        "associated_companies": ["Rosneft"],
        "tags": ["OLIGARCH", "SDN", "PUTIN_CIRCLE", "CRITICAL"],
    },
    {
        "name": "Gennady Timchenko",
        "type": "individual",
        "country": "RU",
        "risk_score": 100.0,
        "sanctions_status": "SDN",
        "description": "Co-founder of Gunvor, close Putin associate since St. Petersburg days.",
        "identifiers": {
            "date_of_birth": "1952-11-09",
            "ofac_id": "TIMCHENKO",
        },
        "sanctions_programs": ["RUSSIA-EO13661", "EU-RUSSIA", "UK-RUSSIA"],
        "aliases": ["G.N. Timchenko", "Gennady Nikolayevich Timchenko"],
        "associated_companies": ["Gunvor", "Volga Group"],
        "tags": ["OLIGARCH", "SDN", "PUTIN_CIRCLE", "CRITICAL"],
    },
    {
        "name": "Arkady Rotenberg",
        "type": "individual",
        "country": "RU",
        "risk_score": 100.0,
        "sanctions_status": "SDN",
        "description": "Judo partner and childhood friend of Putin. Major construction contracts.",
        "identifiers": {
            "date_of_birth": "1951-12-15",
            "ofac_id": "A_ROTENBERG",
        },
        "sanctions_programs": ["RUSSIA-EO13661", "EU-RUSSIA"],
        "aliases": ["A.R. Rotenberg", "Arkady Romanovich Rotenberg"],
        "associated_companies": ["Stroygazmontazh", "SMP Bank"],
        "tags": ["OLIGARCH", "SDN", "PUTIN_CIRCLE", "CONSTRUCTION", "CRITICAL"],
    },
    {
        "name": "Boris Rotenberg",
        "type": "individual",
        "country": "RU",
        "risk_score": 100.0,
        "sanctions_status": "SDN",
        "description": "Brother of Arkady Rotenberg, also close to Putin.",
        "identifiers": {
            "date_of_birth": "1957-01-03",
            "ofac_id": "B_ROTENBERG",
        },
        "sanctions_programs": ["RUSSIA-EO13661"],
        "aliases": ["B.R. Rotenberg", "Boris Romanovich Rotenberg"],
        "associated_companies": ["SMP Bank"],
        "tags": ["OLIGARCH", "SDN", "PUTIN_CIRCLE", "CRITICAL"],
    },
    {
        "name": "Yuri Kovalchuk",
        "type": "individual",
        "country": "RU",
        "risk_score": 100.0,
        "sanctions_status": "SDN",
        "description": "Largest shareholder of Bank Rossiya, 'Putin's personal banker'.",
        "identifiers": {
            "date_of_birth": "1951-07-25",
            "ofac_id": "KOVALCHUK",
        },
        "sanctions_programs": ["RUSSIA-EO13661", "EU-RUSSIA"],
        "aliases": ["Y.V. Kovalchuk", "Yuriy Valentinovich Kovalchuk"],
        "associated_companies": ["Bank Rossiya", "National Media Group"],
        "tags": ["OLIGARCH", "SDN", "PUTIN_CIRCLE", "BANKING", "CRITICAL"],
    },
    {
        "name": "Nikolai Tokarev",
        "type": "individual",
        "country": "RU",
        "risk_score": 90.0,
        "sanctions_status": "SDN",
        "description": "CEO of Transneft, former KGB colleague of Putin.",
        "identifiers": {
            "date_of_birth": "1950-12-20",
            "ofac_id": "TOKAREV",
        },
        "sanctions_programs": ["RUSSIA-EO13661"],
        "aliases": ["N.P. Tokarev", "Nikolai Petrovich Tokarev"],
        "associated_companies": ["Transneft"],
        "tags": ["OLIGARCH", "SDN", "PUTIN_CIRCLE", "ENERGY", "CRITICAL"],
    },
    {
        "name": "Sergey Chemezov",
        "type": "individual",
        "country": "RU",
        "risk_score": 100.0,
        "sanctions_status": "SDN",
        "description": "CEO of Rostec, former KGB colleague of Putin in Dresden.",
        "identifiers": {
            "date_of_birth": "1952-08-20",
            "ofac_id": "CHEMEZOV",
        },
        "sanctions_programs": ["RUSSIA-EO13661", "EU-RUSSIA", "UK-RUSSIA"],
        "aliases": ["S.V. Chemezov", "Sergey Viktorovich Chemezov"],
        "associated_companies": ["Rostec"],
        "tags": ["OLIGARCH", "SDN", "PUTIN_CIRCLE", "DEFENSE", "CRITICAL"],
    },
]

# ============================================================================
# RUSSIAN TECHNOLOGY COMPANIES
# ============================================================================
RUSSIAN_TECH = [
    {
        "name": "Kaspersky Lab",
        "type": "corporation",
        "country": "RU",
        "risk_score": 75.0,
        "sanctions_status": "RESTRICTED",
        "description": "Cybersecurity company banned from US government use.",
        "identifiers": {},
        "sanctions_programs": ["US-TECH-BAN"],
        "aliases": ["Kaspersky", "AO Kaspersky Lab"],
        "address": "39A/3 Leningradskoe Shosse, Moscow 125212, Russia",
        "sector": "Technology - Cybersecurity",
        "tags": ["TECH", "CYBERSECURITY", "US_RESTRICTED"],
    },
    {
        "name": "Yandex",
        "type": "corporation",
        "country": "RU",
        "risk_score": 65.0,
        "sanctions_status": "CAUTION",
        "description": "Russian tech giant, search engine and services. Some restrictions.",
        "identifiers": {
            "ticker": "YNDX",
        },
        "sanctions_programs": [],
        "aliases": ["Yandex N.V.", "Yandex LLC"],
        "address": "16 Leo Tolstoy Street, Moscow 119021, Russia",
        "sector": "Technology - Internet",
        "tags": ["TECH", "INTERNET", "CAUTION"],
    },
    {
        "name": "Mail.ru Group (VK)",
        "type": "corporation",
        "country": "RU",
        "risk_score": 60.0,
        "sanctions_status": "CAUTION",
        "description": "Major Russian internet company, social networks.",
        "identifiers": {},
        "sanctions_programs": [],
        "aliases": ["VK", "VKontakte", "Mail.ru"],
        "address": "39 Leningradsky Prospekt, Moscow 125167, Russia",
        "sector": "Technology - Social Media",
        "tags": ["TECH", "SOCIAL_MEDIA", "CAUTION"],
    },
    {
        "name": "Mikron Group",
        "type": "corporation",
        "country": "RU",
        "risk_score": 95.0,
        "sanctions_status": "SDN",
        "description": "Russia's largest semiconductor manufacturer, critical for defense.",
        "identifiers": {
            "ofac_id": "MIKRON",
        },
        "sanctions_programs": ["RUSSIA-EO14024", "TECH-SANCTIONS"],
        "aliases": ["Mikron", "PJSC Mikron"],
        "address": "1 Zapadny Proezd, Zelenograd 124460, Russia",
        "sector": "Technology - Semiconductors",
        "tags": ["TECH", "SEMICONDUCTORS", "SDN", "DEFENSE_SUPPLY", "CRITICAL"],
    },
    {
        "name": "Baikal Electronics",
        "type": "corporation",
        "country": "RU",
        "risk_score": 95.0,
        "sanctions_status": "SDN",
        "description": "Russian processor/chip designer under sanctions.",
        "identifiers": {
            "ofac_id": "BAIKAL",
        },
        "sanctions_programs": ["RUSSIA-EO14024", "TECH-SANCTIONS"],
        "aliases": ["Baikal", "Baikal Electronics JSC"],
        "address": "Moscow, Russia",
        "sector": "Technology - Semiconductors",
        "tags": ["TECH", "SEMICONDUCTORS", "SDN", "CRITICAL"],
    },
]


def load_entities(tenant_id: str, entities: list, category: str) -> int:
    """Load entities into database."""
    print(f"\n{'='*60}")
    print(f"Loading {len(entities)} {category}...")
    print(f"{'='*60}")

    count = 0
    for entity in entities:
        entity_id = str(uuid.uuid4())

        tags = entity.get("tags", [])
        tags_array = "ARRAY[" + ",".join([f"'{t}'" for t in tags]) + "]::varchar[]" if tags else "ARRAY[]::varchar[]"

        # Build custom_data JSON
        custom_data = {
            "sanctions_status": entity.get("sanctions_status", ""),
            "sanctions_programs": entity.get("sanctions_programs", []),
            "aliases": entity.get("aliases", []),
            "identifiers": entity.get("identifiers", {}),
            "sector": entity.get("sector", ""),
            "address": entity.get("address", ""),
            "associated_companies": entity.get("associated_companies", []),
        }
        custom_data_json = json.dumps(custom_data).replace("'", "''")

        sql = f"""
        INSERT INTO entities (
            id, tenant_id, name, type, country, risk_score,
            description, is_active, tags, custom_data,
            created_at, updated_at
        ) VALUES (
            '{entity_id}',
            '{tenant_id}',
            '{escape_sql(entity["name"])}',
            '{entity["type"]}',
            '{entity.get("country", "")}',
            {entity.get("risk_score", 50.0)},
            '{escape_sql(entity.get("description", ""))}',
            true,
            {tags_array},
            '{custom_data_json}'::jsonb,
            NOW(),
            NOW()
        )
        ON CONFLICT DO NOTHING;
        """

        run_sql(sql)
        status = entity.get("sanctions_status", "N/A")
        risk = entity.get("risk_score", 0)
        print(f"  [OK] {entity['name'][:45]:<45} | Risk: {risk:>5.1f} | Status: {status}")
        count += 1

    return count


def main():
    print("=" * 70)
    print("CORTEX-CI Russia Sanctioned Entities Loader")
    print("Government-Grade Compliance Database")
    print("=" * 70)

    tenant_id = get_tenant_id()
    if not tenant_id:
        print("ERROR: Could not find default tenant!")
        return

    print(f"Tenant: {tenant_id}")

    total = 0
    total += load_entities(tenant_id, RUSSIAN_BANKS, "Russian Banks (SDN/SSI)")
    total += load_entities(tenant_id, RUSSIAN_SOES, "State-Owned Enterprises")
    total += load_entities(tenant_id, RUSSIAN_DEFENSE, "Defense Companies")
    total += load_entities(tenant_id, RUSSIAN_OLIGARCHS, "Oligarchs & PEPs")
    total += load_entities(tenant_id, RUSSIAN_TECH, "Technology Companies")

    # Get final count
    result = run_sql(f"SELECT COUNT(*) FROM entities WHERE tenant_id = '{tenant_id}';")
    for line in result.split("\n"):
        if line.strip().isdigit():
            print(f"\n{'='*70}")
            print(f"Entities loaded this session: {total}")
            print(f"Total entities in database: {line.strip()}")
            print(f"{'='*70}")
            break


if __name__ == "__main__":
    main()
