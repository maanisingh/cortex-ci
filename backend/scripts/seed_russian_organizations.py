"""
Seed Russian Organizations
Sample Russian enterprises and universities for CORTEX platform.

Includes:
- Energy sector: Gazprom, Rosneft, Lukoil, Rosatom
- Finance: Sberbank, VTB, Alfa-Bank, Tinkoff
- Technology: Yandex, VK, Kaspersky
- Telecom: Rostelecom, MTS, Megafon
- Universities: MSU, MIPT, HSE, ITMO
"""

import asyncio
import sys
from datetime import date
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_maker
from app.models.compliance.customer import Customer, CustomerType, CustomerStatus, CustomerRiskRating


RUSSIAN_ORGANIZATIONS = [
    # Energy Sector
    {"name": "Gazprom PJSC", "type": CustomerType.CORPORATE, "industry": "Energy - Oil & Gas", "country": "Russia", "city": "Saint Petersburg", "risk_rating": CustomerRiskRating.HIGH, "description": "Largest natural gas company in the world, major Russian state enterprise", "inn": "7736050003", "ogrn": "1027700070518"},
    {"name": "Rosneft Oil Company", "type": CustomerType.CORPORATE, "industry": "Energy - Oil & Gas", "country": "Russia", "city": "Moscow", "risk_rating": CustomerRiskRating.HIGH, "description": "State-controlled petroleum company, one of world's largest publicly traded oil producers", "inn": "7706107510", "ogrn": "1027700043502"},
    {"name": "Lukoil PJSC", "type": CustomerType.CORPORATE, "industry": "Energy - Oil & Gas", "country": "Russia", "city": "Moscow", "risk_rating": CustomerRiskRating.MEDIUM, "description": "Second largest Russian oil company, privately owned", "inn": "7708004767", "ogrn": "1027700035769"},
    {"name": "Rosatom State Corporation", "type": CustomerType.GOVERNMENT, "industry": "Energy - Nuclear", "country": "Russia", "city": "Moscow", "risk_rating": CustomerRiskRating.HIGH, "description": "State corporation for nuclear energy, manages all Russian nuclear assets", "inn": "7706413348", "ogrn": "1077799032926"},
    {"name": "RusHydro PJSC", "type": CustomerType.CORPORATE, "industry": "Energy - Hydroelectric", "country": "Russia", "city": "Krasnoyarsk", "risk_rating": CustomerRiskRating.MEDIUM, "description": "Russia's largest hydroelectricity producer", "inn": "2460066195", "ogrn": "1042401810494"},
    {"name": "Inter RAO UES", "type": CustomerType.CORPORATE, "industry": "Energy - Electricity", "country": "Russia", "city": "Moscow", "risk_rating": CustomerRiskRating.MEDIUM, "description": "Major Russian electric utility company", "inn": "2320121655", "ogrn": "1022302933630"},
    {"name": "Novatek PJSC", "type": CustomerType.CORPORATE, "industry": "Energy - Natural Gas", "country": "Russia", "city": "Tarko-Sale", "risk_rating": CustomerRiskRating.HIGH, "description": "Largest independent natural gas producer in Russia", "inn": "8903011402", "ogrn": "1028900703963"},
    
    # Financial Sector
    {"name": "Sberbank of Russia", "type": CustomerType.CORPORATE, "industry": "Financial Services - Banking", "country": "Russia", "city": "Moscow", "risk_rating": CustomerRiskRating.HIGH, "description": "Largest bank in Russia and Eastern Europe, state-controlled", "inn": "7707083893", "ogrn": "1027700132195"},
    {"name": "VTB Bank", "type": CustomerType.CORPORATE, "industry": "Financial Services - Banking", "country": "Russia", "city": "Saint Petersburg", "risk_rating": CustomerRiskRating.HIGH, "description": "Second largest Russian bank, state-owned", "inn": "7702070139", "ogrn": "1027739609391"},
    {"name": "Alfa-Bank", "type": CustomerType.CORPORATE, "industry": "Financial Services - Banking", "country": "Russia", "city": "Moscow", "risk_rating": CustomerRiskRating.MEDIUM, "description": "Largest Russian private bank", "inn": "7728168971", "ogrn": "1027700067328"},
    {"name": "Tinkoff Bank", "type": CustomerType.CORPORATE, "industry": "Financial Services - Digital Banking", "country": "Russia", "city": "Moscow", "risk_rating": CustomerRiskRating.MEDIUM, "description": "Leading Russian online bank and fintech company", "inn": "7710140679", "ogrn": "1027739642281"},
    {"name": "Gazprombank", "type": CustomerType.CORPORATE, "industry": "Financial Services - Banking", "country": "Russia", "city": "Moscow", "risk_rating": CustomerRiskRating.HIGH, "description": "Third largest Russian bank, subsidiary of Gazprom", "inn": "7744001497", "ogrn": "1027700167110"},
    {"name": "Moscow Exchange", "type": CustomerType.CORPORATE, "industry": "Financial Services - Exchange", "country": "Russia", "city": "Moscow", "risk_rating": CustomerRiskRating.MEDIUM, "description": "Largest exchange in Russia", "inn": "7702077840", "ogrn": "1027739387411"},
    
    # Technology Sector
    {"name": "Yandex N.V.", "type": CustomerType.CORPORATE, "industry": "Technology - Internet", "country": "Russia", "city": "Moscow", "risk_rating": CustomerRiskRating.MEDIUM, "description": "Largest Russian technology company, internet services and search engine", "inn": "7736207543", "ogrn": "1027700229193"},
    {"name": "VK Company Limited", "type": CustomerType.CORPORATE, "industry": "Technology - Social Media", "country": "Russia", "city": "Saint Petersburg", "risk_rating": CustomerRiskRating.MEDIUM, "description": "Major Russian technology conglomerate, social networks", "inn": "7743001840", "ogrn": "1027739850962"},
    {"name": "Kaspersky Lab", "type": CustomerType.CORPORATE, "industry": "Technology - Cybersecurity", "country": "Russia", "city": "Moscow", "risk_rating": CustomerRiskRating.MEDIUM, "description": "Global cybersecurity company", "inn": "7713140469", "ogrn": "1027739574297"},
    {"name": "Positive Technologies", "type": CustomerType.CORPORATE, "industry": "Technology - Cybersecurity", "country": "Russia", "city": "Moscow", "risk_rating": CustomerRiskRating.LOW, "description": "Russian cybersecurity company", "inn": "7717586723", "ogrn": "1067761458682"},
    {"name": "1C Company", "type": CustomerType.CORPORATE, "industry": "Technology - Software", "country": "Russia", "city": "Moscow", "risk_rating": CustomerRiskRating.LOW, "description": "Major Russian software developer, ERP systems", "inn": "7709860454", "ogrn": "1117746411237"},
    {"name": "Softline", "type": CustomerType.CORPORATE, "industry": "Technology - IT Services", "country": "Russia", "city": "Moscow", "risk_rating": CustomerRiskRating.LOW, "description": "IT solutions provider in Russia and CIS", "inn": "7725231965", "ogrn": "1027725000992"},
    
    # Telecommunications
    {"name": "Rostelecom PJSC", "type": CustomerType.CORPORATE, "industry": "Telecommunications", "country": "Russia", "city": "Moscow", "risk_rating": CustomerRiskRating.MEDIUM, "description": "Largest Russian telecommunications company, state-controlled", "inn": "7707049388", "ogrn": "1027700198767"},
    {"name": "MTS PJSC", "type": CustomerType.CORPORATE, "industry": "Telecommunications - Mobile", "country": "Russia", "city": "Moscow", "risk_rating": CustomerRiskRating.MEDIUM, "description": "Largest mobile network operator in Russia", "inn": "7740000076", "ogrn": "1027700149124"},
    {"name": "MegaFon PJSC", "type": CustomerType.CORPORATE, "industry": "Telecommunications - Mobile", "country": "Russia", "city": "Moscow", "risk_rating": CustomerRiskRating.MEDIUM, "description": "Major Russian mobile operator", "inn": "7812014560", "ogrn": "1027809169585"},
    {"name": "VEON (Beeline)", "type": CustomerType.CORPORATE, "industry": "Telecommunications - Mobile", "country": "Russia", "city": "Moscow", "risk_rating": CustomerRiskRating.MEDIUM, "description": "International telecommunications company operating Beeline in Russia", "inn": "7713076301", "ogrn": "1027700060328"},
    
    # Transportation
    {"name": "Aeroflot PJSC", "type": CustomerType.CORPORATE, "industry": "Transportation - Aviation", "country": "Russia", "city": "Moscow", "risk_rating": CustomerRiskRating.HIGH, "description": "Flag carrier and largest airline of Russia", "inn": "7712040126", "ogrn": "1027700092661"},
    {"name": "Russian Railways (RZD)", "type": CustomerType.GOVERNMENT, "industry": "Transportation - Rail", "country": "Russia", "city": "Moscow", "risk_rating": CustomerRiskRating.HIGH, "description": "State-owned railway monopoly", "inn": "7708503727", "ogrn": "1037739877295"},
    {"name": "Sheremetyevo Airport", "type": CustomerType.CORPORATE, "industry": "Transportation - Aviation", "country": "Russia", "city": "Moscow", "risk_rating": CustomerRiskRating.MEDIUM, "description": "Largest airport in Russia", "inn": "7712033300", "ogrn": "1027700314812"},
    
    # Mining and Metals
    {"name": "Norilsk Nickel (Nornickel)", "type": CustomerType.CORPORATE, "industry": "Mining - Metals", "country": "Russia", "city": "Norilsk", "risk_rating": CustomerRiskRating.HIGH, "description": "World's largest producer of nickel and palladium", "inn": "8401005730", "ogrn": "1028400294600"},
    {"name": "Rusal", "type": CustomerType.CORPORATE, "industry": "Mining - Aluminum", "country": "Russia", "city": "Moscow", "risk_rating": CustomerRiskRating.HIGH, "description": "One of world's largest aluminum producers", "inn": "7709561874", "ogrn": "1047796540167"},
    {"name": "Severstal", "type": CustomerType.CORPORATE, "industry": "Mining - Steel", "country": "Russia", "city": "Cherepovets", "risk_rating": CustomerRiskRating.MEDIUM, "description": "Major Russian steel and mining company", "inn": "3528000597", "ogrn": "1023501236901"},
    {"name": "NLMK Group", "type": CustomerType.CORPORATE, "industry": "Mining - Steel", "country": "Russia", "city": "Lipetsk", "risk_rating": CustomerRiskRating.MEDIUM, "description": "Leading international steel company", "inn": "4823006703", "ogrn": "1024800823123"},
    
    # Retail
    {"name": "X5 Retail Group", "type": CustomerType.CORPORATE, "industry": "Retail - Food", "country": "Russia", "city": "Moscow", "risk_rating": CustomerRiskRating.LOW, "description": "Leading Russian food retailer", "inn": "7728632689", "ogrn": "1057747318556"},
    {"name": "Magnit PJSC", "type": CustomerType.CORPORATE, "industry": "Retail - Food", "country": "Russia", "city": "Krasnodar", "risk_rating": CustomerRiskRating.LOW, "description": "Major Russian retailer", "inn": "2309085638", "ogrn": "1032304945904"},
    {"name": "Wildberries", "type": CustomerType.CORPORATE, "industry": "Retail - E-commerce", "country": "Russia", "city": "Podolsk", "risk_rating": CustomerRiskRating.LOW, "description": "Largest Russian e-commerce company", "inn": "7721546864", "ogrn": "1067746062449"},
    {"name": "Ozon Holdings", "type": CustomerType.CORPORATE, "industry": "Retail - E-commerce", "country": "Russia", "city": "Moscow", "risk_rating": CustomerRiskRating.LOW, "description": "Major Russian e-commerce platform", "inn": "7704217370", "ogrn": "1027700359306"},
    
    # Universities
    {"name": "Lomonosov Moscow State University (MSU)", "type": CustomerType.GOVERNMENT, "industry": "Education - University", "country": "Russia", "city": "Moscow", "risk_rating": CustomerRiskRating.LOW, "description": "Russia's oldest and largest university", "inn": "7729082090", "ogrn": "1027739439507"},
    {"name": "Moscow Institute of Physics and Technology (MIPT)", "type": CustomerType.GOVERNMENT, "industry": "Education - University", "country": "Russia", "city": "Dolgoprudny", "risk_rating": CustomerRiskRating.LOW, "description": "Leading Russian university in physics and technology", "inn": "5008006211", "ogrn": "1025004118197"},
    {"name": "Higher School of Economics (HSE)", "type": CustomerType.GOVERNMENT, "industry": "Education - University", "country": "Russia", "city": "Moscow", "risk_rating": CustomerRiskRating.LOW, "description": "Leading research university in economics and social sciences", "inn": "7714030726", "ogrn": "1027700366101"},
    {"name": "ITMO University", "type": CustomerType.GOVERNMENT, "industry": "Education - University", "country": "Russia", "city": "Saint Petersburg", "risk_rating": CustomerRiskRating.LOW, "description": "National research university focused on IT and photonics", "inn": "7813045789", "ogrn": "1037843027391"},
    {"name": "Saint Petersburg State University (SPbU)", "type": CustomerType.GOVERNMENT, "industry": "Education - University", "country": "Russia", "city": "Saint Petersburg", "risk_rating": CustomerRiskRating.LOW, "description": "Second oldest university in Russia", "inn": "7801002274", "ogrn": "1027809224155"},
    {"name": "Bauman Moscow State Technical University", "type": CustomerType.GOVERNMENT, "industry": "Education - University", "country": "Russia", "city": "Moscow", "risk_rating": CustomerRiskRating.LOW, "description": "Leading Russian technical university", "inn": "7701002520", "ogrn": "1027739059333"},
    {"name": "MISIS (National University of Science and Technology)", "type": CustomerType.GOVERNMENT, "industry": "Education - University", "country": "Russia", "city": "Moscow", "risk_rating": CustomerRiskRating.LOW, "description": "Leading Russian university in materials science", "inn": "7706026990", "ogrn": "1027739439507"},
    {"name": "Skolkovo Institute of Science and Technology", "type": CustomerType.NON_PROFIT, "industry": "Education - University", "country": "Russia", "city": "Moscow", "risk_rating": CustomerRiskRating.LOW, "description": "Private graduate research university", "inn": "5003105883", "ogrn": "1135003000446"},
    {"name": "Tomsk State University", "type": CustomerType.GOVERNMENT, "industry": "Education - University", "country": "Russia", "city": "Tomsk", "risk_rating": CustomerRiskRating.LOW, "description": "First university established in Asian Russia", "inn": "7018004050", "ogrn": "1027000880168"},
    {"name": "Novosibirsk State University", "type": CustomerType.GOVERNMENT, "industry": "Education - University", "country": "Russia", "city": "Novosibirsk", "risk_rating": CustomerRiskRating.LOW, "description": "Major research university in Siberia", "inn": "5408103922", "ogrn": "1025403646844"},
    
    # Government Entities
    {"name": "Central Bank of Russia", "type": CustomerType.GOVERNMENT, "industry": "Government - Central Bank", "country": "Russia", "city": "Moscow", "risk_rating": CustomerRiskRating.HIGH, "description": "Central bank of the Russian Federation", "inn": "7702235133", "ogrn": "1037700013020"},
    {"name": "FSTEC Russia", "type": CustomerType.GOVERNMENT, "industry": "Government - Security", "country": "Russia", "city": "Moscow", "risk_rating": CustomerRiskRating.HIGH, "description": "Federal Service for Technical and Export Control", "inn": "7704251617", "ogrn": "1047704065353"},
    {"name": "Roskomnadzor", "type": CustomerType.GOVERNMENT, "industry": "Government - Regulator", "country": "Russia", "city": "Moscow", "risk_rating": CustomerRiskRating.HIGH, "description": "Federal Service for Supervision of Communications", "inn": "7705846236", "ogrn": "1087746736296"},
]


async def seed_russian_organizations(session: AsyncSession, tenant_id: str) -> dict:
    """Seed Russian organizations as customers."""
    results = {"organizations_created": 0, "errors": []}

    for org_data in RUSSIAN_ORGANIZATIONS:
        try:
            result = await session.execute(
                select(Customer).where(
                    Customer.name == org_data["name"],
                    Customer.tenant_id == tenant_id
                )
            )
            existing = result.scalar_one_or_none()
            if existing:
                print(f"Organization {org_data['name']} already exists, skipping...")
                continue

            customer = Customer(
                id=uuid4(),
                tenant_id=tenant_id,
                name=org_data["name"],
                customer_type=org_data["type"],
                status=CustomerStatus.ACTIVE,
                risk_rating=org_data["risk_rating"],
                industry=org_data.get("industry"),
                country=org_data.get("country"),
                city=org_data.get("city"),
                tax_id=org_data.get("inn"),
                registration_number=org_data.get("ogrn"),
                notes=org_data.get("description"),
                onboarding_date=date.today(),
            )
            session.add(customer)
            results["organizations_created"] += 1
            print(f"Created organization: {org_data['name']}")

        except Exception as e:
            results["errors"].append(f"Error creating {org_data['name']}: {str(e)}")
            print(f"Error: {e}")

    await session.commit()
    return results


async def main():
    """Main entry point."""
    tenant_id = "default"
    async with async_session_maker() as session:
        print("=" * 60)
        print("Seeding Russian Organizations")
        print("=" * 60)
        results = await seed_russian_organizations(session, tenant_id)
        print("\n" + "=" * 60)
        print("Seeding Complete!")
        print(f"Organizations created: {results['organizations_created']}")
        if results["errors"]:
            print(f"Errors: {len(results['errors'])}")
            for error in results["errors"]:
                print(f"  - {error}")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
